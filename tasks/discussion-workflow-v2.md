# 团队异步讨论流程 v2（数据库版）

## 核心理念

保留 .md 文件存储观点内容（可读可分享），用 SQLite 数据库管理状态和元数据（事务安全、并发友好）。

## 与 v1 的核心区别

| 维度 | v1（纯文件） | v2（数据库） |
|------|-------------|-------------|
| 状态存储 | manifest.json | SQLite（WAL 模式） |
| 并发写入 | 无锁，冲突风险 | WAL + busy_timeout，安全 |
| 原子性 | 无，进程崩了可能坏 | 事务原子提交 |
| 状态查询 | 读文件解析 JSON | SQL，高效 |
| 审计日志 | 无 | discussion_log（可选，默认关闭） |
| confidence | 无 | 各 agent 自评，供汇总参考 |

## 数据库 schema

### 表1：discussions（讨论任务）

```sql
CREATE TABLE discussions (
  id              TEXT PRIMARY KEY,
  topic           TEXT NOT NULL,
  background      TEXT,
  goal            TEXT,
  agents          TEXT,          -- JSON array: ["dev","writer","finance"]
  status          TEXT DEFAULT 'PENDING',  -- PENDING/IN_PROGRESS/DONE/CANCELLED
  base_path       TEXT,          -- .md 文件存放根目录
  created         TEXT,
  updated         TEXT
);
```

### 表2：contributions（各方观点状态）

```sql
CREATE TABLE contributions (
  id              TEXT PRIMARY KEY,
  discussion_id   TEXT NOT NULL REFERENCES discussions(id),
  agent           TEXT NOT NULL,  -- dev/writer/finance/community
  file_path       TEXT,           -- .md 文件路径（内容存文件）
  status          TEXT DEFAULT 'PENDING',  -- PENDING/IN_PROGRESS/DONE/FAILED
  confidence      TEXT,           -- high/medium/low（自评结论可信度）
  error_message   TEXT,
  created         TEXT,
  updated         TEXT,
  completed_at    TEXT
);
```

### 表3：discussion_log（审计日志，默认关闭）

```sql
CREATE TABLE discussion_log (
  id              TEXT PRIMARY KEY,
  discussion_id   TEXT NOT NULL REFERENCES discussions(id),
  agent           TEXT,
  action          TEXT,           -- CREATED/DISPATCHED/WRITTEN/COMPLETED/FAILED
  detail          TEXT,
  timestamp       TEXT
);
```

**索引**：
```sql
CREATE INDEX IF NOT EXISTS idx_contributions_discussion ON contributions(discussion_id);
CREATE INDEX IF NOT EXISTS idx_discussion_log_discussion ON discussion_log(discussion_id);
```

---

## 流程（v2）

```
金哥 → main：发起讨论（背景+目标+参与agent）

main：
  1. 调用 create_discussion(topic, agents, background, goal, base_path)
     → 原子写入 discussions + 各 contributions 行
     → base_path 由 main 创建目录后传入（如 E:\openclaw\tasks\discussion\{date}_{topic}\）
  2. 并行 sessions_send 派发给各 agent（mode="run"，单次）
  3. 各 agent：
     - 读取 base_path 目录了解任务背景（main 在目录下放 manifest.json）
     - 写入 {base_path}/{agent}.md（观点内容）
     - 调用 update_contribution(discussion_id, agent, 'DONE', file_path=xxx, confidence='high/medium/low')
     - （可选）调用 log_discussion_action（默认不开启）
  4. main 轮询 get_contributions(discussion_id)
     → 当所有 status=DONE，读取所有 .md
  5. 写入 {base_path}/summary.md → 更新 discussions status=DONE
```

---

## 各 agent 的 .md 格式

```markdown
# [agent] 对「xxx」的观点

## 核心结论
一句话

## 分析逻辑
2-3 句

## 风险提示
如有

## 参考数据
来源
```

## confidence 参考标准（必须填写）

| 等级 | 含义 | 判断标准 |
|------|------|---------|
| **high** | 高可信 | 写过相关文章 / 有实际数据支撑 / 有第一手经验 |
| **medium** | 中可信 | 有逻辑推导但未经实证 / 有不确定性但方向可信 |
| **low** | 低可信 | 跨领域 / 没有数据支撑 / 直觉判断成分居多 |

**注意**：confidence 是自评，main agent 汇总时对 low confidence 内容做降权或二次核实。

## .md 文件路径规范

- **base_path** 由 main 创建讨论时确定，格式：`E:\openclaw\tasks\discussion\{YYYY-MM-DD}_{topic_slug}\`
- 各 agent 写入：`{base_path}/{agent}.md`（如 `dev.md`、`writer.md`）
- 汇总输出：`{base_path}/summary.md`
- **manifest.json** 仍作为任务入口文件存于 base_path，但状态管理完全在 SQLite

---

## ask_board.py 函数封装

```python
from ask_board import *

# 创建讨论（原子事务）
discussion_id = create_discussion(
    topic='议题标题',
    agents=['dev', 'writer', 'finance'],
    background='背景',
    goal='目标',
    base_path='E:\\openclaw\\tasks\\discussion\\2026-04-06_xxx'
)

# 读取讨论
d = get_discussion(discussion_id)

# 读取所有 contributions
cs = get_contributions(discussion_id)

# 更新 contribution（agent 完成时调用）
update_contribution(
    discussion_id,
    agent='dev',
    status='DONE',
    file_path='E:\\openclaw\\tasks\\discussion\\2026-04-06_xxx\\dev.md',
    confidence='high'    # 必须填写
)

# 写审计日志（可选，默认关闭）
log_discussion_action(discussion_id, agent='dev', action='COMPLETED', detail='写入完成')
```

---

## ⚠️ board.db 共库注意事项

讨论功能与任务看板共用 `E:\openclaw\tasks\board.db`：
- ✅ WAL + busy_timeout 已防止锁冲突
- ⚠️ 风险：board.db 损坏时两者同时挂掉，无隔离。建议定期备份 `board.db`
- 如需完全隔离，可将讨论迁移到独立 DB（`board_discussion.db`），只需改 `DB_PATH` 常量

## FAILED 状态说明

`update_contribution` 在最后一个 agent 更新时自动将 discussions.status 改为 DONE。
**规则**：只有 status=DONE 的 agent 才计入；FAILED 的 agent 不触发自动 DONE（由 main agent 确认后手动处理）。

## 设计原则（v2）

| 原则 | 说明 |
|------|------|
| 内容存文件 | .md 可读可分享，是真正的产出 |
| 状态存 DB | WAL 模式 + 事务保证一致性 |
| 原子连接 | `_conn()` 统一处理 WAL + busy_timeout |
| confidence 必填 | 自评信号，汇总时降权 low confidence |
| audit log 可选 | discussion_log 默认关闭，按需开启 |
| 索引保障 | 外键字段有索引，查询不慢 |

---

## 升级检查清单（v1 → v2）

- [x] ask_board.py 已包含 WAL + busy_timeout（`_conn()`）
- [x] init_db() 包含 discussions/contributions/discussion_log 建表
- [x] 外键索引已创建
- [x] confidence 参考标准已写入本文档
- [x] .md 路径规范已定义（base_path + {agent}.md）
- [x] discussion_log 默认关闭（不自动写入）
