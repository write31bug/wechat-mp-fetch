# Claude Code 源码 — 阶段一 + 阶段二 整体复盘

> 2026-03-31 | 连接新旧知识

---

## 一、两个阶段告诉我的事

### 阶段一：架构与主流程
- **核心**：QueryEngine 的 AsyncGenerator 循环
- **状态**：极简 Store（40 行）
- **启动**：subprocess 并行 I/O

### 阶段二：Tool 系统
- **核心**：Tool 接口（~30 个属性/方法）
- **权限**：四级模式 + 规则引擎
- **注册**：Feature Flag 条件注册

---

## 二、把两个阶段串起来

### 完整调用链

```
用户输入
    ↓
QueryEngine.submitMessage()（阶段一）
    ↓
创建 ToolUseContext（阶段二：工具在 context 里）
    ↓
fetchSystemPrompt()（系统提示包含可用工具）
    ↓
query() 循环（阶段一）
    ↓
┌→ API 返回 tool_use block
│       ↓
│   canUseTool()（阶段二：权限检查）
│       ↓
│   Tool.call()（阶段二：工具执行）
│       ↓
│   Store 更新（阶段一：状态管理）
│       ↓
│   继续循环
└→ API 返回 text block → 结束
```

**关键连接点**：

1. **Tool 在 QueryEngine 里不是独立存在的**
   - QueryEngine 持有 `canUseTool` 函数（来自 useCanUseTool hook）
   - QueryEngine 把 `canUseTool` 和 `context` 传给 Tool.call()
   - 工具的权限检查依赖 QueryEngine 注入的函数

2. **状态在工具执行时更新**
   - 工具执行后，`setAppState()` 被调用
   - Store 的 listeners 被通知
   - REPL 重新渲染

3. **ToolUseContext 贯穿全程**
   - 阶段一学的 context 模式
   - 阶段二学的 Tool 接口
   - 两者结合：context 是工具执行的上下文

---

## 三、Claude Code 的分层架构

```
┌─────────────────────────────────────┐
│         REPL（UI 层）               │
│  React + Ink 终端 UI                │
└──────────────┬──────────────────────┘
               │ useCanUseTool()
┌──────────────▼──────────────────────┐
│      QueryEngine（逻辑层）           │
│  AsyncGenerator 循环                │
│  持有 canUseTool, context           │
└──────────────┬──────────────────────┘
               │ Tool.call()
┌──────────────▼──────────────────────┐
│         Tool（工具层）               │
│  Bash / Read / Edit / Agent 等      │
│  ~40 个工具，各自实现 call()        │
└──────────────┬──────────────────────┘
               │ MCP / LSP / Bash
┌──────────────▼──────────────────────┐
│       外部服务（集成层）             │
│  Anthropic API / 文件系统 / LSP     │
└─────────────────────────────────────┘
```

**层级职责**：
- **UI 层**：渲染、用户交互
- **逻辑层**：Agent 循环、权限协调
- **工具层**：具体操作实现
- **集成层**：外部系统对接

---

## 四、对 OpenClaw 的差距分析

### 4.1 架构对比

| 层级 | Claude Code | OpenClaw |
|------|-------------|----------|
| UI 层 | Ink + React CLI | WebChat |
| 逻辑层 | QueryEngine | ? |
| 工具层 | Tool.ts 类 | SKILL.md + wecom_mcp |
| 集成层 | MCP / LSP / Bash | 企业微信 API |

**问题**：OpenClaw 的"逻辑层"是什么？

我还不清楚 OpenClaw Gateway 的架构。需要看：
- 消息从 WebChat 到 skill 执行的完整链路
- 状态在哪里管理
- 权限在哪里检查

### 4.2 状态管理对比

| 维度 | Claude Code | OpenClaw |
|------|-------------|----------|
| 状态位置 | AppStateStore | state-manager.js |
| 响应式 | Store 有 subscribe | 模块级，无订阅 |
| 工具状态 | 在 AppState 里 | 不清楚 |

### 4.3 工具系统对比

| 维度 | Claude Code | OpenClaw |
|------|-------------|----------|
| 工具定义 | Tool.ts 接口 | SKILL.md 文档 |
| 描述 | 动态函数 | 静态字符串 |
| 输入验证 | validateInput() | 无 |
| 权限 | 四级 + 规则引擎 | 无 |
| 注册 | Feature Flag | MCP 配置 |
| 执行 | 原生 call() | wecom_mcp RPC |

---

## 五、真正的差距在哪里？

### 5.1 最需要搞清楚的问题

**OpenClaw Gateway 的架构是什么？**
- 消息从 WebChat 到 skill 执行的完整链路？
- 状态管理在哪里？state-manager.js 是全部吗？
- 权限检查在哪里？还是没有？

### 5.2 短期能做的事

**1. 理解 OpenClaw 的架构**
- 需要看 Gateway 的源码才能对比
- 阶段三、四学到的内容才能真正落地

**2. 增强 SKILL.md 的描述**
- 当前描述是静态的
- 可以考虑支持动态参数
- 但要看 SKILL.md 是怎么被解析的

### 5.3 不能做的事

**1. 不需要把 SKILL.md 改成 Tool.ts**
- 成本太高，收益不明显
- OpenClaw 的工具在 MCP 服务端，不在本地

**2. 不需要引入权限规则引擎**
- 企业微信 API 本身有权限控制
- OpenClaw 不需要再包装一层

**3. 不需要 DCE / Feature Flag**
- OpenClaw 不是 CLI，没有 bundle size 问题

---

## 六、阶段三要学什么

**Hooks 自动化规则引擎**

问题：
- Claude Code 的 hooks 是什么？
- 是在 Tool 执行前后插入逻辑吗？
- 对 OpenClaw 有没有价值？

---

## 七、我的新认知

### 7.1 不要抄"是什么"，要理解"为什么"

Claude Code 的 Tool 有 30 个方法，不是"因为好"才这么设计。
是因为 Claude Code 需要：
- CLI UI 显示（isSearchOrReadCommand 等）
- 细粒度权限控制
- 并发优化
- 动态描述

OpenClaw 不需要这些，就不需要抄。

### 7.2 差距分析要基于完整理解

没有完整理解 OpenClaw 的架构，对比是没有意义的。

我现在只知道：
- OpenClaw 有 wecom_mcp 工具调用
- OpenClaw 有 SKILL.md 文档
- OpenClaw 有 state-manager.js

但完整链路是什么，我还不清楚。

### 7.3 下一步

需要搞清楚 OpenClaw Gateway 的整体架构，才能做真正有价值的差距分析。

---

_Last updated: 2026-03-31_
