<div align="center">

# 🦞 x-tweet-fetcher

**Fetch tweets, timelines, and WeChat articles — zero browser dependency.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue.svg)](https://github.com/openclaw/openclaw)
[![Python 3.7+](https://img.shields.io/badge/Python-3.7+-green.svg)](https://www.python.org)
[![GitHub stars](https://img.shields.io/github/stars/ythx-101/x-tweet-fetcher?style=social)](https://github.com/ythx-101/x-tweet-fetcher)

*Pure HTTP · Python stdlib only · Works everywhere (VPS / Mac / Windows / CI / Claude Code / OpenClaw)*

[Quick Start](#-quick-start) · [Capabilities](#-capabilities) · [Self-hosted Nitter](#-self-hosted-nitter-setup) · [Why Self-host](#-why-self-host) · [Claude Code & CC](#-works-with-claude-code--cc)

</div>

---

## 😤 Problem

```
You: fetch that tweet for me
AI:  I can't access X/Twitter. Please copy-paste the content manually.

You: ...seriously?
```

X has no free API. Scraping gets you blocked. Browser automation is fragile and won't work in headless environments like Claude Code or CI/CD.

**x-tweet-fetcher** solves this: one command → structured JSON, ready for your agent to consume. No API keys, no login, no cookies, **no browser**, **no pip install**.

## 📊 Capabilities

| Feature | Method | Output |
|---------|--------|--------|
| Single tweet | FxTwitter API | text, stats, media, quotes |
| Reply comments | Self-hosted Nitter | threaded comment list |
| User timeline | Self-hosted Nitter | paginated tweet list |
| @mentions monitor | Self-hosted Nitter | incremental new mentions |
| Keyword search | Self-hosted Nitter | real-time tweet stream |
| User profile analysis | Nitter + LLM | MBTI, Big Five, topic graph |
| WeChat article search | Sogou (direct HTTP) | title, url, author, date |
| Tweet growth tracker | FxTwitter API | growth curves, burst detection |

> **For AI Agents**: All output is structured JSON. Import as Python modules for direct integration. Exit codes are cron-friendly (`0`=nothing new, `1`=new content).

## 🚀 Quick Start

### Single tweet (zero setup)

```bash
# Works immediately — no Nitter needed
python3 scripts/fetch_tweet.py --url https://x.com/elonmusk/status/123456789
```

### Timeline, search, replies (needs self-hosted Nitter)

```bash
# Set your Nitter instance URL
export NITTER_URL=http://127.0.0.1:8788

# User timeline
python3 scripts/fetch_tweet.py --user elonmusk --limit 20

# Keyword search — real-time tweets
python3 scripts/nitter_client.py --search "AI agent"

# Tweet replies
python3 scripts/fetch_tweet.py --url https://x.com/elonmusk/status/123456789 --replies

# @mentions monitoring (cron-friendly)
python3 scripts/fetch_tweet.py --monitor @yourusername

# User profile analysis
python3 scripts/x-profile-analyzer.py --user elonmusk --count 100

# WeChat article search (no Nitter needed)
python3 scripts/sogou_wechat.py --keyword "AI Agent" --limit 5 --json
```

## 🖥️ Works with Claude Code / CC

This is the key advantage over browser-based solutions. Since x-tweet-fetcher is **pure HTTP with zero dependencies**, it works perfectly in:

| Environment | Status | Notes |
|-------------|:------:|-------|
| **Claude Code (CC)** | ✅ | No browser to install |
| **OpenClaw** | ✅ | Native skill integration |
| **VPS (headless Linux)** | ✅ | No X11/display needed |
| **Mac / Windows** | ✅ | Just Python |
| **CI/CD pipelines** | ✅ | GitHub Actions, etc. |
| **Docker containers** | ✅ | Minimal image |
| **Termux (Android)** | ✅ | Tested on H618 box |

Previously, tools like Camofox/Playwright required a full browser runtime — impossible in Claude Code, painful on VPS, and fragile everywhere. **No more.**

```bash
# In Claude Code, just point to your Nitter instance:
export NITTER_URL=http://your-vps:8788
python3 scripts/fetch_tweet.py --user YuLin807 --limit 10
```

## 🔧 Self-hosted Nitter Setup

> ⚠️ **Public Nitter instances are dead or unreliable** (as of March 2026, most are returning 403 or timing out). Self-hosting is the only reliable option.

### Why you need this

Twitter removed guest API access in 2023. Nitter now requires real account sessions. Public instances get rate-limited fast because thousands of users share a few accounts. **Your own instance = your own rate limits.**

### 5-minute setup guide

#### 1. Install dependencies

```bash
# Ubuntu/Debian
sudo apt install -y redis-server libpcre3-dev libsass-dev

# Install Nim (Nitter's language)
curl https://nim-lang.org/choosenim/init.sh -sSf | sh
export PATH=$HOME/.nimble/bin:$PATH
```

#### 2. Build Nitter

```bash
git clone https://github.com/zedeus/nitter
cd nitter
nimble build -d:release
nimble scss
cp nitter.example.conf nitter.conf
```

#### 3. Get X session cookies

You need a real X account's cookies. Use a **secondary account** (not your main).

1. Log into X in your browser
2. Open DevTools → Application → Cookies → `x.com`
3. Copy these two values:
   - `auth_token`
   - `ct0`

4. Create `sessions.jsonl`:

```json
{"name":"myaccount","auth_token":"YOUR_AUTH_TOKEN","ct0":"YOUR_CT0"}
```

#### 4. Configure

Edit `nitter.conf`:

```ini
[Server]
address = "127.0.0.1"  # Only local access (security!)
port = 8788

[Config]
hmacKey = "$(openssl rand -hex 32)"  # Generate a random key

[Tokens]
tokenFile = "sessions.jsonl"
```

#### 5. Run

```bash
# Start Redis
sudo systemctl start redis-server

# Start Nitter
./nitter

# Or as a systemd service:
sudo cp nitter.service /etc/systemd/system/
sudo systemctl enable --now nitter
```

#### 6. Test

```bash
curl http://127.0.0.1:8788/YuLin807  # Should return HTML
export NITTER_URL=http://127.0.0.1:8788
python3 scripts/nitter_client.py --search "test"  # Should return JSON
```

### Security

- **Bind to `127.0.0.1` only** — never expose Nitter to the public internet
- **Use a secondary X account** — your session token gives full access
- **Session tokens last ~1 year** — no need to refresh often

## 🤔 Why Self-host?

| | Public Nitter | Self-hosted | Browser (Playwright) |
|--|:---:|:---:|:---:|
| Reliability | ❌ Mostly dead | ✅ 100% uptime | ⚠️ Fragile |
| Speed | Slow (shared) | ⚡ Fast | 🐌 Very slow |
| Works in CC | ✅ (if alive) | ✅ Always | ❌ No |
| Memory usage | — | ~30MB | ~500MB+ |
| Rate limits | Shared with everyone | Only you | N/A |
| Privacy | Third-party sees queries | Self-controlled | Self-controlled |
| Setup time | 0 min | 5 min | 30 min+ |

## ⏰ Cron Integration

All monitoring scripts use exit codes for automation:

| Exit Code | Meaning |
|:---------:|---------|
| `0` | No new content |
| `1` | New content found |
| `2` | Error |

```bash
# Check mentions every 30 min
*/30 * * * * NITTER_URL=http://127.0.0.1:8788 python3 fetch_tweet.py --monitor @username || notify-send "New mentions!"

# Discover tweets daily
0 9 * * * python3 nitter_client.py --search "AI Agent" >> ~/discoveries.jsonl
```

## 📐 How It Works

```
                    ┌─────────────┐
 --url              │  FxTwitter  │  ← Public API, no auth needed
                    │  (free)     │
                    └──────┬──────┘
                           │ JSON
                    ┌──────┴──────┐       ┌──────────┐
 --user             │             │       │  Agent   │
 --replies   ──────▶│   Nitter    │──────▶│  (JSON)  │
 --monitor          │ (self-host) │       │          │
 --search           └─────────────┘       └──────────┘

                    ┌─────────────┐
 sogou_wechat       │   Sogou     │  ← Direct HTTP, no API key
                    │  (search)   │
                    └─────────────┘
```

- **Single tweets**: [FxTwitter](https://github.com/FxEmbed/FxEmbed) public API — always works, zero auth
- **Timeline / Replies / Search / Mentions**: Self-hosted [Nitter](https://github.com/zedeus/nitter) — pure HTTP parsing
- **WeChat articles**: Sogou search — direct HTTP, no browser

## 📦 Requirements

```
Python 3.7+     (that's it)
```

No `pip install`. No `npm install`. No browser. No API keys for basic usage.

| Feature | Extra requirement |
|---------|-----------------|
| Single tweet | Nothing |
| Timeline / Replies / Search | Self-hosted Nitter |
| Profile analysis | Nitter + any LLM API |
| WeChat search | Nothing |
| Growth tracking | Nothing |

## 🤝 Contributing

Issues and PRs welcome! We focus on:

- **X/Twitter** — core platform, Nitter-based
- **WeChat articles** — via Sogou search

Other platforms (Weibo, Bilibili, etc.) are welcome as community PRs.

## 🙏 Acknowledgments

- **[Nitter](https://github.com/zedeus/nitter)** by [zedeus](https://github.com/zedeus) (12.6k ⭐) — the self-hosted Twitter frontend that makes zero-browser tweet fetching possible
- **[FxTwitter](https://github.com/FxEmbed/FxEmbed)** — public API for single tweet data
- **[OpenClaw](https://github.com/openclaw/openclaw)** — the AI agent framework this skill was built for

## 📄 License

[MIT](LICENSE)

---

<div align="center">

*Built for AI agents. Works everywhere. No browser required.* 🦞

**[GitHub](https://github.com/ythx-101/x-tweet-fetcher)** · **[Issues](https://github.com/ythx-101/x-tweet-fetcher/issues)** · **[OpenClaw Q&A](https://github.com/ythx-101/openclaw-qa)**

</div>
