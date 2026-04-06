# 阶段 C 整体复盘 — 阶段一 + 阶段二 + 阶段 B + 阶段 C

> 2026-03-31 | 连接四个阶段的知识

---

## 一、四个阶段告诉我的事

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

### 阶段 C：Compaction
- Claude Code：手动 /context，无自动 compaction
- OpenClaw：自动 Compaction + Hook + 摘要生成
- 这是 OpenClaw 比 Claude Code 强的独特价值

---

## 二、四个阶段串起来

### OpenClaw Agent Runtime 完整链路

```
用户消息
    ↓
Hook: message_received
    ↓
Hook: before_dispatch
    ↓
Hook: before_model_resolve
    ↓
Hook: before_prompt_build
    ↓
Hook: before_agent_start
    ↓
Hook: llm_input
    ↓
Agent Runtime (runEmbeddedPiAgent)
    ↓
API 调用（QueryEngine 循环）
    ↓
Hook: llm_output
    ↓
Tool 调用 (callGateway RPC)
    ↓
Hook: before_tool_call
    ↓
Tool 执行
    ↓
Hook: after_tool_call
    ↓
Compaction 检查（token 达到阈值？）
    ↓
Hook: before_compaction
    ↓
session.compact() → 生成摘要
    ↓
Hook: after_compaction
    ↓
Hook: session_end
    ↓
Hook: message_sent
```

### Claude Code 的对应链路

```
用户输入
    ↓
QueryEngine 循环
    ↓
Tool.call()
    ↓
Hook: PreToolUse / PostToolUse
    ↓
手动 /context 命令（无自动 compaction）
```

---

## 三、Claude Code vs OpenClaw 完整对比

### 架构差异

| 维度 | Claude Code | OpenClaw |
|------|------------|----------|
| **架构** | 单体 CLI | 分布式 Gateway |
| **Agent 循环** | QueryEngine (AsyncGenerator) | runEmbeddedPiAgent (Promise) |
| **Tool 执行** | 原生 call() | RPC 调用 |
| **Hook 系统** | Skill 级别 | 完整生命周期 |
| **Compaction** | 手动截断 | 自动摘要 |
| **上下文管理** | 用户手动 | 自动 + 可配置阈值 |

### OpenClaw 比 Claude Code 强的地方

1. **Compaction**：自动摘要，比 Claude Code 的手动截断更智能
2. **Hook 生命周期**：覆盖完整，比 Claude Code 的 Skill Hook 更完整
3. **Gateway 架构**：支持多渠道，比 Claude Code 的 CLI 更通用
4. **Plugin 系统**：模块化扩展，比 Claude Code 的 Skill 更强大

### Claude Code 比 OpenClaw 强的地方

1. **Tool 原生执行**：无 RPC 开销
2. **动态 Tool 描述**：description 是函数
3. **极简设计**：代码量少，容易理解

---

## 四、我的新认知

### 4.1 OpenClaw 的 Compaction 是真正的差异化能力

Claude Code 完全**没有**自动 Compaction，这是 OpenClaw 作为平台的核心竞争力之一。

对于长会话、多渠道的企业场景，自动 Compaction 是必需的。

### 4.2 Hook 系统贯穿整个生命周期

从 message_received 到 session_end，Hook 覆盖了完整的生命周期。

这是 OpenClaw 作为平台的核心能力：让插件可以在任何阶段干预。

### 4.3 架构决定设计

Claude Code 是单体 CLI，设计选择是"简单、高性能"。
OpenClaw 是分布式 Gateway，设计选择是"可扩展、可运维"。

---

## 五、继续学习的价值排序

### 阶段 D：Plugin SDK（🔴 优先）

**为什么**：
- Plugin SDK 是 OpenClaw 的扩展核心
- Hook 系统通过 Plugin 注册
- Compaction 是 Plugin Hook 的一部分

### 阶段 E：权限模型（🟡 按需）

**为什么**：
- Claude Code 有四级权限模式
- OpenClaw 目前没有细粒度权限抽象
- 如果企业微信需要权限控制，可以参考

---

## 六、我的下一步

1. **更新学习计划**，加入阶段 C 的结论
2. **继续学习阶段 D：Plugin SDK**
3. **写阶段 C 的落地规划**

---

_Last updated: 2026-03-31_
