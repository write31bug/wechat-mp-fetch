# multi-discussion · 多 Agent 异步讨论系统

## 功能概述

让多个 AI Agent 针对特定话题进行结构化讨论，生成结构化总结报告。

**核心特性：**
- N 个 Agent，不固定数量（2-5 个推荐）
- 可配置轮次（默认 3 轮）
- 串行发言模式（每个 Agent 看到完整上下文）
- 自动总结生成（共识 / 分歧 / 建议 / 各方观点）
- 本地存储，所有数据不上传云端

---

## 工作原理

```
金哥发起讨论
     │
     ▼
Orchestrator（主调度器）
  负责：session 初始化 → N 轮循环 → 总结生成
     │
     ├── StorageManager    负责：目录创建 / 文件读写 / manifest 管理
     ├── ContextBuilder    负责：给每个 Agent 组装上下文
     └── SummaryGenerator  负责：分析发言 → 生成总结报告
```

**存储结构：**
```
~/.openclaw/discussions/{session_id}/
├── manifest.json              # 讨论配置 + 状态
├── history.json              # 结构化发言数据
├── summary.md               # 总结报告
└── contributions/           # 各 Agent 原始发言
    ├── {agent_id}/round{n}.md
    └── ...
```

---

## 使用方式

### 触发方式

在对话中直接发起，例如：

```
讨论主题：AI是否会取代程序员
参与者：乐观派、怀疑派、中立派
轮次：3轮
```

### 使用示例

**示例 1：基础用法（三默认角色）**

```
讨论主题：远程工作是否会成为主流
参与者：乐观派、怀疑派、中立派
轮次：2轮
```

**示例 2：自定义角色**

```
讨论主题：新产品是否要做小程序
参与者：产品经理、技术负责人、运营负责人
轮次：2轮
```

**示例 3：使用预定义角色包**

```
讨论主题：是否应该 All in AI
角色包：investment_debate
轮次：3轮
```

---

## 调用代码

### 方式一：使用预设角色包（推荐）

```python
import sys
sys.path.insert(0, 'E:/openclaw/tasks/multi-discussion')

from config_loader import get_preset
from orchestrator import DiscussionOrchestrator, OrchestratorConfig

# 一行代码加载预设角色包
agents = get_preset("investment_debate")  # 投资分析：多头/空头/客观分析师
# agents = get_preset("product_debate")  # 产品决策：产品经理/技术负责人/运营

orch = DiscussionOrchestrator('AI是否会取代程序员', agents, OrchestratorConfig(rounds=2))
paths = orch.init_session()
# —— 小金在对话里执行 sessions_spawn，调用 orch.save_contribution() ——
orch.complete()
```

### 方式二：自定义角色

```python
from config_loader import get_default_agents
from context_builder import AgentConfig
from orchestrator import DiscussionOrchestrator, OrchestratorConfig

# 基于默认角色修改
agents = get_default_agents()
agents[0].role = "你是一个更激进的乐观派，关注技术创新带来的指数级增长"

# 或完全自定义
agents = [
    AgentConfig(id='pragmatist', name='务实派',
               role='你关注落地和可行性，强调执行细节'),
]

orch = DiscussionOrchestrator('新产品策略', agents, OrchestratorConfig(rounds=3))
paths = orch.init_session()
# —— 小金执行 sessions_spawn ——
orch.complete()
```

---

## 预定义角色包

| 包名 | 角色 | 说明 |
|------|------|------|
| 默认 | optimist / skeptic / neutral | 乐观派 / 怀疑派 / 中立派 |
| investment_debate | bull / bear / analyst | 多头分析师 / 空头分析师 / 客观分析师 |
| product_debate | pm / tech / ops | 产品经理 / 技术负责人 / 运营负责人 |

加载方式：

```python
from config_loader import get_preset, get_default_agents

get_preset("investment_debate")   # 投资讨论
get_preset("product_debate")     # 产品决策
get_default_agents()             # 默认三角色
```

---

## 架构说明

**Python 模块 = 数据层 + 上下文构建
小金（main agent） = 实际调度者**

