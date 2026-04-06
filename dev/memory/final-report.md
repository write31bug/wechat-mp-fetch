# Claude Code × OpenClaw 研究 — 最终沉淀报告

> 研究时间：2026-03-31 | 研究人：开发助手

---

## 一、核心结论

### 1.1 Claude Code 是什么？

**单用途 CLI 编码工具**

```
CLI（REPL）
    ↓
QueryEngine（AsyncGenerator Agent 循环）
    ↓
Tool.call()（原生执行，~40个工具）
    ↓
Skill Hook（@before_write 等，Skill 级别）
    ↓
手动 /context 上下文管理
```

**特点**：简单、直接、高性能、无平台扩展性

---

### 1.2 OpenClaw 是什么？

**分布式 AI Gateway 平台**

```
Gateway Server（HTTP/WS）
    ↓
Plugin Registry（Plugin SDK）
    ↓
Agent Runtime（runEmbeddedPiAgent）
    ↓
callGateway()（RPC 调用 Tool）
    ↓
Hook 系统（30+ 生命周期 Hook）
    ↓
Compaction（自动摘要）
```

**特点**：可扩展、可运维、多渠道、智能上下文管理

---

## 二、架构全对比

### 2.1 核心链路对比

```
Claude Code：
用户输入 → QueryEngine 循环 → Tool.call() → Skill Hook

OpenClaw：
消息 → Hook(message_received)
     → Hook(before_dispatch)
     → Hook(before_model_resolve)
     → Agent Runtime
     → API 调用
     → Tool 调用 (RPC)
     → Hook(before/after_tool_call)
     → Compaction（自动）
     → Hook(before/after_compaction)
     → Hook(session_end)
```

### 2.2 各维度对比

| 维度 | Claude Code | OpenClaw | 胜出 |
|------|------------|----------|------|
| **架构** | 单体 CLI | 分布式 Gateway | OpenClaw |
| **Tool 执行** | 原生 call()，无 RPC | RPC 调用 | Claude Code（快） |
| **Tool 描述** | 动态函数 | 静态字符串 | Claude Code |
| **Hook 系统** | Skill 级别（4种） | 30+ 生命周期 | **OpenClaw** |
| **Compaction** | 手动截断 | 自动摘要 | **OpenClaw** |
| **Plugin 系统** | ❌ 无 | 完整 SDK | **OpenClaw** |
| **Channel** | ❌ 无 | 10+ 渠道 | **OpenClaw** |
| **权限模型** | 四级权限 | 无 | Claude Code |
| **上下文管理** | /context 手动 | 自动 | **OpenClaw** |

---

## 三、Claude Code 核心设计

### 3.1 QueryEngine（Agent 循环）

```typescript
async function* query(params): AsyncGenerator<Message> {
  while (true) {
    yield { type: 'stream_request_start' }
    
    for await (const event of api.stream({ messages })) {
      if (event.type === 'content_block') {
        if (event.content.type === 'tool_use') {
          // 收集 tool calls
          toolUseBlocks.push(event.content)
        }
        if (event.content.type === 'text') {
          yield event  // 实时 yield
        }
      }
    }
    
    if (toolUseBlocks.length > 0) {
      yield* runTools(toolUseBlocks)  // 执行工具
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

### 3.2 Tool 系统

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

**权限模式**：
- `default`：首次询问
- `plan`：Plan 模式自动允许
- `bypassPermissions`：完全跳过（CI）
- `auto`：ML 分类器自动决策

---

### 3.3 极简 Store（40 行）

```typescript
function createStore<T>(initialState: T, onChange?) {
  let state = initialState
  const listeners = new Set<Listener>()
  
  return {
    getState: () => state,
    setState: (updater) => {
      const next = updater(state)
      if (Object.is(next, prev)) return  // 相同引用，跳过
      state = next
      listeners.forEach(l => l())
    },
    subscribe: (listener) => {
      listeners.add(listener)
      return () => listeners.delete(listener)  // 返回取消函数
    }
  }
}
```

**关键点**：
- 手写，不引入 zustand/jotai
- Object.is 检查避免无意义 re-render
- subscribe 返回取消函数

---

## 四、OpenClaw 核心设计

### 4.1 Hook 系统（27 个生命周期 Hook）

```typescript
const PLUGIN_HOOK_NAMES = [
  // Gateway 生命周期
  'gateway_start', 'gateway_stop',
  // 模型选择
  'before_model_resolve', 'before_prompt_build',
  // Agent 生命周期
  'before_agent_start', 'llm_input', 'llm_output', 'agent_end',
  // 工具调用
  'before_tool_call', 'after_tool_call', 'tool_result_persist',
  // 会话生命周期
  'session_start', 'session_end',
  // 压缩
  'before_compaction', 'after_compaction',
  // 消息
  'message_received', 'message_sending', 'message_sent', 'before_message_write',
  // 子 Agent
  'subagent_spawning', 'subagent_delivery_target', 'subagent_spawned', 'subagent_ended',
  // 其他
  'before_dispatch', 'before_install', 'before_reset', 'inbound_claim',
]
```

---

### 4.2 Compaction 机制

```
Token 达到阈值
    ↓
Hook: before_compaction
    ↓
session.compact() → 生成摘要
    ↓
