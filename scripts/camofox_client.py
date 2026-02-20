#!/usr/bin/env python3
"""
Camofox Client - Shared module for Camofox browser automation.

Provides functions to open tabs, get snapshots, and fetch pages via Camofox REST API.
Used by fetch_tweet.py and fetch_china.py.
"""

import json
import sys
import time
import urllib.request
import urllib.error
from typing import Optional


def check_camofox(port: int = 9377) -> bool:
    """Return True if Camofox is reachable."""
    try:
        req = urllib.request.Request(f"http://localhost:{port}/tabs", method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            resp.read()
        return True
    except Exception:
        return False


def camofox_open_tab(url: str, session_key: str, port: int = 9377) -> Optional[str]:
    """Open a new Camofox tab; return tabId or None."""
    try:
        payload = json.dumps({
            "userId": "x-tweet-fetcher",
            "sessionKey": session_key,
            "url": url,
        }).encode()
        req = urllib.request.Request(
            f"http://localhost:{port}/tabs",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        return data.get("tabId")
    except Exception as e:
        print(f"[Camofox] open tab error: {e}", file=sys.stderr)
        return None


def camofox_snapshot(tab_id: str, port: int = 9377) -> Optional[str]:
    """Get page snapshot text from Camofox tab."""
    try:
        url = f"http://localhost:{port}/tabs/{tab_id}/snapshot?userId=x-tweet-fetcher"
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        return data.get("snapshot", "")
    except Exception as e:
        print(f"[Camofox] snapshot error: {e}", file=sys.stderr)
        return None


def camofox_close_tab(tab_id: str, port: int = 9377):
    """Close a Camofox tab."""
    try:
        req = urllib.request.Request(
            f"http://localhost:{port}/tabs/{tab_id}",
            method="DELETE",
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass


def camofox_fetch_page(url: str, session_key: str, wait: float = 8, port: int = 9377) -> Optional[str]:
    """Open URL in Camofox, wait, snapshot, close. Returns snapshot text."""
    tab_id = camofox_open_tab(url, session_key, port)
    if not tab_id:
        return None
    time.sleep(wait)
    snapshot = camofox_snapshot(tab_id, port)
    camofox_close_tab(tab_id, port)
    return snapshot
