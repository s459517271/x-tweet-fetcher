"""Article reconstruction must expand Draft.js MARKDOWN entities (prompts)."""
from __future__ import annotations

from xtf.backends.fxtwitter import _reconstruct_article


def test_reconstruct_article_expands_markdown_entity_map_list():
    article = {
        "title": "font prompts fixture",
        "preview_text": "preview",
        "created_at": "2026-09-04T08:31:21.000Z",
        "content": {
            "blocks": [
                {
                    "key": "a",
                    "text": "21. Graphik",
                    "type": "unstyled",
                    "entityRanges": [],
                    "inlineStyleRanges": [],
                    "data": {},
                },
                {
                    "key": "b",
                    "text": "AI 生图提示词：",
                    "type": "unstyled",
                    "entityRanges": [],
                    "inlineStyleRanges": [],
                    "data": {},
                },
                {
                    "key": "c",
                    "text": "",
                    "type": "atomic",
                    "entityRanges": [{"offset": 0, "length": 1, "key": 2}],
                    "inlineStyleRanges": [],
                    "data": {},
                },
                {
                    "key": "d",
                    "text": "22. Circular",
                    "type": "unstyled",
                    "entityRanges": [],
                    "inlineStyleRanges": [],
                    "data": {},
                },
                {
                    "key": "e",
                    "text": "",
                    "type": "atomic",
                    "entityRanges": [{"offset": 0, "length": 1, "key": 4}],
                    "inlineStyleRanges": [],
                    "data": {},
                },
            ],
            # FxTwitter often returns entityMap as a list of {key,value}
            "entityMap": [
                {
                    "key": "2",
                    "value": {
                        "type": "MARKDOWN",
                        "mutability": "Mutable",
                        "data": {
                            "markdown": "```text\nGraphik-inspired minimalist grotesque sans serif, neutral contemporary forms\n```"
                        },
                    },
                },
                {
                    "key": "4",
                    "value": {
                        "type": "MARKDOWN",
                        "mutability": "Mutable",
                        "data": {
                            "markdown": "```text\nCircular-inspired geometric sans serif, friendly circular shapes\n```"
                        },
                    },
                },
            ],
        },
        "media_entities": [],
        "cover_media": {},
    }

    out = _reconstruct_article(article)
    text = out["full_text"]
    assert "AI 生图提示词：" in text
    assert "Graphik-inspired minimalist grotesque sans serif, neutral contemporary forms" in text
    assert "Circular-inspired geometric sans serif, friendly circular shapes" in text
    # prompts must not be dropped (the bug reported by qtwaiter)
    assert text.index("AI 生图提示词：") < text.index("Graphik-inspired")


def test_reconstruct_article_expands_markdown_entity_map_dict():
    article = {
        "title": "t",
        "preview_text": "p",
        "created_at": "",
        "content": {
            "blocks": [
                {
                    "key": "c",
                    "text": "",
                    "type": "atomic",
                    "entityRanges": [{"offset": 0, "length": 1, "key": "9"}],
                    "inlineStyleRanges": [],
                    "data": {},
                }
            ],
            "entityMap": {
                "9": {
                    "type": "MARKDOWN",
                    "mutability": "Mutable",
                    "data": {"markdown": "```text\nplain prompt body\n```"},
                }
            },
        },
        "media_entities": [],
        "cover_media": {},
    }
    assert _reconstruct_article(article)["full_text"] == "plain prompt body"
