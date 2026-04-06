# Claude Code 核心洞察（精简版）

> 阶段一 + 阶段二 精华沉淀 | 2026-03-31

---

## Claude Code 架构三句话

```
用户输入
    ↓
QueryEngine（AsyncGenerator 循环）→ Tool.call()
    ↓
Store 更新 → REPL 渲染
```

---

## 最重要的 3 个设计

### 1. QueryEngine = Agent 循环

- 用 **AsyncGenerator** 实现流式响应
- 循环：API 调用 → 收集 tool_use → 执行工具 → 继续
- `canUseTool` 函数注入到 Tool，不直接依赖权限模块（依赖反转）

### 2. Tool = 描述 + 执行 + 权限

```typescript
type Tool = {
  name: string
  call(args, context, canUseTool, onProgress): Promise<ToolResult>  // 执行
  description(input, options): Promise<string>  // 动态描述
  checkPermissions(input, context): Promise<PermissionResult>  // 权限
  isConcurrencySafe(input): boolean  // 并发优化
  isReadOnly(input): boolean  // 读写分类
}
```

### 3. 极简 Store（40 行）

- 手写，不用 zustand/jotai
- `Object.is(next, prev)` 避免无意义 re-render
- subscribe 返回取消函数

---

## 对 OpenClaw 有价值的

| 设计 | OpenClaw 现状 | 行动 |
|------|-------------|------|
| **动态 Tool 描述** | SKILL.md 描述是静态的 | 考虑增强 |
| **最小化 Store** | 无响应式 Store | 观察是否需要 |
| **权限抽象** | 无 | 按需引入 |

---

## 不需要抄的

- 启动优化（CLI 专属，Gateway 场景不同）
- Dead Code Elimination（Bun 特有）
- CLI UI 渲染（OpenClaw 是 Web）
- Bash 工具复杂逻辑（企业微信工具不需要）

---

## 下一步：带着这个框架看 OpenClaw

研究 OpenClaw 时要问：
1. OpenClaw 的 "QueryEngine" 在哪里？
2. OpenClaw 的 "Tool.call()" 是什么形态？
3. OpenClaw 有没有权限抽象？

---

_Last updated: 2026-03-31_
