# dev 对「v2 方案修复后」的复审

## 核心结论
**升级** — P0 工程风险已全部修复，代码实现与方案文档基本对齐。

## P0 问题验证

- **WAL 模式**：✅ 已修复
  证据：`_conn()` 函数第 4 行明确执行 `conn.execute('PRAGMA journal_mode=WAL')`

- **init_db 建表**：✅ 已修复
  证据：`init_db()` 包含 3 张新表：`discussions`（第 27 行）、`contributions`（第 39 行）、`discussion_log`（第 52 行），均用 `CREATE TABLE IF NOT EXISTS`

- **busy_timeout**：⚠️ 小差异（不影响升级）
  证据：`_conn()` 第 5 行配置了 `busy_timeout=5000`（5 秒），但 manifest 背景文档写的是 "10s"。代码实现是合理的默认值（SQLite 常见配置），5s vs 10s 属于调优参数，不算错误

- **外键索引**：✅ 已修复
  证据：第 61-62 行有两行 `CREATE INDEX IF NOT EXISTS`，分别对 `contributions(discussion_id)` 和 `discussion_log(discussion_id)` 建索引

## 遗留问题

1. **busy_timeout 数值不一致**：代码写 5000ms，manifest 背景写 10s。建议统一，避免后续困惑。建议统一为 10000（10s），因为并发等待 5s 在高负载时可能偏短

## 最终建议

**建议升级到 v2**。

代码层面四个 P0 全部修复到位，WAL + busy_timeout + 建表 + 索引均已实现。唯一小瑕疵是 busy_timeout 的数值（5s vs 10s）在不同文档中不一致，建议统一为 10s 后再正式上线。

---
confidence: high
