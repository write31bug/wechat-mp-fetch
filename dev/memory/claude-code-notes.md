# Claude Code 学习笔记

> 基于泄露源码（2026-03-31）| 仅供研究参考

---

## 目录

1. [核心架构](#核心架构)
2. [QueryEngine](#queryengine)
3. [Tool 系统](#tool-系统)
4. [Hook 系统](#hook-系统)
5. [极简 Store](#极简-store)
6. [Claude Code vs OpenClaw](#claude-code-vs-openclaw)

---

## 核心架构

```
用户输入
    ↓
QueryEngine（AsyncGenerator 循环）
    ↓
Tool.call()（原生执行，~40个工具）
    ↓
Skill Hook（@before_write 等）
    ↓
手动 /context 上下文管理
```

---

## QueryEngine

### Agent 循环（AsyncGenerator）

```typescript
async function* query(params): AsyncGenerator<Message> {
  while (true) {
    yield { type: 'stream_request_start' }
    
    for await (const event of api.stream({ messages })) {
      if (event.type === 'content_block') {
        if (event.content.type === 'tool_use') {
          toolUseBlocks.push(event.content)
        }
        if (event.content.type === 'text') {
          yield event  // 实时 yield
        }
      }
    }
    
    if (toolUseBlocks.length > 0) {
      yield* runTools(toolUseBlocks)
      messages.push(...toolResults)
      continue
    }
    
    yield { type: 'result', stop_reason }
    break
  }
}
```

**关键点**：
- AsyncGenerator 实现流式响应
- 工具执行分读写，只读可并发
- canUseTool 通过依赖注入

---

## Tool 系统

### Tool 接口

```typescript
interface Tool {
  name: string
  description(input, options): Promise<string>  // 动态描述
  inputSchema: Input  // Zod schema
  permission: PermissionMode  // 权限模式
  checkPermissions(input, context): Promise<PermissionResult>
  isConcurrencySafe(input): boolean  // 并发优化
  isReadOnly(input): boolean  // 读写分类
  call(input, context, canUseTool, onProgress): Promise<ToolResult>
}
```

### 权限模式

| 模式 | 行为 |
|------|------|
| `default` | 首次询问，之后记住 |
| `plan` | Plan 模式自动允许 |
| `bypassPermissions` | 完全跳过（CI） |
| `auto` | ML 分类器自动决策 |

### 读写分类

```typescript
const CONCURRENCY_SAFE_TOOLS = new Set(['Read', 'Grep', 'WebFetch'])
// 只读工具并发执行，写操作工具串行执行
```

---

## Hook 系统

### Hook Events（27个）

```typescript
const HOOK_EVENTS = [
  'PreToolUse', 'PostToolUse', 'PostToolUseFailure',
  'Notification', 'UserPromptSubmit',
  'SessionStart', 'SessionEnd',
  'SubagentStart', 'SubagentStop',
  'PreCompact', 'PostCompact',
  'PermissionRequest', 'PermissionDenied',
  'Setup', 'TeammateIdle',
  'TaskCreated', 'TaskCompleted',
  'Elicitation', 'ElicitationResult',
  'ConfigChange',
  'WorktreeCreate', 'WorktreeRemove',
  'InstructionsLoaded',
  'CwdChanged', 'FileChanged',
]
```

### Hook 类型（4种）

```typescript
type HookCommand =
  | { type: 'command', command: string }     // Bash 命令
  | { type: 'prompt', prompt: string }        // LLM prompt
  | { type: 'agent', prompt: string }         // 子 Agent 验证
  | { type: 'http', url: string }             // HTTP POST
```

### Skill Hook 示例

```yaml
# SKILL.md
---
description: 我的 Skill
hooks:
  before_tool_call:
    - matcher: "Write"
      hooks:
        - type: command
          command: "echo 'before Write'"
          if: "Write(*.ts)"
---
```

---

## 极简 Store

### 40 行手写状态管理

```typescript
function createStore<T>(initialState: T, onChange?) {
  let state = initialState
  const listeners = new Set<Listener>()
  
  return {
    getState: () => state,
    setState: (updater) => {
      const next = updater(state)
      if (Object.is(next, prev)) return
      state = next
      listeners.forEach(l => l())
    },
    subscribe: (listener) => {
      listeners.add(listener)
      return () => listeners.delete(listener)
    }
  }
}
```

**关键点**：
- 手写，不引入 zustand/jotai
- Object.is 检查避免无意义 re-render
- subscribe 返回取消函数

---

## Claude Code vs OpenClaw

| 维度 | Claude Code | OpenClaw | 胜出 |
|------|------------|----------|------|
| **架构** | 单体 CLI | 分布式 Gateway | OpenClaw |
| **Tool 执行** | 原生 call() | RPC 调用 | Claude Code |
| **Hook 系统** | Skill 级别 | 30+ 生命周期 | **OpenClaw** |
| **Compaction** | 手动截断 | 自动摘要 | **OpenClaw** |
| **Plugin 系统** | ❌ 无 | 完整 SDK | **OpenClaw** |
| **权限模型** | 四级权限 | 无 | Claude Code |

### OpenClaw 的强项（Claude Code 没有的）

- Compaction（自动上下文压缩）
- Hook 系统（30+ 生命周期）
- Plugin SDK（完整扩展系统）
- Channel 系统（多渠道接入）

### Claude Code 的强项（OpenClaw 可以学的）

- 动态 Tool 描述（description 是函数）
- 极简 Store（40 行手写）
- 四级权限模式

---

## 不要抄的

- ❌ 启动优化（CLI 专属）
- ❌ Dead Code Elimination（Bun 特有）
- ❌ CLI UI 渲染（Ink + React）
- ❌ 命令分类 Set（维护负担）

---

_Last updated: 2026-03-31_
