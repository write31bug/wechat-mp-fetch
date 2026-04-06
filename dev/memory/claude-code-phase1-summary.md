# Claude Code 源码 — 阶段一总结（供下一阶段参考）

> 2026-03-31

---

## 核心架构

```
用户输入
    ↓
processUserInput()      ← 处理 slash 命令、附件、上下文构建
    ↓
submitMessage()         ← QueryEngine 入口（AsyncGenerator）
    ↓
fetchSystemPrompt()     ← 获取系统提示
    ↓
query()                 ← 核心循环（AsyncGenerator）
    ↓
API Streaming           ← Anthropic API
    ↓
runTools()             ← 工具执行（并发优化）
    ↓
循环直到完成
```

---

## 阶段一关键要点（下一阶段的基础）

### 1. 启动流程（main.tsx）
- 在 import 之前触发 subprocess（MDM + Keychain）
- 目的：并行化 I/O，节省 ~65ms
- **注**：这对 CLI 有意义，对 Web Gateway 价值有限

### 2. QueryEngine 核心循环
- AsyncGenerator 模式，实时 yield 流式响应
- 工具执行分两类：并发安全（只读）vs 串行（写操作）
- 核心方法：`submitMessage()` → `query()` → `runTools()`

### 3. 工具系统架构
- 工具注册在 `tools.ts`，~40 个工具
- 权限模式：`default` / `plan` / `bypassPermissions` / `auto`
- 每个工具有自己的 `permission.mode` + 动态 `description()`

### 4. 状态管理
- 手写 Store（40 行），不用 zustand/jotai
- `Object.is(next, prev)` 避免无意义 re-render
- `subscribe` 返回取消函数

### 5. Dead Code Elimination
- `feature('FLAG')` 条件导入
- Bun 特有，Node.js 不可用
- **注**：需要 eslint-disable 特殊注释，牺牲代码整洁度

---

## 对 OpenClaw 有价值的（按优先级）

| 优先级 | 设计 | 原因 |
|--------|------|------|
| 🔴 高 | 极简 Store 实现 | 不需要引入重量级状态库 |
| 🔴 高 | 工具权限抽象 | 声明式权限模式，skill 可声明自己的权限级别 |
| 🟡 中 | AsyncGenerator 模式 | 长时间任务可 yield 进度（文档导出等） |
| 🟡 中 | Context 贯穿全链路 | 新增参数只需扩展 context，不用改函数签名 |
| 🟢 低 | 启动优化 | CLI 专属，Gateway 场景不同 |
| 🟢 低 | 命令分类 Set | OpenClaw 工具不渲染 CLI UI |

---

## 阶段一落地规划（OpenClaw 对齐）

### OpenClaw 现状分析

**1. 状态管理**
- OpenClaw 使用**模块级状态管理**（state-manager.js）
- 管理内容：WSClient 实例、消息状态（TTL 清理）、ReqId 存储
- **不是响应式 Store**，没有订阅机制
- Claude Code 的 Store 有 `subscribe`，OpenClaw 的没有

**2. 工具系统**
- OpenClaw 使用 **SKILL.md 文档系统**
- 每个 skill 是 Markdown 文档，定义"操作"和"典型工作流"
- 通过 `wecom_mcp` MCP tool 调用
- **文档驱动**，不是代码驱动
- Claude Code 的 Tool 是 TypeScript 类，有 `execute()` 方法

**3. 权限系统**
- OpenClaw 目前**没有工具级别的权限抽象**
- wecom_mcp 的权限依赖 MCP 协议本身
- Claude Code 有 `default/plan/bypassPermissions/auto` 四级权限模式

### 差距在哪里

| 维度 | OpenClaw | Claude Code | 差距 |
|------|----------|------------|------|
| 状态管理 | 模块级，无订阅 | 响应式 Store，有 subscribe | ❌ 无响应式 |
| 工具定义 | SKILL.md 文档 | Tool.ts 接口+类 | ❌ 无代码级别定义 |
| 工具描述 | 静态字符串 | 动态函数 | ❌ 描述不可变 |
| 权限模型 | 无 | 四级权限模式 | ❌ 无权限抽象 |
| 执行机制 | MCP 调用 | 原生 execute() | ❌ 无原生执行层 |

### 下一步行动

**短期（1-2 周）**
- [ ] 不需要引入 zustand/jotai，先用现有模块级状态管理
- [ ] 观察 OpenClaw 的状态管理是否真的需要响应式

**中期（1 个月）**
- [ ] 考虑 Skill 系统是否需要升级为"代码级工具定义"
- [ ] 权限模型是否需要增强？

**长期（季度）**
- [ ] 如果 OpenClaw 扩展到多工具协同，可能需要 Claude Code 的 Tool 架构

### 与阶段二（Tool 系统）的连接点

阶段二会深入学 Claude Code 的 Tool 系统，包括：
- Tool 基类设计
- 工具注册机制
- 权限检查链
- 工具编排

这些和阶段一学到的"状态管理"、"QueryEngine 循环"会串起来，帮助理解 Claude Code 的整体架构。

---

## 下一阶段学习重点

**阶段二：Tool 系统与权限系统**

要深入看的文件：
- `src/Tool.ts` — 工具基类定义
- `src/tools.ts` — 工具注册机制
- `src/hooks/useCanUseTool.tsx` — 权限检查核心
- `src/tools/BashTool/BashTool.tsx` — 典型工具实现参考
- `src/services/tools/toolOrchestration.ts` — 工具执行编排
- `src/utils/permissions/permissions.ts` — 权限规则引擎

---

## 阶段一发现的问题（待验证）

- main.tsx 4500+ 行 — 耦合太紧，是否有循环依赖？
- 条件导入的 eslint-disable 满天飞 — DCE 代价
- 命令分类 Set 手动维护负担

---

## 我的改进承诺

- ✅ 停止"快速扫描"，先问"为什么"
- ✅ 先想"适不适合 OpenClaw"，再决定是否参考
- ✅ 下一阶段带着问题学

---

_Last updated: 2026-03-31_
