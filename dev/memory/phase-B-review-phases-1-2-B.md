# 阶段 B 整体复盘 — 阶段一 + 阶段二 + 阶段 B

> 2026-03-31 | 连接三个阶段的知识

---

## 一、三个阶段告诉我的事

### 阶段一：架构与核心链路
- QueryEngine = AsyncGenerator Agent 循环
- Store = 40 行极简实现
- 状态管理贯穿整个生命周期

### 阶段二：Tool 系统
- Tool = 描述 + 执行 + 权限 + 分类
- 权限通过 canUseTool 函数注入（依赖反转）
- 工具分读写，只读可并发

### 阶段 B：Hook 系统
- Hook = 横切关注点的注入点
- Claude Code：Skill 级别的 Hook（4种类型）
- OpenClaw：Plugin 级别的 Hook（27个生命周期事件）

---

## 二、三个阶段串起来

### 完整架构图

```
┌─────────────────────────────────────────────────────────┐
│                    Claude Code                          │
│                                                          │
│  ┌──────────┐    ┌─────────────┐    ┌────────────────┐  │
│  │   CLI    │ → │ QueryEngine │ →  │ Tool.call()    │  │
│  │   REPL   │    │ (循环)       │    │ (工具执行)      │  │
│  └──────────┘    └──────┬──────┘    └───────┬────────┘  │
│                          │                   │            │
│                   ┌──────▼──────┐    ┌──────▼────────┐   │
│                   │  Store     │    │ canUseTool() │   │
│                   │ (状态管理)   │    │ (权限检查)    │   │
│                   └─────────────┘    └───────┬────────┘   │
│                                               │            │
│                   ┌───────────────────────────▼────────┐  │
│                   │         Hook 系统                   │  │
│                   │  PreToolUse / PostToolUse          │  │
│                   │  SessionStart / SessionEnd         │  │
│                   │  FileChanged / CwdChanged          │  │
│                   └────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                     OpenClaw                            │
│                                                          │
│  ┌──────────┐    ┌─────────────┐    ┌────────────────┐  │
│  │ Gateway  │ → │ Agent       │ →  │ Tool (RPC)     │  │
│  │ Server   │    │ Runtime     │    │ callGateway()   │  │
│  └──────────┘    └──────┬──────┘    └───────┬────────┘  │
│                          │                   │            │
│                   ┌──────▼──────┐    ┌──────▼────────┐   │
│                   │  Compaction │    │ Hook Runner   │   │
│                   │ (上下文压缩)  │    │ (Plugin Hook) │   │
│                   └─────────────┘    └───────┬────────┘   │
│                                               │            │
│  ┌───────────────────────────────────────────▼────────┐  │
│  │                  Plugin 系统                      │  │
│  │  before_model_resolve / llm_input / session_start │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 三、核心连接点

### 3.1 QueryEngine ↔ Tool ↔ Hook

```
QueryEngine.query() 循环
    ↓
API 返回 tool_use
    ↓
canUseTool() 权限检查（Tool 系统）
    ↓
Tool.call() 执行
    ↓
Hook: before_tool_call / after_tool_call
    ↓
Store 更新
    ↓
REPL 渲染
```

### 3.2 OpenClaw 的对应关系

```
Agent Runtime (runEmbeddedPiAgent)
    ↓
Hook: before_agent_start
    ↓
Hook: before_model_resolve
    ↓
Hook: before_prompt_build
    ↓
Hook: llm_input
    ↓
API 调用
    ↓
Hook: llm_output
    ↓
Tool 调用 (callGateway RPC)
    ↓
Hook: before_tool_call / after_tool_call
    ↓
Compaction (上下文压缩)
    ↓
Hook: before_compaction / after_compaction
```

---

## 四、Claude Code vs OpenClaw 的真正差距

### 4.1 架构层面的差距

| 维度 | Claude Code | OpenClaw | 结论 |
|------|------------|----------|------|
| **架构** | 单体 CLI | 分布式 Gateway | 各有优劣 |
| **Tool 执行** | 原生 call() | RPC 调用 | Claude Code 更快 |
| **Hook 机制** | Skill 级别 | 生命周期级别 | OpenClaw 更完整 |
| **上下文管理** | 手动 /context | 自动 Compaction | OpenClaw 更智能 |
| **权限模型** | 四级模式 | 无 | Claude Code 更细 |

### 4.2 OpenClaw 比 Claude Code 强的地方

1. **Compaction**：自动上下文压缩，Claude Code 没有
2. **Hook 生命周期**：覆盖完整的 Agent + Gateway + Session 周期
3. **Plugin 系统**：模块化扩展，Claude Code 没有
4. **Channel 系统**：多渠道消息接入，Claude Code 没有

### 4.3 Claude Code 比 OpenClaw 强的地方

1. **Tool 原生执行**：无 RPC 开销
2. **动态 Tool 描述**：description 是函数
3. **权限模型**：细粒度权限控制
4. **极简设计**：代码量少，容易理解

---

## 五、真正的落地方向

### 5.1 OpenClaw 现状总结

| 能力 | 现状 | 是否需要增强 |
|------|------|------------|
| Tool 系统 | wecom_mcp RPC | ❌ 足够 |
| Hook 系统 | 27 个生命周期 hook | ✅ 已经很强 |
| 权限模型 | 无细粒度抽象 | 🟡 按需 |
| 上下文管理 | Compaction | ✅ 已经很强 |
| 状态管理 | 模块级 | 🟡 观察是否需要 |

### 5.2 下一步行动

**短期（1-2 周）**：
- 继续学习 OpenClaw 的 Compaction 机制（阶段 C）
- 这是 Claude Code 没有的独特价值

**中期（1 个月）**：
- 研究 OpenClaw 的 Plugin SDK
- 这是 OpenClaw 的扩展能力核心

**长期（季度）**：
- 如果需要细粒度权限控制，参考 Claude Code 的模式
- 如果需要动态 Tool 描述，增强 SKILL.md 格式

---

## 六、我的新认知

### 6.1 不要比较"谁更好"，要理解"各自为什么这样设计"

Claude Code 是单体 CLI，设计选择是"简单、高性能"。
OpenClaw 是分布式 Gateway，设计选择是"可扩展、可运维"。

不能拿 Claude Code 的设计去套 OpenClaw，也不能拿 OpenClaw 的设计去套 Claude Code。

### 6.2 OpenClaw 的 Hook 系统是真正的强项

OpenClaw 的 27 个生命周期 Hook + Plugin 系统，是 Claude Code 完全不具备的能力。

这是 OpenClaw 作为平台的核心竞争力。

### 6.3 下一步学习的价值排序

1. **阶段 C：Compaction**（Claude Code 没有的）
2. **阶段 D：Plugin SDK**（OpenClaw 的扩展核心）
3. **阶段 E：权限模型**（Claude Code 的强项）

---

_Last updated: 2026-03-31_
