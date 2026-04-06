# Self-Improving Agent 使用教程

## 这个 Skill 是什么

自动记录学习笔记、错误和纠正，持续优化 Agent 表现。每次被纠正、发现新方法、或遇到失败时自动写入日志，定期生成报告并建议更新 SOUL.md。

**评分**：LobeHub 4.88/5，337次安装，GitHub ⭐ 2596

---

## 现状：装了两个版本

| 版本 | 来源 | 存放位置 |
|------|------|---------|
| xiucheng 原版 | ClawHub（早期安装） | `E:\openclaw\main\skills\self-improving-agent\` |
| LobeHub 升级版 | LobeHub（更成熟） | 尚未安装 |

建议用 **LobeHub 版本**，结构更完整，有 promotion 机制。

---

## LobeHub 版核心机制

### 三类日志文件

在 workspace 建立 `.learnings/` 目录，包含：

```
.learnings/
├── LEARNINGS.md      # 学到的教训（LRN-YYYYMMDD-XXX）
├── ERRORS.md         # 错误记录（ERR-YYYYMMDD-XXX）
└── FEATURE_REQUESTS.md  # 功能需求（FEAT-YYYYMMDD-XXX）
```

### 记录格式（LRN-YYYYMMDD-XXX）

```markdown
## [LRN-20260403-001] category
**Logged**: 2026-04-03T09:00:00Z
**Priority**: high
**Status**: pending
**Area**: config

### Summary
One-line description of what was learned

### Details
Full context: what happened, what was wrong, what's correct

### Suggested Action
Specific fix or improvement to make

### Metadata
- Source: conversation | error | user_feedback
- Related Files: path/to/file.ext
- Tags: tag1, tag2
- See Also: LRN-20250110-001
- Pattern-Key: simplify.dead_code (optional, for recurring patterns)
- Recurrence-Count: 1 (optional)
- First-Seen: 2026-04-03 (optional)
- Last-Seen: 2026-04-03 (optional)
```

### 自动 Promotion 机制

好的教训会自动提升到项目记忆文件：
- `AGENTS.md` — 写入团队规则
- `CLAUDE.md` / `SOUL.md` — 写入行为准则
- 普通教训保留在 `.learnings/` 中待处理

---

## 安装步骤（LobeHub 版）

### 1. 注册设备（如果没注册过）

```bash
npx -y @lobehub/market-cli register \
  --name "小金" \
  --description "金哥的AI中枢主管" \
  --source open-claw
```

### 2. 安装 Skill

```bash
# 安装到全局（所有 agent 共享）
npx -y @lobehub/market-cli skills install openclaw-skills-self-improving-agent-1-0-0

# 安装到 main agent（当前配置）
npx -y @lobehub/market-cli skills install openclaw-skills-self-improving-agent-1-0-0 --agent open-claw
```

### 3. 建立目录结构

在 main workspace 建立 `.learnings/` 目录：

```python
# 在 E:\openclaw\main\ 下创建
import os
os.makedirs("E:/openclaw/main/.learnings", exist_ok=True)
```

或直接告诉小金：`帮我创建 .learnings 目录和三个日志文件`

### 4. 验证安装

```bash
python E:\openclaw\main\skills\self-improving-agent\self_improving.py --stats
```

---

## 使用方法

### 触发时机（何时记录）

1. **被金哥纠正时** — "不对，应该是……"
2. **命令/操作失败时** — exec 出错、工具调用失败
3. **发现更好的方法时** — 以前的方法不对，现在找到了更好的
4. **用户提出不存在的能力需求时** — "你能……吗？" → 记录为功能需求
5. **意识到知识过时/错误时** — 主动承认并记录

### 手动记录

```python
from self_improving import SelfImprovingAgent

sia = SelfImprovingAgent(workspace="E:/openclaw/main")

# 记录一个学习
sia.log_improvement(
    "被金哥指出：回答技术问题时不应该跳步骤，应该先查源码再回答",
    category="communication"
)
```

### 生成周报

```python
report = sia.generate_weekly_report()
print(report)
```

输出示例：
```
# 🔄 Self-Improvement Weekly Report
Generated: 2026-04-03 09:30

## 📊 This Week's Insights
- Total improvements logged: 5

## 🎯 Next Week Goals
- Continue monitoring conversation quality
- Identify patterns in user feedback
- Update response strategies based on insights
```

### 查看统计

```python
stats = sia.get_improvement_stats()
# {'log_exists': True, 'soul_exists': True, 'total_entries': 5, 'log_size_kb': 2.34}
```

### 建议更新 SOUL.md

```python
suggestions = sia.suggest_soul_updates()
# ['Consider adding conciseness to personality traits', ...]
```

---

## 配置到 Agent

安装后，在 `openclaw.json` 的 `skills.entries` 中启用：

```json
{
  "skills": {
    "entries": {
      "self-improving-agent": {
        "enabled": true,
        "config": {
          "auto_analyze": true,
          "improvement_log": "./.learnings/LEARNINGS.md",
          "soul_file": "./SOUL.md"
        }
      }
    }
  }
}
```

或在 AGENTS.md 里加一行到工作流程：

```
每次被纠正或发现重要教训 → 立即调用 self-improving-agent 记录
每周生成一次改进报告 → 同步到 SOUL.md/AGENTS.md
```

---

## 对我们最有用的场景

结合今天的讨论，建议这样用：

| 场景 | 触发 | 记录类型 |
|------|------|---------|
| 被金哥指出回答太急躁 | 立即记录 | LRN |
| subagent session 清理发现 bug | 立即记录 | ERR |
| 希望小金有某个新能力 | 记录需求 | FEAT |
| 技术问题判断错误 | 记录教训 | LRN |
| 找到一个更好的工作流 | 记录方法 | LRN |

---

## 今天的教训怎么录入

刚才讨论"回答太急躁"的结论，可以用这个格式记录：

```
## [LRN-20260403-001] communication
**Logged**: 2026-04-03T09:00:00Z
**Priority**: high
**Status**: done
**Area**: config

### Summary
小金回答问题时跳步骤、不验证，是"自我纠正盲点"——LLM有能力自纠但不会主动激活

### Details
CMU研究证实（ICLR 2026）：14个主流模型平均64.5%自我错误未被纠正。解决方案：回答前加"Wait"激活审查模式。

### Suggested Action
已在 SOUL.md 加入"行为准则"四条（耐心/诚实/严谨/自检）

### Metadata
- Source: user_feedback
- Tags: behavior, response-quality
- Pattern-Key: behavior.hasty-response
```

---

## 常见问题

**Q：记录太多会很乱吗？**
A：有 Priority + Status + Area 多维索引，支持搜索，不会有这个问题。

**Q：谁来触发记录？**
A：小金每次被纠正时自动记录，不需要金哥提醒。

**Q：和 MEMORY.md 有什么区别？**
A：MEMORY.md 是长期记忆，`.learnings/` 是结构化的改进日志，专门用于追踪教训和错误，有 promotion 机制。
