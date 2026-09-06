"""FxTwitter backend — single tweets and user profiles, zero dependencies.

Output of ``fetch_tweet`` reproduces the v1 ``tweet`` dict byte-for-byte
(including the article full-text reconstruction from Draft.js blocks).
"""
from __future__ import annotations

import re
import sys
from typing import Any

from .. import http
from ..exceptions import NotFound, UpstreamDown, XtfError
from ..models import Profile
from ..parsers.fxtwitter_json import extract_media
from .base import Backend

API = "https://api.fxtwitter.com"



def _normalize_entity_map(entity_map: Any) -> dict[str, Any]:
    """Normalize Draft.js entityMap (dict or list-of-{key,value}) to a dict."""
    if isinstance(entity_map, dict):
        return {str(k): v for k, v in entity_map.items()}
    out: dict[str, Any] = {}
    if isinstance(entity_map, list):
        for e in entity_map:
            if not isinstance(e, dict):
                continue
            k = e.get("key")
            if k is None:
                continue
            out[str(k)] = e.get("value")
    return out


def _entity_markdown_text(entity: Any) -> str:
    """Extract readable text from a MARKDOWN entity (unwrap fences when present)."""
    if not isinstance(entity, dict) or entity.get("type") != "MARKDOWN":
        return ""
    md = (entity.get("data") or {}).get("markdown") or ""
    if not isinstance(md, str):
        return ""
    m = re.search(r"```(?:[a-zA-Z0-9_-]*)?\n(.*?)```", md, re.DOTALL)
    if m:
        return m.group(1).strip("\n")
    return md.strip()


def _reconstruct_article(article: dict[str, Any]) -> dict[str, Any]:
    """Rebuild article full_text (with inline images) from Draft.js blocks."""
    article_data: dict[str, Any] = {
        "title": article.get("title", ""),
        "preview_text": article.get("preview_text", ""),
        "created_at": article.get("created_at", ""),
    }
    content = article.get("content", {})
    blocks = content.get("blocks", [])
    cover = article.get("cover_media", {})
    media_entities = article.get("media_entities", [])

    if blocks:
        media_id_to_url: dict[str, str] = {}
        if cover:
            cover_url = cover.get("media_info", {}).get("original_img_url")
            cover_id = cover.get("media_id")
            if cover_url and cover_id:
                media_id_to_url[str(cover_id)] = cover_url
        for me in media_entities:
            mid = str(me.get("media_id", ""))
            murl = me.get("media_info", {}).get("original_img_url", "")
            if mid and murl:
                media_id_to_url[mid] = murl

        entities = _normalize_entity_map(content.get("entityMap") or {})
        key_to_url: dict[str, str] = {}
        key_to_markdown: dict[str, str] = {}
        for e_key, e_val in entities.items():
            if not isinstance(e_val, dict):
                continue
            etype = e_val.get("type")
            if etype == "MEDIA":
                for mi in e_val.get("data", {}).get("mediaItems", []):
                    if isinstance(mi, dict):
                        mid = str(mi.get("mediaId", ""))
                        if mid in media_id_to_url:
                            key_to_url[str(e_key)] = media_id_to_url[mid]
            elif etype == "MARKDOWN":
                md_text = _entity_markdown_text(e_val)
                if md_text:
                    key_to_markdown[str(e_key)] = md_text

        atomic_media: dict[int, str] = {}
        atomic_markdown: dict[int, str] = {}
        for bi, b in enumerate(blocks):
            if not isinstance(b, dict):
                continue
            if b.get("type") != "atomic":
                continue
            for r in b.get("entityRanges", []):
                if not isinstance(r, dict):
                    continue
                ek = r.get("key")
                if ek is None:
                    continue
                sk = str(ek)
                if sk in key_to_url:
                    atomic_media[bi] = key_to_url[sk]
                elif sk in key_to_markdown:
                    atomic_markdown[bi] = key_to_markdown[sk]

        text_parts: list[str] = []
        for bi, b in enumerate(blocks):
            if not isinstance(b, dict):
                continue
            btype = b.get("type")
            btext = b.get("text", "")
            if btype == "atomic":
                if bi in atomic_media:
                    img_url = atomic_media[bi]
                    if (
                        isinstance(img_url, str)
                        and img_url.startswith(("https://", "http://"))
                        and ")" not in img_url
                        and "\n" not in img_url
                        and "\r" not in img_url
                    ):
                        text_parts.append(f"![]({img_url})")
                elif bi in atomic_markdown:
                    text_parts.append(atomic_markdown[bi])
                elif btext:
                    text_parts.append(btext)
            elif btext:
                text_parts.append(btext)
        full_text = "\n\n".join(text_parts)
        article_data["full_text"] = full_text
        article_data["word_count"] = len(full_text.split())
        article_data["char_count"] = len(full_text)

    article_images = []
    if cover:
        cover_url = cover.get("media_info", {}).get("original_img_url")
        if cover_url:
            article_images.append({"type": "cover", "url": cover_url})
    for entity in media_entities:
        img_url = entity.get("media_info", {}).get("original_img_url")
        if img_url:
            article_images.append({"type": "image", "url": img_url})
    if article_images:
        article_data["images"] = article_images
        article_data["image_count"] = len(article_images)

    return article_data


