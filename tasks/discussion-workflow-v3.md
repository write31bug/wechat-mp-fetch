# 团队异步讨论流程 v3（两轮制）

## 核心理念

**先独立思考，再交叉验证。**

两轮制：Round 1 各方独立撰写，Round 2 互读后补充修正。避免先入为主，同时真正实现观点交流。

## 与 v2 的核心区别

| 维度 | v2（单轮） | v3（两轮） |
|------|-----------|-----------|
| 轮次 | 1 轮，各自写完 | 2 轮，Round 2 互读 |
| 交叉验证 | 无 | Round 2 做认同/反驳/补充 |
| 状态节点 | DONE | ROUND1_DONE → ROUND2_DONE |
| 汇总质量 | 各自独立，可能重复/冲突 | 先独立再交流，有碰撞有深化 |

---

## 流程（v3 两轮制）

```
金哥 → main：发起讨论（背景+目标+参与agent）

main：
  1. 调用 create_discussion(topic, agents, background, goal, base_path)
     → base_path 由 main 创建，如 E:\openclaw\tasks\discussion\{date}_{topic}\
  2. 在 base_path 写入 manifest.json，字段 round="round1"
  3. 并行 sessions_send 派发给各 agent（mode="run"，单次）
  4. 各 agent（Round 1）：
     - 读取 base_path/manifest.json
     - 写入 {base_path}/{agent}.md，标题标注 ## 第一轮
     - 调用 update_contribution(discussion_id, agent, 'ROUND1_DONE', file_path=xxx, confidence='high/medium/low')
  5. main 轮询 get_contributions(discussion_id)
     → 当所有 agent 都是 ROUND1_DONE（或 DONE/FAILED），通知金哥
  6. 【金哥手动】确认进入 Round 2
  7. main 更新 manifest.json 的 round="round2"，重新派发给各 agent
  8. 各 agent（Round 2）：
     - 读取 base_path/{other_agent}.md（其他所有人的 Round 1 内容）
     - 在自己的 {agent}.md 追加 ## 第二轮，内容包括：
       * 认同哪些点（及原因）
       * 不认同哪些点（及理由）
       * 补充或修正
       * 是否有新结论
     - 调用 update_contribution(discussion_id, agent, 'ROUND2_DONE', file_path=xxx, confidence='high/medium/low')
  9. main 轮询，当所有 ROUND2_DONE，读取所有 .md
  10. 写入 {base_path}/summary.md → discussions status=DONE
```

---

## 状态机（v3）

```
PENDING → ROUND1_DONE → ROUND2_DONE
                ↓
             FAILED（任意轮失败）
```

- **ROUND1_DONE**：第一轮完成，等待其他 agent
- **ROUND2_DONE**：第二轮完成，视为最终完成（等价于 v2 的 DONE）
- discussions 自动 DONE：当所有 contributions 不再是 PENDING

---

## 各 agent .md 格式（v3）

### Round 1 结构

```markdown
# [agent] 对「xxx」的观点

## 第一轮

### 核心结论
一句话

### 分析逻辑
2-3 句

### 风险提示
如有

### 参考数据
来源
```

### Round 2 追加结构

```markdown
## 第二轮

### 认同的点
- 其他 agent 的 xxx（原因）

### 不认同的点
- 其他 agent 的 xxx（理由）

### 补充与修正
新的信息或角度

### 最终结论
经交叉验证后的修正结论
```

---

## confidence 参考标准（v3）

| 等级 | 含义 | 判断标准 |
|------|------|---------|
| **high** | 高可信 | 写过相关文章 / 有实际数据支撑 / 有第一手经验 |
| **medium** | 中可信 | 有逻辑推导但未经实证 / 有不确定性但方向可信 |
| **low** | 低可信 | 跨领域 / 没有数据支撑 / 直觉判断成分居多 |

**注意**：
- Round 1 结束时自评 Round 1 的 confidence
- Round 2 结束时可更新 confidence（基于交叉验证后是否更有把握）

---

## manifest.json 格式（v3）

```json
{
  "id": "2026-04-06_xxx",
  "topic": "议题标题",
  "background": "背景",
  "goal": "目标",
  "agents": ["dev", "writer", "finance"],
  "round": "round1",
  "created": "2026-04-06 22:00:00",
  "updated": "2026-04-06 22:00:00"
}
```

- `round` 字段决定当前所处轮次：main 在 Round 2 开始前更新为 `"round2"`

---

## ask_board.py 函数（v3 新增/变更）

```python
from ask_board import *

# 创建讨论（不变）
discussion_id = create_discussion(...)

# Round 1 完成时调用
update_contribution(
    discussion_id,
    agent='writer',
    status='ROUND1_DONE',
    file_path='E:\\openclaw\\tasks\\discussion\\2026-04-06_xxx\\writer.md',
    confidence='high'
)

# Round 2 完成时调用
update_contribution(
    discussion_id,
    agent='writer',
    status='ROUND2_DONE',
    file_path='E:\\openclaw\\tasks\\discussion\\2026-04-06_xxx\\writer.md',
    confidence='high'   # 可更新
)
```

**status 取值**：`PENDING` / `ROUND1_DONE` / `ROUND2_DONE` / `DONE` / `FAILED`

---

## 升级检查清单（v2 → v3）

- [x] ask_board.py 支持 ROUND1_DONE / ROUND2_DONE 状态，状态值合法性校验
- [x] discussions 自动 DONE 条件改为"所有 contributions 不是 PENDING"
- [x] workflow v3 文档（两轮制）
- [x] manifest.json 加 round 字段
- [x] .md 格式更新（第一轮 + 第二轮结构）
- [ ] 各 agent SOUL/AGENTS.md 需同步更新流程说明

---

## 设计原则（v3）

| 原则 | 说明 |
|------|------|
| 先独立后交叉 | Round 1 独立，Round 2 互读，保证不先入为主 |
| 状态分层 | ROUND1_DONE / ROUND2_DONE 语义清晰，金哥可控 |
| 内容存文件 | .md 可读，Round 2 时可互引 |
| confidence 自评 | 两轮均可更新，体现认知升级 |
| 金哥手动触发 Round 2 | 简单可控，避免自动逻辑 bug |