sessions_spawn 只能在 LLM 工具上下文里执行，不能 Python import。
实际调度由小金在对话里完成，Python 模块负责存储和上下文构建。

**小金调度流程：**

```
小金：讨论主题 + 参与者
    │
    ├── orchestrator.init_session()         创建 session
    │
    ├── for 每轮每 agent：
    │    ├── orchestrator.build_context() 构建上下文
    │    ├── 小金调用 sessions_spawn(     实际调度
    │    │       agent_id=agent.id,
    │    │       task=context,
    │    │       runtime="subagent",
    │    │       mode="run",
    │    │       cleanup="delete"
    │    │   )
    │    └── orchestrator.save_contribution() 存发言
    │
    ├── orchestrator.build_summary_prompt()
    ├── 小金调用 sessions_spawn 生成总结
    ├── orchestrator.save_summary()         写入总结
    └── orchestrator.complete()             标记完成
```

**sessions_spawn 调用示例：**

```python
sessions_spawn(
    agent_id="optimist",    # agent workspace 名称
    task=f"你是 乐观派。\n\n{context}",
    runtime="subagent",
    mode="run",
    cleanup="delete"
)
```

---

## 配置说明

### AgentConfig 参数

| 参数 | 必须 | 说明 |
|------|------|------|
| `id` | ✅ | 唯一标识，如 `optimist`、`dev` |
| `name` | ✅ | 显示名称，如 `乐观派` |
| `role` | ✅ | 角色定位（注入 system prompt） |
| `personality` | ❌ | 性格特点，如 `积极前瞻` |
| `model` | ❌ | 使用模型，默认 `gpt-4o` |
| `temperature` | ❌ | 温度参数，默认 `0.7` |

---

## 输出结果说明

**manifest.json** — 讨论元数据

```json
{
  "session_id": "2026-04-07_AI是否会取代程序员",
  "topic": "AI是否会取代程序员",
  "agents": ["optimist", "skeptic", "neutral"],
  "rounds": 3,
  "current_round": 3,
  "status": "COMPLETED"
}
```

**summary.md** — 总结报告（自动生成）

```markdown
# 讨论总结：AI是否会取代程序员

## 📌 主要共识
1. ...

## ⚡ 主要分歧
1. ...

## 💡 综合建议
...

## 👤 各方观点摘要
...
```

**contributions/{agent_id}/round{n}.md** — 各 Agent 原始发言

---

## 状态追踪

```python
from ask_board import list_discussions, get_discussion_detail

# 列出所有讨论
all_discussions = list_discussions()

# 按状态过滤
in_progress = list_discussions(status='IN_PROGRESS')
completed = list_discussions(status='COMPLETED')

# 查看详情
detail = get_discussion_detail('20260407_xxx')
print(detail['summary_path'])  # 总结文件路径
```

---

## 常见问题

**Q：Agent 数量有限制吗？**
A：没有固定限制，建议 2-5 个。

**Q：支持并行发言吗？**
A：当前只支持串行。并行模式在规划中。

**Q：讨论可以中途停止吗？**
A：可以。manifest.json 的 `status` 实时更新，可以随时中断。

**Q：历史讨论如何查看？**
A：存在 `~/.openclaw/discussions/`，按日期组织。

---

## 故障排查

| 现象 | 可能原因 | 解决方式 |
|------|---------|---------|
| Agent 没发言 | sessions_spawn 未成功 | 检查 subagent 配置 |
| 发言文件没生成 | 调用超时 | 增加 timeout |
| 总结为空 | LLM 返回非 JSON | SummaryGenerator 有降级处理 |
| 状态一直是 IN_PROGRESS | 讨论中断 | 重新发起 |

---

## 文件清单

```
E:\openclaw\tasks\multi-discussion\
├── SKILL.md
├── orchestrator.py
├── context_builder.py
├── storage_manager.py
├── summary_generator.py
├── agent_pool.py
├── config_loader.py      ← 加载预设角色的入口
├── config.yaml           ← 预设角色包定义
└── test_multi_discussion.py
```

---

*文档版本：1.0.0 | 更新日期：2026-04-07*
