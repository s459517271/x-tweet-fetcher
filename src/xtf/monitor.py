"""Incremental mentions monitor (--monitor mode). Cron-friendly.

First run establishes a baseline; later runs report only new URLs.
Cache lives in ``XTF_CACHE_DIR`` (default ~/.x-tweet-fetcher).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from . import config
from .exceptions import XtfError
from .i18n import t

_CACHE_MAX = 500


def _get_cache_path(username: str) -> Path:
    clean = username.lstrip("@").lower()
    return config.cache_dir() / f"mentions-cache-{clean}.json"


def _load_cache(username: str) -> dict:
    path = _get_cache_path(username)
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):  # v1 legacy format (bare list)
                return {"seen": data, "is_baseline": False}
            return data
        except Exception:
            pass
    return {"seen": [], "is_baseline": True}


def _save_cache(username: str, cache: dict) -> None:
    config.cache_dir().mkdir(parents=True, exist_ok=True)
    if len(cache["seen"]) > _CACHE_MAX:
        cache["seen"] = cache["seen"][-_CACHE_MAX:]
    with open(_get_cache_path(username), "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def _search_mentions_nitter(nitter_backend, username: str, limit: int) -> list[dict]:
    clean = username.lstrip("@")
    tweets = nitter_backend.search(f"@{clean}", limit=limit)
    results = []
    for tw in tweets:
        handle = tw.author.lstrip("@")
        results.append({
            "url": f"https://x.com/{handle}/status/{tw.tweet_id}" if tw.tweet_id else "",
            "title": f"@{handle}: {tw.text[:80]}",
            "snippet": tw.text,
            "username": handle,
            "tweet_id": tw.tweet_id,
        })
    return [r for r in results if r["url"]]


def monitor_mentions(router, username: str, limit: int = 10,
                     use_nitter: bool = False) -> dict[str, Any]:
    """Run one monitor cycle. Returns v1-compatible result dict."""
    result: dict[str, Any] = {
        "username": username.lstrip("@"),
        "new_mentions": [],
        "is_baseline": False,
        "known_count": 0,
    }

    cache = _load_cache(username)
    seen_set = set(cache["seen"])
    result["known_count"] = len(seen_set)

    try:
        if use_nitter:
            all_results = _search_mentions_nitter(router.nitter, username, limit)
        else:
            if not router.browser.available():
                result["error"] = t("monitor_camofox_error", port=router.browser.port)
                return result
            all_results = router.browser.search_mentions(username, limit=limit)
    except XtfError as e:
        result["error"] = str(e)
        return result

    if cache["is_baseline"]:
        new_urls = [r["url"] for r in all_results]
        cache["seen"] = list(seen_set | set(new_urls))
        cache["is_baseline"] = False
        _save_cache(username, cache)
        result["is_baseline"] = True
        result["known_count"] = len(cache["seen"])
        print(t("monitor_baseline", count=len(cache["seen"])), file=sys.stderr)
    else:
        new_mentions = [r for r in all_results if r["url"] not in seen_set]
        for r in new_mentions:
            cache["seen"].append(r["url"])
        _save_cache(username, cache)
        result["new_mentions"] = new_mentions
        result["known_count"] = len(cache["seen"])
        if new_mentions:
            print(t("monitor_new_found", count=len(new_mentions)), file=sys.stderr)
        else:
            print(t("monitor_no_new", known=len(seen_set)), file=sys.stderr)

    return result
