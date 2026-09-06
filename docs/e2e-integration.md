# xtf-ledger 端到端集成测试记录

**日期**: 2026-08-09
**版本**: xtf 3.1.0（阶段2 完成后）
**方式**: 真实抓取（本地 Nitter 实例 + fxtwitter 官方 API），非 mock

## 环境

- 本地 Nitter：`http://127.0.0.1:8888`（经 FlClash 代理出口）
- fxtwitter API：`https://api.fxtwitter.com`（直连可用）
- 测试用户：`YuLin807`（QingYue）
- 测试库：`/tmp/xtf-e2e.db`（每次从空库开始）

## 链路验证

### 1. 抓取 → 归档（Nitter 时间线）

```bash
PYTHONPATH=src XTF_NITTER=http://127.0.0.1:8888 \
  python -m xtf.cli --user YuLin807 --limit 5 --ledger /tmp/xtf-e2e.db --pretty
```

结果：`count: 5`，`ledger: {inserted: 5, duplicates: 0, skipped: 0}`，5 条真实推文入库。

### 2. 抓取 → 归档（fxtwitter 单推，跨后端去重）

```bash
PYTHONPATH=src python -m xtf.cli \
  --url https://x.com/YuLin807/status/2086132781533544665 --ledger /tmp/xtf-e2e.db --pretty
```

结果：`ledger: {inserted: 0, duplicates: 1}` —— 该推文已被 Nitter 步骤归档，
fxtwitter 单推抓到同一 `tweet_id` 时正确识别为重复，证明**跨后端按 tweet_id 去重生效**。
（fxtwitter 返回的 dict 无 `tweet_id` 字段，CLI 从 URL 注入，见 `cli.py` 单推模式。）

### 3. 查询

```bash
PYTHONPATH=src python -m xtf.cli --ledger /tmp/xtf-e2e.db --query 'sop' --pretty
```

结果：`count: 2`，返回两条含 "sop" 的推文（`full_text` 子串匹配），输出已剔除 `raw_json`。

### 4. 统计

```bash
PYTHONPATH=src python -m xtf.cli --ledger /tmp/xtf-e2e.db --stats --pretty
```

结果：`total_tweets: 5`，时间范围 `Aug 8, 2026 · 4:16 PM UTC → 4:55 PM UTC`，`last_imported_at` 正常。

### 5. 重复抓取幂等性

```bash
PYTHONPATH=src XTF_NITTER=http://127.0.0.1:8888 \
  python -m xtf.cli --user YuLin807 --limit 5 --ledger /tmp/xtf-e2e.db --pretty
```

结果：`ledger: {inserted: 0, duplicates: 5}` —— 全量重复，库不变（`total_tweets` 仍为 5）。

## 结论

抓取 → 归档 → 去重 → 查询 → 统计全链路通过；跨后端去重与幂等性均验证；无 `--ledger` 时行为与 3.0.0 完全一致（回归测试覆盖）。
