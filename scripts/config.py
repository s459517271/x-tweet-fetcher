#!/usr/bin/env python3
"""
Unified configuration for x-tweet-fetcher scripts.

All external service URLs are configurable via environment variables.
Defaults work for local development; override for VPS/custom setups.

Environment variables:
  XTF_MAC_BRIDGE    — Mac Bridge URL (default: http://localhost:17899)
  XTF_SEARXNG       — SearxNG search URL (default: http://localhost:8080/search)
  XTF_GEMINI_SCRIPT — Path to gemini_chat.py (default: empty, auto-detect)
  GITHUB_TOKEN      — GitHub Personal Access Token (optional, for higher rate limits)
  OPENALEX_EMAIL    — Email for OpenAlex polite pool (optional)
"""
import os

# External service URLs — override via env vars for your setup
MAC_BRIDGE = os.environ.get("XTF_MAC_BRIDGE", "http://localhost:17899")
SEARXNG_URL = os.environ.get("XTF_SEARXNG", "http://localhost:8080/search")
GEMINI_SCRIPT = os.environ.get("XTF_GEMINI_SCRIPT", "")

# API config
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
OPENALEX_EMAIL = os.environ.get("OPENALEX_EMAIL", "")
OPENALEX_API = "https://api.openalex.org"
ARXIV_API = "https://export.arxiv.org/api/query?id_list={arxiv_id}"

# Rate limiting
REQUEST_DELAY = 0.5       # seconds between GitHub scraping calls
OPENALEX_DELAY = 0.2      # seconds between OpenAlex calls
