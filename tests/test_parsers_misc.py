"""Tests for URL/ID parsing, FxTwitter JSON normalization, Nitter HTML parsing."""
import json
from pathlib import Path

import pytest

from xtf.backends.fxtwitter import normalize_tweet_json
from xtf.parsers.fxtwitter_json import extract_media
from xtf.parsers.nitter_html import (
    _extract_next_cursor,
    _extract_tweets_from_events,
    _parse_html,
    parse_tweet_detail_html,
)
from xtf.parsers.urls import extract_list_id, parse_article_id, parse_tweet_url

FIXTURES = Path(__file__).parent / "fixtures"


# ── URL / ID parsing ──────────────────────────────────────────────────────
@pytest.mark.parametrize("url,expected", [
    ("https://x.com/alice/status/12345", ("alice", "12345")),
    ("https://twitter.com/bob_1/status/999?s=20", ("bob_1", "999")),
    ("x.com/carol/status/42#photo", ("carol", "42")),
])
def test_parse_tweet_url(url, expected):
    assert parse_tweet_url(url) == expected


@pytest.mark.parametrize("bad", [
    "https://x.com/alice", "https://example.com/a/status/1", "not a url",
])
def test_parse_tweet_url_rejects(bad):
    with pytest.raises(ValueError):
        parse_tweet_url(bad)


@pytest.mark.parametrize("s,expected", [
    ("123456789", "123456789"),
    ("https://x.com/i/lists/123456789", "123456789"),
    ("twitter.com/i/lists/42?foo=1", "42"),
    ("garbage", None),
])
def test_extract_list_id(s, expected):
    assert extract_list_id(s) == expected


@pytest.mark.parametrize("s,expected", [
    ("2011779830157557760", "2011779830157557760"),
    ("https://x.com/i/article/2011779830157557760", "2011779830157557760"),
    ("123", None),  # too short
    ("no id here", None),
])
def test_parse_article_id(s, expected):
    assert parse_article_id(s) == expected


# ── FxTwitter JSON normalization ──────────────────────────────────────────
@pytest.fixture(scope="module")
def tweet():
    data = json.loads((FIXTURES / "fxtwitter_tweet.json").read_text())
    return normalize_tweet_json(data["tweet"])


class TestFxTwitterNormalize:

    def test_core_fields(self, tweet):
        assert tweet["text"].startswith("Announcing v2")
        assert tweet["screen_name"] == "alice"
        assert tweet["likes"] == 120
        assert tweet["views"] == 9000
        assert tweet["replies_count"] == 33
        assert tweet["is_article"] is False

    def test_media(self, tweet):
        media = tweet["media"]
        assert media["images"][0]["url"] == "https://pbs.twimg.com/media/AAA111.jpg"
        assert media["images"][0]["width"] == 1200
        assert media["videos"][0]["variants"][0]["bitrate"] == 832000

    def test_quote(self, tweet):
        q = tweet["quote"]
        assert q["screen_name"] == "carol"
        assert q["likes"] == 10

    def test_extract_media_empty(self):
        assert extract_media({"media": {}}) is None


@pytest.fixture(scope="module")
def article_tweet():
    data = json.loads((FIXTURES / "fxtwitter_article.json").read_text())
    return normalize_tweet_json(data["tweet"])


class TestFxTwitterArticle:

    def test_article_flag(self, article_tweet):
        assert article_tweet["is_article"] is True

    def test_full_text_with_inline_image(self, article_tweet):
        full = article_tweet["article"]["full_text"]
        assert "First paragraph of the article." in full
        assert "![](https://pbs.twimg.com/media/INLINE.jpg)" in full
        assert "Second paragraph after the image." in full
        # Order: para, image, para
        assert full.index("First") < full.index("INLINE") < full.index("Second")

    def test_images_collected(self, article_tweet):
        images = article_tweet["article"]["images"]
        types = {img["type"] for img in images}
        assert types == {"cover", "image"}
        assert article_tweet["article"]["image_count"] == 2


# ── Nitter raw-HTML parsing ───────────────────────────────────────────────
@pytest.fixture(scope="module")
def tweets():
    html = (FIXTURES / "nitter_timeline.html").read_text()
    return _extract_tweets_from_events(_parse_html(html).events)


class TestNitterHtml:
    # Fixtures are real Nitter captures (see tests/fixtures/README-style note):
    #   nitter_timeline.html — GET /jack (jack's profile timeline, 21 items)
    #   nitter_status.html   — GET /jack/status/20 (first-ever tweet + replies)
    # If Nitter's markup changes, re-capture and update these expected values.

    def test_tweet_fields(self, tweets):
        assert len(tweets) == 21
        tw = tweets[0]
        assert tw["username"] == "jack"
        assert tw["display_name"] == "jack"
        assert tw["text"].startswith("We reject: kings, presidents, and voting.")
        assert tw["tweet_id"] == "1833951636005552366"
        assert (tw["replies"], tw["retweets"], tw["likes"], tw["views"]) == (3819, 4276, 26380, 8195028)

    def test_media_url_decoded(self, tweets):
        # jack's own top tweet has no media; the first media-bearing item in
        # the timeline is a retweet whose proxied path decodes to a twimg URL.
        with_media = [t for t in tweets if t["media_urls"]]
        assert with_media, "expected at least one tweet with media in the fixture"
        first = with_media[0]
        assert first["has_media"] is True
        assert first["media_urls"] == ["https://pbs.twimg.com/media/CNq2BQMWIAESvuO.jpg"]
        assert all(u.startswith("https://pbs.twimg.com/") for t in with_media for u in t["media_urls"])

    def test_cursor(self):
        html = (FIXTURES / "nitter_timeline.html").read_text()
        assert _extract_next_cursor(html) == "DAAHCgABHMetd58__-oLAAIAAAATMjA2Nzk2MDg5MDMzOTUzNzAxNggAAwAAAAIAAA"

    def test_tweet_detail_split(self):
        html = (FIXTURES / "nitter_status.html").read_text()
        detail = parse_tweet_detail_html(html, "jack", "20")
        # og:description ("just setting up my twttr") is >= the parsed body, so it wins.
        assert detail["text"] == "just setting up my twttr"
        assert detail["username"] == "jack"
        assert detail["tweet_id"] == "20"
        replies = detail["replies_list"]
        assert len(replies) == 35
        assert replies[0]["username"] == "kwanelencube07"
        assert replies[0]["likes"] == 143
