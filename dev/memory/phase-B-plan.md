# 阶段 B：Hook 系统对比 — 详细规划

> 2026-03-31

---

## 目标

**理解两者的 Hook 机制差异，找出 OpenClaw 可借鉴的点。**

---

## Claude Code Hooks（Skill 级别）

### 要看的文件

1. **Skill Hook 核心**
   - `src/skills/hooks/` — Skill Hook 定义
   - `src/hooks/toolPermission/` — 权限 hook

2. **Hook 执行机制**
   - `src/tools/SkillTool/` — Skill 如何触发 hook
   - `src/query.ts` — hook 在 query 中的位置

### 关键问题

- Skill Hook 有哪些类型？（`@before_write`、`@after_task`、`@on_error`）
- hook 是怎么注册和触发的？
- hook 和 Tool 执行的关系是什么？

---

## OpenClaw Hooks（30+ 生命周期 hook）

### 要看的文件

1. **Hook 类型定义**
   - `src/plugins/hooks.ts` — 所有 hook 类型（重点！）
   - `src/plugins/types.ts` — hook 上下文类型

2. **Hook 执行机制**
   - `src/plugins/hook-runner-global.ts` — 全局 hook runner
   - `src/plugins/hooks.ts` — hook 注册和执行

3. **具体 Hook 实现**
   - `before_tool_call` — 工具调用前
   - `after_tool_call` — 工具调用后
   - `llm_input` / `llm_output` — LLM 输入输出
   - `session_start` / `session_end` — 会话生命周期

### 关键问题

- OpenClaw 有多少种 hook？覆盖哪些阶段？
- hook 是怎么注册的？（Plugin 注册 vs 配置文件）
- hook 的执行顺序是什么？（优先级）

---

## 对比分析

### Hook 覆盖阶段对比

| 阶段 | Claude Code | OpenClaw |
|------|------------|----------|
| Agent 启动前 | ❌ | ✅ `before_agent_start` |
| 模型选择前 | ❌ | ✅ `before_model_resolve` |
| Prompt 构建前 | ❌ | ✅ `before_prompt_build` |
| LLM 输入 | ❌ | ✅ `llm_input` |
| LLM 输出 | ❌ | ✅ `llm_output` |
| 工具调用前 | ✅ Skill hook | ✅ `before_tool_call` |
| 工具调用后 | ✅ Skill hook | ✅ `after_tool_call` |
| 会话开始 | ❌ | ✅ `session_start` |
| 会话结束 | ❌ | ✅ `session_end` |
| 消息收到 | ❌ | ✅ `message_received` |
| 消息发送 | ❌ | ✅ `message_sending` |
| Compaction 前/后 | ❌ | ✅ `before_compaction` / `after_compaction` |

**结论**：OpenClaw 的 Hook 覆盖了完整的生命周期，Claude Code 只有 Skill 级别的 hook。

---

## 产出目标

### 1. Hook 地图

输出一个表格，列出：
- 所有 OpenClaw Hook
- 每个 Hook 的触发时机
- 每个 Hook 的用途

### 2. 差距分析

- Claude Code 的 Skill Hook 在 OpenClaw 怎么实现？
- OpenClaw 的 Hook 系统是否足够？
- 有没有需要新增的 Hook？

### 3. 落地建议

- 短期（1-2周）：OpenClaw Hook 系统有没有明显缺失？
- 中期（1个月）：Claude Code 的 Skill Hook 模式能否迁移？
- 长期（季度）：Hook 系统需要什么增强？

---

## 执行步骤

### 步骤 1：研究 Claude Code Skill Hook（1小时）
- 读 `src/skills/hooks/` 目录
- 理解 `@before_write`、`@after_task`、`@on_error` 的实现

### 步骤 2：研究 OpenClaw Hook 系统（2小时）
- 读 `src/plugins/hooks.ts` 全部 hook 类型
- 读 `src/plugins/hook-runner-global.ts` 执行机制
- 读几个具体的 hook 实现（如 `before_tool_call`）

### 步骤 3：对比分析（1小时）
- 列出差异
- 分析 OpenClaw Hook 够不够
- 提出改进建议

### 步骤 4：复盘（30分钟）
- 写阶段 B 落地规划
- 回答"OpenClaw 有没有？怎么改？"

---

## 时间估算

- 步骤 1-4：约 4-5 小时
- 核心产出：Hook 地图 + 差距分析 + 落地建议

---

_Last updated: 2026-03-31_
