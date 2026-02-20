# x-tweet-fetcher

**[中文](#中文) | [English](#english)**

---

<details open>
<summary><h2>中文</h2></summary>

从 X/Twitter **无需登录、无需 API Key** 抓取内容。

[OpenClaw](https://github.com/openclaw/openclaw) Skill。零依赖、零配置。

## 功能概览

### X/Twitter 抓取

| 内容 | 支持 | 依赖 |
|------|------|------|
| 普通推文 | ✅ 全文 + 统计数据 | 无 |
| 长推文 | ✅ 完整文本 | 无 |
| X Articles (长文) | ✅ 完整文章 | 无 |
| 引用推文 | ✅ 内含引用 | 无 |
| 统计数据 (点赞/RT/浏览) | ✅ 包含 | 无 |
| **回复评论** | ⚠️ 带评论 | **需要 Camofox** |
| **用户时间线** | ⚠️ 带时间线 | **需要 Camofox** |

### 国内平台

| 平台 | 内容 | 依赖 |
|------|------|------|
| **微博** | ✅ 帖子、评论、统计数据 | Camofox |
| **B站** | ✅ 视频信息、UP主、播放点赞 | Camofox |
| **CSDN** | ✅ 文章、代码块、统计数据 | Camofox |
| **微信公众号** | ✅ 完整文章、图片 | **无需 (直接 HTTP)** |

## 快速开始

### 基础用法（无需依赖）

```bash
# JSON 输出
python3 scripts/fetch_tweet.py --url "https://x.com/user/status/123456"

# 人类可读文本
python3 scripts/fetch_tweet.py --url "https://x.com/user/status/123456" --text-only

# 格式化 JSON
python3 scripts/fetch_tweet.py --url "https://x.com/user/status/123456" --pretty
```

### 抓取评论和时间线（需要 Camofox）

抓取回复评论或用户时间线需要安装 **Camofox**（反检测浏览器服务）：

```bash
# 方式 1: 作为 OpenClaw 插件安装
openclaw plugins install @askjo/camofox-browser

# 方式 2: 独立安装
git clone https://github.com/jo-inc/camofox-browser
cd camofox-browser
npm install
npm start  # 监听端口 9377
```

然后使用 `--replies` 参数：

```bash
python3 scripts/fetch_tweet.py --url "https://x.com/user/status/123456" --replies
```

## 技术架构

采用 **Strategy Pattern** 设计，易于扩展新平台：

```
fetcher/
├── base.py          # 基础接口
├── fxtwitter.py     # FxTwitter 策略
├── nitter.py        # Nitter 策略
├── camofox.py       # Camofox 策略
└── china/           # 国内平台策略
    ├── weibo.py
    ├── bilibili.py
    ├── csdn.py
    └── wechat.py
```

- **基础模式**：使用 [FxTwitter](https://github.com/FxEmbed/FxEmbed) 公开 API 获取推文数据
- **评论/时间线**：使用 Camofox（基于 Camoufox）绕过反爬虫检测

## Camofox 安装说明

### 什么是 Camofox？

Camofox 是一个基于 [Camoufox](https://camoufox.com) 的反检测浏览器服务 —— 一个在 C++ 层面进行指纹伪装的 Firefox 分支。可绕过：
- Google 机器人检测
- Cloudflare 防护
- 大多数反爬虫措施

### 环境变量（可选）

如果配合 OpenClaw 使用 Camofox，设置 API Key：

```bash
export CAMOFOX_API_KEY="your-secret-key"
openclaw start
```

## 国内平台抓取

自动检测平台类型，一键抓取。

```bash
# 微博帖子
python3 scripts/fetch_china.py --url "https://weibo.com/user/post" --pretty

# B站视频
python3 scripts/fetch_china.py --url "https://www.bilibili.com/video/BVxxxxxx" --pretty

# CSDN 文章
python3 scripts/fetch_china.py --url "https://blog.csdn.net/user/article/details/xxx" --pretty

# 微信公众号文章（无需 Camofox！）
python3 scripts/fetch_china.py --url "https://mp.weixin.qq.com/s/xxxxx" --pretty

# Markdown 输出（带 YAML frontmatter）
python3 scripts/fetch_china.py --url "<URL>" --markdown

# 纯文本输出
python3 scripts/fetch_china.py --url "<URL>" --text-only

# 英文输出
python3 scripts/fetch_china.py --url "<URL>" --lang en
```

### 支持的输出格式

| 格式 | 参数 | 说明 |
|------|------|------|
| JSON | 默认 | 结构化数据，含统计、媒体、元数据 |
| Markdown | `--markdown` | 简洁 markdown，含 YAML frontmatter |
| 纯文本 | `--text-only` | 人类可读纯文本 |

## 输出示例

### JSON 输出

```json
{
  "platform": "twitter",
  "id": "1234567890",
  "url": "https://x.com/user/status/1234567890",
  "author": {
    "id": "user123",
    "name": "Username",
    "display_name": "User Name"
  },
  "content": "Tweet content here...",
  "created_at": "2024-01-01T00:00:00Z",
  "stats": {
    "likes": 100,
    "retweets": 20,
    "replies": 5,
    "views": 1000
  }
}
```

### Markdown 输出

```markdown
---
platform: twitter
id: "1234567890"
author: Username
created_at: 2024-01-01T00:00:00Z
likes: 100
retweets: 20
replies: 5
views: 1000
---

Tweet content here...

[Media: 1 image]
```

## 局限性

- 无法获取已删除或设为私密的推文
- 依赖 FxTwitter / Camofox 服务可用性
- 国内平台：评论可能需要登录（优雅降级）
- 微信公众号：仅支持有效文章链接（不支持过期短链接）

## License

MIT

</details>

---

<details>
<summary><h2>English</h2></summary>

Fetch content from X/Twitter **without login or API keys**.

An [OpenClaw](https://github.com/openclaw/openclaw) skill. Zero dependencies, zero configuration.

## Features

### X/Twitter Fetching

| Content | Support | Requirement |
|---------|---------|-------------|
| Regular tweets | ✅ Full text + stats | None |
| Long tweets | ✅ Full text | None |
| X Articles (long-form) | ✅ Complete article | None |
| Quoted tweets | ✅ Included | None |
| Stats (likes/RT/views) | ✅ Included | None |
| **Reply comments** | ⚠️ With comments | **Camofox required** |
| **User timeline** | ⚠️ With timeline | **Camofox required** |

### China Platforms

| Platform | Content | Requirement |
|----------|---------|-------------|
| **Weibo** | ✅ Posts, comments, stats | Camofox |
| **Bilibili** | ✅ Video info, UP, views, likes | Camofox |
| **CSDN** | ✅ Articles, code blocks, stats | Camofox |
| **WeChat** | ✅ Full articles, images | **None (direct HTTP)** |

## Quick Start

### Basic Usage (No Dependencies)

```bash
# JSON output
python3 scripts/fetch_tweet.py --url "https://x.com/user/status/123456"

# Human readable
python3 scripts/fetch_tweet.py --url "https://x.com/user/status/123456" --text-only

# Pretty JSON
python3 scripts/fetch_tweet.py --url "https://x.com/user/status/123456" --pretty
```

### Fetching Comments & Timeline (Requires Camofox)

To fetch reply comments or user timelines, install **Camofox** (anti-detection browser server):

```bash
# Option 1: Install as OpenClaw plugin
openclaw plugins install @askjo/camofox-browser

# Option 2: Standalone installation
git clone https://github.com/jo-inc/camofox-browser
cd camofox-browser
npm install
npm start  # Starts on port 9377
```

Then use the `--replies` flag:

```bash
python3 scripts/fetch_tweet.py --url "https://x.com/user/status/123456" --replies
```

## Architecture

Built with **Strategy Pattern** for easy extension:

```
fetcher/
├── base.py          # Base interface
├── fxtwitter.py     # FxTwitter strategy
├── nitter.py        # Nitter strategy
├── camofox.py       # Camofox strategy
└── china/           # China platform strategies
    ├── weibo.py
    ├── bilibili.py
    ├── csdn.py
    └── wechat.py
```

- **Basic mode**: Uses [FxTwitter](https://github.com/FxEmbed/FxEmbed) public API
- **Comments/Timeline**: Uses Camofox (powered by Camoufox) to bypass anti-bot detection

## Camofox Setup

### What is Camofox?

Camofox is an anti-detection browser server built on [Camoufox](https://camoufox.com) - a Firefox fork with fingerprint spoofing at the C++ level. It can bypass:
- Google bot detection
- Cloudflare protection
- Most anti-scraping measures

### Environment Variable (Optional)

If using Camofox with OpenClaw, set the API key:

```bash
export CAMOFOX_API_KEY="your-secret-key"
openclaw start
```

## China Platform Fetcher

Automatic platform detection for Chinese platforms.

```bash
# Weibo post
python3 scripts/fetch_china.py --url "https://weibo.com/user/post" --pretty

# Bilibili video
python3 scripts/fetch_china.py --url "https://www.bilibili.com/video/BVxxxxxx" --pretty

# CSDN article
python3 scripts/fetch_china.py --url "https://blog.csdn.net/user/article/details/xxx" --pretty

# WeChat article (no Camofox needed!)
python3 scripts/fetch_china.py --url "https://mp.weixin.qq.com/s/xxxxx" --pretty

# Markdown output with YAML frontmatter
python3 scripts/fetch_china.py --url "<URL>" --markdown

# Human readable text
python3 scripts/fetch_china.py --url "<URL>" --text-only

# English output
python3 scripts/fetch_china.py --url "<URL>" --lang en
```

### Supported Output Formats

| Format | Flag | Description |
|--------|------|-------------|
| JSON | (default) | Structured data with stats, media, metadata |
| Markdown | `--markdown` | Clean markdown with YAML frontmatter |
| Text | `--text-only` | Human-readable plain text |

## Output Examples

### JSON Output

```json
{
  "platform": "twitter",
  "id": "1234567890",
  "url": "https://x.com/user/status/1234567890",
  "author": {
    "id": "user123",
    "name": "Username",
    "display_name": "User Name"
  },
  "content": "Tweet content here...",
  "created_at": "2024-01-01T00:00:00Z",
  "stats": {
    "likes": 100,
    "retweets": 20,
    "replies": 5,
    "views": 1000
  }
}
```

### Markdown Output

```markdown
---
platform: twitter
id: "1234567890"
author: Username
created_at: 2024-01-01T00:00:00Z
likes: 100
retweets: 20
replies: 5
views: 1000
---

Tweet content here...

[Media: 1 image]
```

## Limitations

- Cannot fetch deleted or private tweets
- Depends on FxTwitter / Camofox service availability
- China platforms: Comments may require login (graceful degradation)
- WeChat: Only works with valid article links (not expired short links)

## License

MIT

</details>
