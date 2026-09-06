"""Fixture tests for aria-snapshot parsers.

These lock the current parsing behavior. If Nitter or X change their
page structure, capture a fresh snapshot into tests/fixtures/ and these
tests will show exactly which parser and field broke.
"""
from pathlib import Path

import pytest

from xtf.parsers.snapshot import (
    _parse_stats_from_text,
    extract_next_cursor,
    parse_article_snapshot,
    parse_replies_snapshot,
    parse_timeline_snapshot,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _read(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


# ── stats line parsing ────────────────────────────────────────────────────
@pytest.mark.parametrize("raw,expected", [
    ("  7  9  83 ", ("", 7, 9, 83, 0)),
    ("some tweet text here  1   22  4,418", ("some tweet text here", 1, 22, 4418, 0)),
    ("shorter text  5  10", ("shorter text", 5, 0, 10, 0)),
    ("no stats in this line at all", ("no stats in this line at all", 0, 0, 0, 0)),
])
def test_parse_stats_from_text(raw, expected):
    assert _parse_stats_from_text(raw) == expected


def test_parse_stats_icon_format():
    raw = "prefix \ue803 3 \ue80c 1 \ue801 42 \ue800"
    text, replies, retweets, likes, _views = _parse_stats_from_text(raw)
    assert text == "prefix"
    assert (replies, retweets, likes) == (3, 1, 42)


# ── timeline snapshot ─────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def tweets():
    return parse_timeline_snapshot(_read("snapshot_timeline.txt"), limit=20)


class TestTimelineSnapshot:

    def test_card_count(self, tweets):
        assert len(tweets) == 3

    def test_plain_tweet(self, tweets):
        tw = tweets[0]
        assert tw["author"] == "@alice"
        assert tw["author_name"] == "Alice Anderson"
        assert tw["tweet_id"] == "1900000000000000001"
        assert tw["text"].startswith("Shipping the new parser")
        assert (tw["replies"], tw["retweets"], tw["likes"]) == (7, 9, 83)
        assert tw["time_ago"] == "3h"
        assert "retweeted_by" not in tw
        assert "quoted_tweet" not in tw

    def test_retweet_attribution(self, tweets):
        tw = tweets[1]
        assert tw["author"] == "@carol"
        assert tw["retweeted_by"] == "Bob Builder"
        assert (tw["replies"], tw["retweets"], tw["likes"]) == (12, 30, 245)

    def test_media_and_quote(self, tweets):
        tw = tweets[2]
        assert tw["author"] == "@dave"
        assert tw["media"] == ["https://pbs.twimg.com/media/Gabc123XYZ.jpg"]
        q = tw["quoted_tweet"]
        assert q["author"] == "@erin"
        assert q["text"].startswith("This is the quoted tweet body")
        assert (q["replies"], q["retweets"], q["likes"]) == (4, 1, 55)

    def test_limit_respected(self):
        tweets = parse_timeline_snapshot(_read("snapshot_timeline.txt"), limit=1)
        assert len(tweets) == 1

    def test_empty_snapshot(self):
        assert parse_timeline_snapshot("", limit=20) == []


def test_extract_next_cursor():
    cursor = extract_next_cursor(_read("snapshot_timeline.txt"))
    assert cursor == "DAABCgABGc+Qqpp__9sLAAIAAAAT"


def test_extract_next_cursor_absent():
    assert extract_next_cursor("- text: nothing here") is None


# ── replies snapshot ──────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def replies():
    return parse_replies_snapshot(_read("snapshot_replies.txt"),
                                  original_author="alice")


class TestRepliesSnapshot:

    def test_reply_count(self, replies):
        assert len(replies) == 2

    def test_first_reply(self, replies):
        r = replies[0]
        assert r["author"] == "@carol"
        assert r["author_name"] == "Carol Chen"
        assert r["text"].startswith("Great point")
        assert r["likes"] == 60
        assert r["replies"] == 1
        assert r["media"] == ["https://pbs.twimg.com/media/DEF456img.jpg"]
        assert r["tweet_id"] == "1900000000000000101"

    def test_v1_nested_scan_quirk_locked(self, replies):
        # Known v1 behavior: the forward scan treats the NEXT reply block's
        # text as a thread_reply of the current one. Locked intentionally —
        # changing this changes output for all --replies users.
        tr = replies[0]["thread_replies"]
        assert len(tr) == 1 and tr[0]["text"].startswith("Here is the repo")

    def test_second_reply_with_link(self, replies):
        r = replies[1]
        assert r["author"] == "@frank"
        assert r["time_ago"] == "Feb 15"
        assert "https://github.com/example/repo" in r["links"]
        assert r["tweet_id"] == "1900000000000000102"

    def test_original_author_excluded(self, replies):
        assert all(r["author"] != "@alice" for r in replies)


# ── article snapshot ──────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def article():
    return parse_article_snapshot(_read("snapshot_article.txt"))


class TestArticleSnapshot:

    def test_metadata(self, article):
        assert article["title"] == "How We Built a Zero-Dependency Tweet Fetcher"
        assert article["author_handle"] == "@writerjane"
        assert article["author"] == "Jane Writer"

    def test_paragraphs_exclude_boilerplate(self, article):
        assert len(article["paragraphs"]) == 2
        joined = " ".join(article["paragraphs"]).lower()
        assert "log in" not in joined and "sign up" not in joined

    def test_partial_detection(self, article):
        assert article["is_partial"] is False
        short = parse_article_snapshot('- heading "T"\n- text: tiny')
        assert short["is_partial"] is True
