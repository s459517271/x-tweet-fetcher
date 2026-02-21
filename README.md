# x-tweet-fetcher

🦞 **Fetch tweets and replies from X/Twitter without login or API keys. OpenClaw Skill.**

**[中文](#中文) | [English](#english)**

---

<details open>
<summary><h2>中文</h2></summary>

从 X/Twitter **无需登录、无需 API Key** 抓取内容。

[OpenClaw](https://github.com/openclaw/openclaw) Skill。零依赖、零配置。

### ⭐ 亮点功能

- 🐦 **推文抓取** — 单条推文、长推文、X Articles，零依赖
- 💬 **评论区抓取** — 完整评论 + 嵌套回复递归抓取
- 📊 **用户时间线** — 一次抓 300 条，支持翻页
- 🔍 **Google 搜索** — `camofox_search()` 零成本零 API Key 搜 Google
- 🇨🇳 **国内平台** — 微博/B站/CSDN/微信公众号，给链接出内容
- 🧠 **用户画像分析** — AI 分析推文生成 MBTI/大五/星座/话题图谱

## 功能概览

### X/Twitter 抓取

| 内容 | 支持 | 依赖 |
|------|------|------|
| 普通推文 | ✅ 全文 + 统计数据 | 无 |
| 长推文 (Twitter Blue) | ✅ 完整文本 | 无 |
| X Articles (长文) | ✅ 完整文章 | 无 |
| 引用推文 | ✅ 内含引用 | 无 |
| 统计数据 (点赞/RT/浏览) | ✅ 包含 | 无 |
| **回复评论** | ✅ 含嵌套回复 | **Camofox** |
| **用户时间线** | ✅ 支持翻页(300+条) | **Camofox** |

### 国内平台

| 平台 | 内容 | 依赖 |
|------|------|------|
| **微博** | ✅ 帖子、评论、统计数据 | Camofox |
| **B站** | ✅ 视频信息、UP主、播放点赞 | Camofox |
| **CSDN** | ✅ 文章、代码块、统计数据 | Camofox |
| **微信公众号** | ✅ 完整文章、图片 | **无需 Camofox** |

### 额外工具

| 工具 | 说明 | 依赖 |
|------|------|------|
| `camofox_search()` | 零成本 Google 搜索，不需要 API Key | Camofox |
| `x-profile-analyzer` | AI 用户画像分析 (MBTI/大五/星座) | Camofox + AI API |

## 快速开始

### 基础用法（零依赖）

```bash
# JSON 输出
python3 scripts/fetch_tweet.py --url "https://x.com/user/status/123456"

# 人类可读文本
python3 scripts/fetch_tweet.py --url "https://x.com/user/status/123456" --text-only

# 格式化 JSON
python3 scripts/fetch_tweet.py --url "https://x.com/user/status/123456" --pretty
```

### 抓取评论区（需要 Camofox）

```bash
# 抓取推文 + 所有评论（含嵌套回复）
python3 scripts/fetch_tweet.py --url "https://x.com/user/status/123456" --replies

# 文本模式
python3 scripts/fetch_tweet.py --url "https://x.com/user/status/123456" --replies --text-only
```

### 抓取用户时间线

```bash
# 抓取最近 300 条推文（自动翻页）
python3 scripts/fetch_tweet.py --user username --limit 300
```

### Google 搜索（零成本）

```python
# Python 调用
from scripts.camofox_client import camofox_search
results = camofox_search("你的搜索关键词")
# 返回: [{"title": "...", "url": "...", "snippet": "..."}, ...]
```

```bash
# 命令行
python3 scripts/camofox_client.py "你的搜索关键词"
```

> 💡 用 Camofox 浏览器直接搜 Google，**不需要 Brave Search API Key**，零成本。

### 用户画像分析

```bash
# 分析用户推文，生成人格画像报告
python3 scripts/x-profile-analyzer.py --user username

# 指定抓取数量
python3 scripts/x-profile-analyzer.py --user username --count 300

# 只抓数据不调 AI
python3 scripts/x-profile-analyzer.py --user username --no-analyze

# 保存报告
python3 scripts/x-profile-analyzer.py --user username --output report.md
```

AI 分析生成：MBTI 人格类型、大五人格评分、星座预测、核心话题图谱、沟通风格分析。

### 国内平台抓取

```bash
# 自动检测平台，给链接出内容
python3 scripts/fetch_china.py --url "https://weibo.com/..."
python3 scripts/fetch_china.py --url "https://bilibili.com/..."
python3 scripts/fetch_china.py --url "https://blog.csdn.net/..."
python3 scripts/fetch_china.py --url "https://mp.weixin.qq.com/..."  # 无需 Camofox

# 输出格式
python3 scripts/fetch_china.py --url "<URL>" --markdown    # Markdown
python3 scripts/fetch_china.py --url "<URL>" --text-only   # 纯文本
python3 scripts/fetch_china.py --url "<URL>" --lang en      # 英文输出
```

## Camofox 安装

> ⚠️ 评论区抓取、时间线、国内平台（除微信）、Google 搜索都需要 Camofox。
> 基础推文抓取**不需要** Camofox。

### 什么是 Camofox？

[Camofox](https://github.com/jo-inc/camofox-browser) 是基于 [Camoufox](https://camoufox.com) 的反检测浏览器服务 —— Firefox 分支，C++ 层面指纹伪装。可绕过：
- Google 机器人检测
- Cloudflare 防护
- 大多数反爬虫措施

### 安装方式

**方式 1: OpenClaw 插件（推荐）**

```bash
openclaw plugins install @askjo/camofox-browser
```

**方式 2: 独立安装**

```bash
git clone https://github.com/jo-inc/camofox-browser
cd camofox-browser
npm install
npm start  # 监听端口 9377
```

### 验证安装

```bash
curl http://localhost:9377/health
# 返回: {"status":"ok"}
```

### 环境变量（可选）

```bash
export CAMOFOX_API_KEY="your-secret-key"
```

## 技术架构

采用 **Strategy Pattern** 设计，易于扩展新平台：

```
x-tweet-fetcher/
├── SKILL.md                    # Agent 技能文件
├── README.md                   # 本文件
├── CHANGELOG.md                # 更新日志
├── scripts/
│   ├── fetch_tweet.py          # 主抓取器（推文 + 评论 + 时间线）
│   ├── fetch_china.py          # 国内平台抓取器
│   ├── camofox_client.py       # Camofox API 客户端 + camofox_search()
│   ├── x-profile-analyzer.py   # AI 用户画像分析
│   └── version_check.py        # 后台版本检查（启动时静默检查新版本）
└── VERSION
```

- **基础模式**：[FxTwitter](https://github.com/FxEmbed/FxEmbed) 公开 API
- **评论/时间线**：Camofox → Nitter（隐私友好的 X 前端）
- **国内平台**：Camofox 渲染 JS → 提取内容
- **Google 搜索**：Camofox 打开 Google → 解析结果

## 局限性

- 无法获取已删除或私密推文
- 依赖 FxTwitter / Camofox 服务可用性
- 国内平台：知乎/小红书需要 Cookie 导入登录
- 微信公众号：仅支持有效文章链接（不支持过期短链接）

## License

MIT

</details>

---

<details>
<summary><h2>English</h2></summary>

Fetch content from X/Twitter **without login or API keys**.

An [OpenClaw](https://github.com/openclaw/openclaw) skill. Zero dependencies, zero configuration.

### ⭐ Highlights

- 🐦 **Tweet Fetching** — Single tweets, long tweets, X Articles, zero deps
- 💬 **Reply Threads** — Full comments + recursive nested replies
- 📊 **User Timeline** — Fetch 300+ tweets with pagination
- 🔍 **Google Search** — `camofox_search()` zero-cost, no API key needed
- 🇨🇳 **Chinese Platforms** — Weibo/Bilibili/CSDN/WeChat, just give a URL
- 🧠 **Profile Analysis** — AI-powered MBTI/Big Five/persona analysis from tweets

## Features

### X/Twitter

| Content | Support | Requirement |
|---------|---------|-------------|
| Regular tweets | ✅ Full text + stats | None |
| Long tweets (Blue) | ✅ Full text | None |
| X Articles (long-form) | ✅ Complete article | None |
| Quoted tweets | ✅ Included | None |
| Stats (likes/RT/views) | ✅ Included | None |
| **Reply comments** | ✅ With nested replies | **Camofox** |
| **User timeline** | ✅ Pagination (300+) | **Camofox** |

### Chinese Platforms

| Platform | Content | Requirement |
|----------|---------|-------------|
| **Weibo** | ✅ Posts, comments, stats | Camofox |
| **Bilibili** | ✅ Video info, views, likes | Camofox |
| **CSDN** | ✅ Articles, code blocks | Camofox |
| **WeChat** | ✅ Full articles, images | **None** |

### Extra Tools

| Tool | Description | Requirement |
|------|-------------|-------------|
| `camofox_search()` | Zero-cost Google search, no API key | Camofox |
| `x-profile-analyzer` | AI profile analysis (MBTI/Big Five) | Camofox + AI API |

## Quick Start

### Basic (No Dependencies)

```bash
# JSON output
python3 scripts/fetch_tweet.py --url "https://x.com/user/status/123456"

# Human readable
python3 scripts/fetch_tweet.py --url "https://x.com/user/status/123456" --text-only
```

### Reply Threads (Requires Camofox)

```bash
python3 scripts/fetch_tweet.py --url "https://x.com/user/status/123456" --replies
```

### User Timeline

```bash
python3 scripts/fetch_tweet.py --user username --limit 300
```

### Google Search (Zero Cost)

```python
from scripts.camofox_client import camofox_search
results = camofox_search("your query")
```

```bash
python3 scripts/camofox_client.py "your query"
```

> 💡 Uses Camofox browser to search Google directly. **No Brave API key needed.**

### Profile Analysis

```bash
python3 scripts/x-profile-analyzer.py --user username --count 300 --output report.md
```

### Chinese Platforms

```bash
python3 scripts/fetch_china.py --url "https://weibo.com/..."
python3 scripts/fetch_china.py --url "https://mp.weixin.qq.com/..."  # No Camofox needed
```

## Camofox Setup

> ⚠️ Required for: replies, timelines, Chinese platforms (except WeChat), Google search.
> **Not required** for basic tweet fetching.

[Camofox](https://github.com/jo-inc/camofox-browser) is an anti-detection browser based on [Camoufox](https://camoufox.com) (Firefox fork with C++ fingerprint spoofing).

**Install:**

```bash
# Option 1: OpenClaw plugin (recommended)
openclaw plugins install @askjo/camofox-browser

# Option 2: Standalone
git clone https://github.com/jo-inc/camofox-browser
cd camofox-browser && npm install && npm start  # Port 9377
```

**Verify:**

```bash
curl http://localhost:9377/health
```

## File Structure

```
x-tweet-fetcher/
├── SKILL.md                    # Agent skill file
├── README.md                   # This file
├── scripts/
│   ├── fetch_tweet.py          # Main fetcher (tweets + replies + timeline)
│   ├── fetch_china.py          # Chinese platform fetcher
│   ├── camofox_client.py       # Camofox API client + camofox_search()
│   ├── x-profile-analyzer.py   # AI profile analyzer
│   └── version_check.py        # Background version checker (silent on startup)
└── VERSION
```

## Limitations

- Cannot fetch deleted or private tweets
- Depends on FxTwitter / Camofox availability
- Chinese platforms: Zhihu/Xiaohongshu need cookie import
- WeChat: Only valid article links (no expired short links)

## License

MIT

</details>