Hook: after_compaction
    ↓
truncateSessionAfterCompaction()
```

**特点**：
- 自动触发（budget / overflow）
- 生成摘要，比截断保留更多上下文
- before/after Hook 让过程可扩展
- Safety Timeout + Safeguard 保障

---

### 4.3 Plugin SDK

```typescript
// Plugin Manifest
{
  "id": "my-plugin",
  "name": "My Plugin",
  "channels": ["telegram"],
  "skills": ["./skills"]
}

// Plugin Entry Point
definePluginEntry({
  register(api) {
    api.registerTool({...})      // 注册工具
    api.registerChannel({...})   // 注册渠道
    api.registerHook({...})      // 注册 Hook
    api.registerCommand({...})    // 注册命令
  }
})
```

---

## 五、对 wecom-openclaw-plugin 的建议

### 5.1 当前架构

```
wecom-openclaw-plugin
    │
    ├── Channel：企业微信渠道 ✅
    │
    ├── Skills：SKILL.md 驱动（轻量）
    │
    └── MCP：通过 mcporter 集成企业微信 API
```

### 5.2 是否需要升级？

| 维度 | 当前 | 升级到 Plugin SDK | 结论 |
|------|------|-----------------|------|
| Channel | ✅ 企业微信 | 已经是最优 | ❌ 不需要 |
| Tool | MCP 调用 | api.registerTool() | ❌ 不需要 |
| Hook | 无 | api.registerHook() | 🟡 按需 |
| Provider | ❌ 无 | 不需要 | ✅ 不需要 |

**结论**：当前 SKILL.md + MCP 模式已经足够，不需要升级到完整 Plugin SDK。

### 5.3 未来可能的方向

**如果需要**：
- Hook 能力 → 使用 `api.registerHook()`
- 自定义 Tool → 使用 `api.registerTool()`

**但目前没有明确需求，不需要提前优化**。

---

## 六、最小化改进建议

### 6.1 可以考虑的改进（不紧急）

1. **SKILL.md 描述动态化**
   - 当前：静态字符串
   - Claude Code：动态函数
   - 但 OpenClaw 场景可能不需要

2. **权限模型**
   - Claude Code 有四级权限模式
   - OpenClaw 目前无
   - 如果企业微信需要细粒度权限，可以参考

### 6.2 不需要改的

- ❌ 不引入 zustand/jotai（当前模块级状态足够）
- ❌ 不升级到完整 Plugin SDK（SKILL.md 够用）
- ❌ 不做 DCE（Gateway 场景不需要）
- ❌ 不做启动优化（Gateway 不是 CLI）

---

## 七、研究产出清单

| 文档 | 内容 |
|------|------|
| `memory/claude-code-core-insights.md` | Claude Code 核心洞察（精简版） |
| `memory/claude-code-phase1-deep-study.md` | 阶段一：架构概览 |
| `memory/claude-code-phase1-summary.md` | 阶段一：总结 + 落地规划 |
| `memory/claude-code-phase2-deep-study.md` | 阶段二：Tool 系统 |
| `memory/openclaw-architecture-study.md` | OpenClaw 架构研究 |
| `memory/openclaw-vs-claude-code-summary.md` | OpenClaw vs Claude Code 对比 |
| `memory/phase-B-hooks-deep-study.md` | 阶段 B：Hook 系统 |
| `memory/phase-B-review-phases-1-2-B.md` | 阶段 B 整体复盘 |
| `memory/phase-C-compaction-deep-study.md` | 阶段 C：Compaction 机制 |
| `memory/phase-C-review-phases-1-2-B-C.md` | 阶段 C 整体复盘 |
| `memory/phase-D-plugin-sdk-deep-study.md` | 阶段 D：Plugin SDK |
| `memory/phase-D-review-all-phases.md` | 全部阶段整体复盘 |
| `memory/learning-plan-v3.md` | 学习计划 v3 |
| `memory/final-report.md` | 最终沉淀报告 |

---

## 八、核心认知

### 8.1 不要比较"谁更好"

Claude Code 是**单用途 CLI**，设计选择是"简单、高性能"。
OpenClaw 是**分布式平台**，设计选择是"可扩展、可运维"。

**架构决定设计，不能互相套用。**

### 8.2 OpenClaw 的核心优势

1. **Compaction**：自动上下文压缩，Claude Code 没有
2. **Hook 系统**：30+ 生命周期，Claude Code 只有 Skill Hook
3. **Plugin SDK**：完整扩展系统，Claude Code 没有
4. **Channel 系统**：多渠道接入，Claude Code 没有

### 8.3 Claude Code 的核心优势

1. **Tool 原生执行**：无 RPC 开销
2. **动态 Tool 描述**：description 是函数
3. **极简设计**：代码量少，容易理解
4. **四级权限模式**：细粒度权限控制

### 8.4 学习的正确方式

- ✅ 问"为什么这样设计"
- ✅ 理解"适不适合 OpenClaw"
- ✅ 架构差异大的不照搬
- ❌ 不为了"技术先进"而抄

---

## 九、金句

> **工具是死的，思路是活的。先想清楚，再写代码。**
> — SOUL.md

> **架构决定设计，不能互相套用。**
> — 这次研究的核心认知

---

_Last updated: 2026-03-31_
