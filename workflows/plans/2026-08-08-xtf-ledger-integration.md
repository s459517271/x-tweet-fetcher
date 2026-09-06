# 计划：将 tweet-ledger 功能集成进 x-tweet-fetcher（xtf）

**日期**: 2026-08-08
**状态**: 阶段2 完成（CLI 接入 --ledger/--query/--stats，89 tests PASS）
**任务定级**: medium（多文件代码集成，有测试，不改生产服务）
**仓库**: /Users/linyu/projects/x-tweet-fetcher-ledger（新工作区）

## 1. 目标
把 tweet-ledger（推文归档库）的核心能力集成进 xtf 3.0.0，让 xtf 成为"抓取 + 归档 + 查询"一体化工具。作为 xtf 的亮点功能（"一道甜菜"）。

## 2. 现状证据
- xtf 3.0.0（~/Downloads/xtf-v2）：多后端（fxtwitter/nitter/browser），CLI 入口 cli.py，Tweet 模型有 to_dict()
- tweet-ledger（~/Library/Application Support/OpenClaw/...）：sqlite 存储，import_new_tweets.py 提供导入接口
- tweets 表结构：tweet_id (PK), created_at, full_text, lang, is_reply, in_reply_to_status_id, retweeted_status_id, quoted_status_id, urls_json, media_json, raw_json, imported_at

## 3. 设计
### 3.1 新增 CLI 参数
```
xtf --user <name> --limit N --ledger <db_path>
xtf --ledger <db_path> --query "关键词"
xtf --ledger <db_path> --stats
```
- `--ledger <db>`：抓取结果自动归档到 sqlite（复用 import_new_tweets 逻辑）
- `--ledger-query`：查询归档库
- `--ledger-stats`：统计归档库

### 3.2 集成方式（最小侵入）
- 新增 `src/xtf/ledger.py`：封装 sqlite 归档/查询逻辑（从 tweet-ledger 移植，适配 xtf 的 Tweet 模型）
- cli.py 增加参数解析和分发
- 复用 tweet-ledger 的 normalize/ensure_tables 逻辑

### 3.3 亮点功能（"甜菜"）
- **一键归档**：抓取即归档，自动去重
- **本地推文库**：积累自己的推文数据库，可离线查询
- **统计报表**：推文量、活跃时间、来源分布

## 4. 分阶段
- 阶段1: 移植 ledger 核心（sqlite 归档 + 去重）→ 测试
- 阶段2: 接入 CLI（--ledger 参数）→ 测试
- 阶段3: 查询 + 统计功能 → 测试
- 阶段4: 文档 + 示例

## 5. 测试
- 单元测试：归档去重、查询、统计
- 集成测试：抓取 10 条 → 归档 → 查询 → 验证
- 兼容：不影响现有 xtf 命令（无 --ledger 时行为不变）

## 6. 回滚
- 新增文件独立，不影响现有代码
- git 版本控制，可 revert

## 7. Roster
- orchestrator: pi
- sole-writer: codex（DeepSeek 驱动，可独立工作）
- reviewer: grok（跨厂商审查）

## 8. 需要人类决策
- [x] 批准计划
- [x] 确认集成范围（只加归档能力，不改抓取核心）