def normalize_tweet_json(tweet: dict[str, Any]) -> dict[str, Any]:
    """FxTwitter tweet object -> v1-compatible tweet dict. Pure."""
    tweet_data: dict[str, Any] = {
        "text": tweet.get("text", ""),
        "author": tweet.get("author", {}).get("name", ""),
        "screen_name": tweet.get("author", {}).get("screen_name", ""),
        "likes": tweet.get("likes", 0),
        "retweets": tweet.get("retweets", 0),
        "bookmarks": tweet.get("bookmarks", 0),
        "views": tweet.get("views", 0),
        "replies_count": tweet.get("replies", 0),
        "created_at": tweet.get("created_at", ""),
        "is_note_tweet": tweet.get("is_note_tweet", False),
        "lang": tweet.get("lang", ""),
    }

    media = extract_media(tweet)
    if media:
        tweet_data["media"] = media

    if tweet.get("quote"):
        qt = tweet["quote"]
        tweet_data["quote"] = {
            "text": qt.get("text", ""),
            "author": qt.get("author", {}).get("name", ""),
            "screen_name": qt.get("author", {}).get("screen_name", ""),
            "likes": qt.get("likes", 0),
            "retweets": qt.get("retweets", 0),
            "views": qt.get("views", 0),
        }
        quote_media = extract_media(qt)
        if quote_media:
            tweet_data["quote"]["media"] = quote_media

    article = tweet.get("article")
    if article:
        tweet_data["article"] = _reconstruct_article(article)
        tweet_data["is_article"] = True
    else:
        tweet_data["is_article"] = False

    return tweet_data


class FxTwitterBackend(Backend):
    name = "fxtwitter"

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def available(self) -> bool:
        return True  # public API; failures surface per-call

    def fetch_tweet(self, username: str, tweet_id: str) -> dict[str, Any]:
        data = http.get_json(
            f"{API}/{username}/status/{tweet_id}",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=self.timeout,
        )
        code = data.get("code")
        if code == 404:
            raise NotFound(f"tweet {username}/{tweet_id} not found")
        if code != 200:
            raise UpstreamDown(
                f"FxTwitter returned code {code}: {data.get('message', 'Unknown')}"
            )
        return normalize_tweet_json(data["tweet"])

    def fetch_user_info(self, username: str) -> Profile:
        data = http.get_json(f"{API}/{username}", timeout=10)
        u = data.get("user", {})
        if not u:
            raise NotFound(f"user @{username} not found")
        return Profile(
            username=u.get("screen_name", username),
            display_name=u.get("name", ""),
            bio=u.get("description", ""),
            tweets_count=u.get("tweets", 0),
            followers=u.get("followers", 0),
            following=u.get("following", 0),
            joined=u.get("joined", ""),
        )

    def fetch_user_info_dict(self, username: str) -> dict[str, Any]:
        """v1-compatible extended profile dict (includes avatar/banner/etc)."""
        data = http.get_json(f"{API}/{username}", timeout=10)
        u = data.get("user", {})
        if not u:
            raise NotFound(f"user @{username} not found")
        return {
            "username": u.get("screen_name", username),
            "display_name": u.get("name", ""),
            "bio": u.get("description", ""),
            "tweets_count": u.get("tweets", 0),
            "followers": u.get("followers", 0),
            "following": u.get("following", 0),
            "joined": u.get("joined", ""),
            "avatar": u.get("avatar_url", ""),
            "banner": u.get("banner_url", ""),
            "likes": u.get("likes", 0),
            "website": u.get("website", ""),
        }


def supplement_views(tweets: list[dict], max_supplement: int = 50) -> list[dict]:
    """Fill missing view counts via FxTwitter. Best-effort, never raises."""
    for tw in tweets[:max_supplement]:
        if tw.get("views", 0) != 0:
            continue
        author = tw.get("author", "")
        if not author or not author.startswith("@"):
            continue
        username = author.lstrip("@")
        tweet_id = tw.get("tweet_id") or tw.get("id")
        if not tweet_id:
            continue
        try:
            data = http.get_json(
                f"{API}/{username}/status/{tweet_id}", timeout=5, retries=0
            )
            views = data.get("tweet", {}).get("views", 0)
            if views:
                tw["views"] = views
                print(f"[views] {username}/{str(tweet_id)[:8]}... -> {views}", file=sys.stderr)
        except XtfError:
            pass
    return tweets
