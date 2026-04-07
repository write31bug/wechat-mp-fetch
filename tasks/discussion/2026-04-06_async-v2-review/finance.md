# finance 对「异步讨论方案 v2」的评审

## 核心结论
**优化后升。** v2 解决了 v1 的并发和原子性问题，但 discussion_log 表增加了不必要的复杂度，建议保留 confidence 字段，其余先跑 MVP。

---

## 核心价值评审

### v2 解决了什么

| 问题 | v1 怎么处理 | v2 怎么处理 | 解决程度 |
|------|-----------|-----------|---------|
| 并发写入冲突 | 无锁，靠协调 | SQLite WAL，进程安全 | ✅ 彻底解决 |
| 状态不一致/坏文件 | 无原子性 | 事务提交 | ✅ 彻底解决 |
| 状态查询效率 | 读文件解析 JSON | SQL 一句搞定 | ✅ 彻底解决 |
| 汇总时不知谁可信 | 无信号 | confidence 字段 | ✅ 新价值 |

v2 对 v1 的核心痛点（并发 + 原子性 + 可查询性）给出了干净解法，没有引入过多新概念。

### v2 没解决什么 / 仍存在的问题

1. **双系统维护成本**：文件 + SQLite 两套系统，ask_board.py 需要同步维护。subagent 端如果用 Python 封装还好；如果用 exec 直接跑 SQL，学习成本上升。
2. **文件优先还是 DB 优先的歧义**：workflow 里说"内容存文件，状态存 DB"，但没定义冲突时谁为准。如果文件写了但 DB 事务回滚，以哪个为准？这个边界条件没明确。
3. **confidence 是自评，非交叉验证**：agent 自己打 confidence，main agent 只能参考，无法独立核实。如果某个 agent 盲目自信打了 high，价值打折。

---

## confidence 字段
**高价值。** 是 v2 里最实用的新增字段。

理由：
- **主 agent 汇总效率直接提升**：不需要读完每个 .md 才知道结论权重，有 confidence 加持可以优先处理高可信度贡献。
- **对财务视角尤为重要**：finance 的结论经常涉及数字和风险判断，如果 main agent 在做最终综合时能给 finance 的内容更多权重，整体质量会上一个台阶。
- **与其他字段互补**：confidence + status + completed_at 三个字段组合，可以还原完整的贡献质量画像。

建议 confidence 字段继续保留，并在文档中明确：**high = 有数据支撑、有风险提示；low = 主观判断、缺乏核实**。

---

## 风险提示

1. **board.db 耦合风险**：discussion 和 task 看板共一个 DB 文件。如果 board.db 因讨论任务频繁写入出现性能问题，会连带影响任务看板的可用性。建议在 ask_board.py 里对两种表操作分开 try/except，避免相互影响。

2. **discussion_log 表可能overkill**：每步操作都写审计日志，在小团队（4个agent）场景下日志量增长快但实际使用率低。如果只是为了"出了问题能查"，可以考虑**降级为可选表**（默认关闭，通过 `discussion_log_enabled=True` 参数开启）。

3. **subagent 端实现复杂度**：如果 subagent 不是 Python 写的（比如直接用 exec 跑 shell），SQLite 操作的原子性和错误恢复更难保证。需要确保所有 agent 都通过 ask_board.py 封装层操作数据库。

4. **confidence 自评可信度问题**：建议在 summary.md 汇总时，main agent 对 low confidence 的内容做二次核实或降权处理，否则高自信的错判比低自信的错判危害更大。

---

## 综合建议

**值得升级，但分步走。**

### 第一步（v2 MVP，直接升）
- 迁移状态管理到 SQLite（discussions + contributions 表）
- 保留 confidence 字段（核心价值）
- **manifest.json 降级为可选**（金哥/主 agent 创建任务时直接写 DB，不再依赖文件）

### 第二步（按需开启）
- discussion_log 表作为**可选审计层**，默认关闭
- 等团队对 v2 稳定性有体感后，再通过参数开启

### 不建议升级的情况
如果 board.db 目前已经承担了较重的任务看板负载（高频 update），引入 discussion 的写操作可能产生竞争。建议先在 **staging 路径**（E:\openclaw\tasks\board_staging.db）单独验证，确认无性能问题后再合并到正式库。

---

**一句话总结**：v2 对 v1 的核心工程缺陷（WAL + 事务 + SQL查询）修正是正确的，confidence 字段是亮点，discussion_log 是锦上添花。推荐升级，但分步实施，audit log 按需开启。
