# dev 对「异步讨论方案 v2」的评审

## 核心结论
**优化后升。** WAL 模式解决并发写入安全是核心价值，但 schema 缺索引、ask_board.py 缺 WAL 初始化和超时配置，实现时需补上这些才能上生产。

---

## schema 评审

### 1. 三张表结构基本合理，但缺关键索引
`discussions.contributions(discussion_id)` 和 `discussion_log(discussion_id)` 都会做关联查询，两个外键字段都应该建索引。当前 schema 未声明任何索引，在 agent 数量多或 log 表增长后会有性能问题。建议：
```sql
CREATE INDEX IF NOT EXISTS idx_contributions_discussion ON contributions(discussion_id);
CREATE INDEX IF NOT EXISTS idx_discussion_log_discussion ON discussion_log(discussion_id);
```

### 2. `agents` 字段存 JSON 字符串可接受，但查询不友好
`discussions.agents` 用 JSON array 存储，精确匹配可以，但无法做"查询所有参与 dev 的讨论"这类操作。考虑到 agent 列表本身稳定（讨论创建时写入后几乎不变），这个 tradeoff 可以接受。后续如需扩展查询，再考虑拆表。

### 3. `confidence` 字段设计有价值但语义模糊
`contributions.confidence` 定位是"汇总时参考"，但没有定义计算规则，也没有在流程中实际被消费。**建议明确：只在 FAILED 时记录 error_message，confidence 改为记录结论来源置信度**（如 LLM 自评等级），并在 manifest 流程里说明汇总逻辑如何参考它，否则这个字段会沦为空值。

---

## 工程风险

### 风险1：`ask_board.py` 初始化未包含新表
现有 `init_db()` 只建 `tasks` 表，v2 扩展的 3 张表没有建表逻辑。如果直接调用新函数（`create_discussion` 等），会报 `no such table`。
**修复：** 在 `init_db()` 里加 3 个 `CREATE TABLE IF NOT EXISTS`。

### 风险2：WAL 模式未显式启用
当前 `ask_board.py` 所有连接都是 `sqlite3.connect(DB_PATH)`，没有设置 WAL 模式。如果 OS 默认是 DELETE 模式，多进程并发写入仍会有锁冲突。
**修复：** 每次连接后执行 `conn.execute('PRAGMA journal_mode=WAL')`，并在连接对象上设置 `busy_timeout`。

### 风险3：subagent 并发写入无超时保护
多个 agent 并行 `UPDATE contributions` 时，SQLite 写锁冲突会直接抛 `sqlite3.OperationalError: database is locked`，没有重试机制。
**修复：** 设置 `busy_timeout`（如 5000ms），或者在 Python 层做一次重试（3次，指数退避）。

### 风险4：board.db 损坏影响面扩大
合并后 board.db 同时承载 task 看板和讨论系统，一张表出问题可能影响另一套流程。需要确认备份策略（目前无）。

---

## 具体改进建议

### 建议1：显式初始化 + WAL + timeout（必须）
每个数据库连接函数开头统一处理：
```python
conn = sqlite3.connect(DB_PATH, timeout=10)
conn.execute('PRAGMA journal_mode=WAL')
conn.execute('PRAGMA busy_timeout=5000')
```

### 建议2：`create_discussion` 应该是一个原子事务（必须）
当前 workflow 里"向 discussions 写行 + 向各 contributions 写 PENDING 行"分两步，如果中间崩溃会导致孤立状态。应该在一个 `with conn:` 事务里完成，或者 main agent 先写入 manifest.json 作为幂等保障。

### 建议3：`get_pending_contributions(discussion_id)` 函数签名问题（次要）
按 `ask_board.py` 现有风格，`discussion_id` 应作为第二个参数，但 v2 函数签名里把它放第一位——不一致。保持与现有函数风格统一（`task_id` 在前），避免调用时混淆。

---

## v1 vs v2 总结

| | v1 | v2 |
|---|---|---|
| 并发安全 | ❌ 无，文件锁不可靠 | ✅ WAL + 事务原子 |
| 状态查询 | ❌ 读文件解析 JSON | ✅ SQL 高效 |
| 审计日志 | ❌ 无 | ✅ discussion_log |
| 复杂度 | 低 | 中（需维护 schema） |
| 依赖 | 无 | SQLite |

**结论：** 如果团队只有 2-3 个 agent、讨论频率低，v1 够用。如果要扩展到 4+ agent 或频繁并发讨论，v2 的 ACID 保证是值得的。**建议先上 v2，但必须实现建议1（ WAL + timeout）和建议2（init_db 补表）。**
