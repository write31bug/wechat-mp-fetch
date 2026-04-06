# Claude Code 源码深度学习 - 阶段一：架构与核心链路

> 学习日期：2026-03-31 | 基于泄露源码 v2026-03-31

---

## 一、启动流程深度解析

### 1.1 模块加载前的副作用（Side Effects）

```typescript
// main.tsx — 在任何模块 import 之前就触发
profileCheckpoint('main_tsx_entry');        // 记录入口时间戳
startMdmRawRead();                          // 触发 MDM 配置读取 subprocess
startKeychainPrefetch();                    // 触发 macOS Keychain 读取 subprocess
```

**设计原理**：
- `startMdmRawRead()` — 企业设备管理配置，用 subprocess 并行读取，避免阻塞主线程
- `startKeychainPrefetch()` — OAuth token 和 API Key 预读取，同样用 subprocess 并行
- 如果不预取，这些操作会在 `applySafeConfigEnvironmentVariables()` 中同步执行，每次启动多花 ~65ms

**性能优化关键**：
> 把原本串行的 I/O 操作，通过提前触发 subprocess 实现"伪并行"，在模块加载的 ~135ms 窗口内完成 I/O。

### 1.2 启动检查点分析（Startup Profiler）

```typescript
// startupProfiler.ts — 内置性能分析工具
const DETAILED_PROFILING = CLAUDE_CODE_PROFILE_STARTUP=1
const STATSIG_SAMPLING = 0.5% external / 100% internal

// 关键阶段定义
const PHASE_DEFINITIONS = {
  import_time:    ['cli_entry', 'main_tsx_imports_loaded'],
  init_time:      ['init_function_start', 'init_function_end'],
  settings_time:  ['eagerLoadSettings_start', 'eagerLoadSettings_end'],
  total_time:     ['cli_entry', 'main_after_run'],
}
```

**关键洞察**：采样率控制 + 环境变量开关，冷用户不付任何性能开销。

### 1.3 初始化流程（init.ts）

```typescript
// 初始化顺序（关键路径）
enableConfigs()                              // 启用配置系统
  → applySafeConfigEnvironmentVariables()   // 应用安全环境变量（TLS cert 前）
  → setupGracefulShutdown()                 // 注册退出处理
  → initializeTelemetry()                   // 懒加载 OpenTelemetry (~400KB)
  → initializeLspServerManager()             // LSP 服务管理
  → initializeRemoteManagedSettings()        // 企业远程设置
  → initializePolicyLimits()                 // 组织策略限制
  → preconnectAnthropicApi()                 // API 预连接
```

**关键洞察**：
1. TLS cert 配置在第一个 TLS 握手**之前**就应用了（Bun/BoringSSL 会缓存 cert store）
2. OpenTelemetry 懒加载，通过 `import()` 动态导入，不在主路径上
3. 远程设置和企业策略是并行加载的

---

## 二、QueryEngine 核心循环解析

### 2.1 整体架构

```
用户输入
    ↓
processUserInput()      ← 处理 slash 命令、附件、上下文构建
    ↓
submitMessage()         ← QueryEngine 的公开入口
    ↓
fetchSystemPrompt()     ← 获取系统提示（模型相关）
    ↓
query() *               ← AsyncGenerator，核心循环
    ↓
API Streaming           ← Anthropic API 调用
    ↓
┌→ tool_use block? → runTools() → 追加结果 → 继续循环
└→ text block?      → yield 给调用方 → 循环直到 stop_reason
```

### 2.2 submitMessage 关键职责

```typescript
async *submitMessage(prompt, options) {
  // 1. 构建 ProcessUserInputContext（上下文构建器）
  const processUserInputContext = {
    messages: [],              // 对话历史
    options: {
      tools,                   // 可用工具列表
      commands,                // 可用命令
      mainLoopModel,           // 当前模型
      thinkingConfig,           // Thinking 模式配置
      mcpClients,              // MCP 客户端
    },
    getAppState, setAppState,  // 状态读写
    abortController,            // 中断控制
    // ...更多上下文
  }

  // 2. 处理用户输入（slash 命令、附件）
  const { messages, shouldQuery } = await processUserInput({...})

  // 3. 预取 Skills 和 Plugins（cache-only，不阻塞）
  const [skills, { enabled: enabledPlugins }] = await Promise.all([
    getSlashCommandToolSkills(cwd),
    loadAllPluginsCacheOnly(),
  ])

  // 4. 进入 query 循环
  for await (const message of query({ messages, systemPrompt, ... })) {
    yield message  // 实时 yield 给调用方
  }
}
```

### 2.3 query() 循环状态机

```typescript
// queryLoop — 核心循环
while (true) {
  // 1. yield stream_request_start
  yield { type: 'stream_request_start' }

  // 2. API 调用：messages → streaming response
  for await (const event of api.stream({ messages, systemPrompt })) {
    if (event.type === 'content_block') {
      if (event.content.type === 'tool_use') {
        // 收集 tool calls
        toolUseBlocks.push(event.content)
      }
      if (event.content.type === 'text') {
        // yield 实时文本片段
        yield event
      }
    }
    if (event.type === 'message_delta' && event.delta.stop_reason) {
      stopReason = event.delta.stop_reason
    }
  }

  // 3. 执行工具（如果有必要）
  if (toolUseBlocks.length > 0) {
    for await (const update of runTools(toolUseBlocks, ...)) {
      yield update  // yield 工具执行进度
    }
    // 追加工具结果到 messages
    messages.push(...toolResults)
    continue  // 继续下一次循环
  }

  // 4. 循环结束，yield 最终结果
  yield { type: 'result', stop_reason: stopReason, ... }
  break
}
```

### 2.4 工具并发执行策略

```typescript
// toolOrchestration.ts — 工具执行编排
export async function* runTools(...) {
  // 关键：按"是否并发安全"对工具调用分组
  for (const { isConcurrencySafe, blocks } of partitionToolCalls(...)) {
    if (isConcurrencySafe) {
      // 并发执行：只读工具（Read/Grep/WebFetch）
      yield* runToolsConcurrently(blocks, ...)
    } else {
      // 串行执行：写操作工具（Write/Edit/Bash）
      yield* runToolsSerially(blocks, ...)
    }
  }
}

// 读写分类原则
const isConcurrencySafe = (
  tool.permission.mode === 'read' ||
  tool.permission.mode === 'read_without_execution'
)
```

**并发优化**：多个只读工具（如 Read+Grep+WebFetch）可以并发执行，互不影响。

---

## 三、Tool 系统架构

### 3.1 工具注册机制

```typescript
// tools.ts — 工具注册表
const allTools: Tools = [
  AgentTool, SkillTool, BashTool,
  FileEditTool, FileReadTool, FileWriteTool,
  GlobTool, GrepTool, WebFetchTool, WebSearchTool,
  // ... 共 ~40 个工具
]

// 条件注册（Dead Code Elimination）
const SleepTool = feature('PROACTIVE') || feature('KAIROS')
  ? require('./tools/SleepTool/SleepTool.js').SleepTool
  : null
```

### 3.2 Tool 基类设计

```typescript
// Tool.ts — 工具接口定义
interface Tool {
  name: string
  description: (input, context) => Promise<string>   // 动态描述（用于权限提示）
  inputSchema: JSONSchema                           // Zod v4 schema
  permission: {
    mode: PermissionMode
    // ...
  }

  // 核心方法
  async execute(input, context): Promise<ToolResult> {
    // 1. 验证输入
    // 2. 执行逻辑
    // 3. 返回结果
  }
}
```

### 3.3 权限系统

```typescript
// useCanUseTool.tsx — 权限检查 Hook
async function hasPermissionsToUseTool(tool, input, context, ...) {
  // 权限检查链路
  // 1. alwaysAllowRules — 白名单规则
  // 2. alwaysDenyRules  — 黑名单规则
  // 3. classifier        — 自动分类器（TRANSCRIPT_CLASSIFIER feature）
  // 4. hooks             — 自定义权限 Hook
  // 5. 用户交互确认       — 弹窗询问
}
```

**权限模式**：
| 模式 | 行为 |
|------|------|
| `default` | 首次询问用户 |
| `plan` | Plan 模式下自动绕过 |
| `bypassPermissions` | 完全跳过（CI 模式） |
| `auto` | 自动决策（分类器） |

---

## 四、状态管理

### 4.1 Store 实现（极简模式）

```typescript
// state/store.ts — 自定义 Store
type Store<T> = {
  getState: () => T
  setState: (updater: (prev: T) => T) => void
  subscribe: (listener: () => void) => () => void
}

function createStore<T>(initialState: T, onChange?): Store<T> {
  let state = initialState
  const listeners = new Set<Listener>()

  return {
    getState: () => state,
    setState: (updater) => {
      const next = updater(state)
      if (Object.is(next, state)) return  // 相同引用则跳过
      state = next
      onChange?.({ newState: next, oldState: prev })
      listeners.forEach(l => l())          // 通知所有监听者
    },
    subscribe: (listener) => {
      listeners.add(listener)
      return () => listeners.delete(listener)
    }
  }
}
```

**设计亮点**：
1. **相同引用检查**：避免不必要的 re-render
2. **订阅返回取消函数**：简化订阅管理
3. **可选的 onChange 回调**：用于日志/调试

### 4.2 AppState 结构

```typescript
// AppStateStore.ts — 全局状态
type AppState = {
  // 设置相关
  settings: SettingsJson
  mainLoopModel: ModelSetting
  verbose: boolean

  // 权限上下文
  toolPermissionContext: ToolPermissionContext

  // 状态栏/视图
  statusLineText: string | undefined
  expandedView: 'none' | 'tasks' | 'teammates'

  // 文件历史
  fileHistory: FileHistoryState

  // MCP 相关
  mcpServerConnections: MCPServerConnection[]
  mcpResources: Record<string, ServerResource[]>

  // Speculation（预测执行）
  speculation: SpeculationState

  // ... 更多
}
```

---

## 五、开发经验总结

### 5.1 工程化经验

#### 经验 1：启动优化 — Subprocess 并行 I/O

**问题**：Keychain 读取、MDM 配置等 I/O 操作会阻塞启动。

**方案**：
```typescript
// 在模块加载前就触发 subprocess
startMdmRawRead();           // 立即触发，不等待
startKeychainPrefetch();     // 立即触发，不等待
// ... 其他 135ms 的模块加载期间，这些 subprocess 在后台运行
```

**效果**：节省 ~65ms 启动时间。

#### 经验 2：懒加载大依赖

```typescript
// OpenTelemetry ~400KB，gRPC ~700KB，动态导入
const { initializeTelemetry } = await import('./telemetry/init.js')
```

**原则**：不在主路径上的依赖，一律懒加载。

#### 经验 3：Dead Code Elimination

```typescript
// Bun 特有机制
import { feature } from 'bun:bundle'

const voiceModule = feature('VOICE_MODE')
  ? require('./voice/index.js').default
  : null
```

**效果**：未启用的功能代码完全不进入产物。

#### 经验 4：循环依赖管理

```typescript
// 懒 require 打破循环
const getTeammateUtils = () => require('./utils/teammate.js')

// 或依赖注入
function getCoordinatorUserContext(
  mcpClients: ReadonlyArray<{ name: string }>,
  scratchpadDir?: string,
) { ... }
```

### 5.2 架构设计经验

#### 经验 5：AsyncGenerator 实现流式处理

```typescript
// query() 是一个 AsyncGenerator
async function* query(params): AsyncGenerator<Message | StreamEvent> {
  yield { type: 'stream_request_start' }  // 实时流式 yield

  for await (const event of api.stream()) {
    if (event.type === 'text') {
      yield event  // 实时文本片段立即 yield
    }
    if (event.type === 'tool_use') {
      // 工具调用不 yield，收集后批量执行
    }
  }
}
```

**好处**：调用方可以实时看到响应，不用等整个请求完成。

#### 经验 6：工具并发优化

```typescript
// 工具分两类：并发安全 vs 非并发安全
const CONCURRENCY_SAFE_TOOLS = new Set(['Read', 'Grep', 'WebFetch', ...])

// 只读工具并发执行
if (blocks.every(b => CONCURRENCY_SAFE_TOOLS.has(b.name))) {
  yield* runToolsConcurrently(blocks)
} else {
  yield* runToolsSerially(blocks)
}
```

#### 经验 7：Context 对象贯穿全链路

```typescript
// 每个阶段都接收 context，而不是零散参数
const processUserInputContext: ProcessUserInputContext = {
  messages,
  options: { tools, commands, model, ... },
  getAppState, setAppState,
  abortController,
  readFileState,
  // ... 所有上下文信息
}
```

**好处**：新增参数只需扩展 context，不用改函数签名。

#### 经验 8：State 不可变更新

```typescript
// always return new reference
setState(prev => {
  const next = updater(prev)
  return Object.is(next, prev) ? prev : next  // 相同则返回旧引用
})
```

### 5.3 可改进的设计

#### 改进点 1：main.tsx 过于庞大

`main.tsx` 有 4500+ 行，所有初始化逻辑堆在一起。建议按功能拆分为多个模块。

#### 改进点 2：类型声明分散

很多类型在 `types/` 和源文件之间重复导出，造成维护负担。

#### 改进点 3：条件导入的 ESLint 规则过于特殊

```typescript
/* eslint-disable custom-rules/no-top-level-side-effects */
startMdmRawRead();
/* eslint-enable custom-rules/no-top-level-side-effects */
```

为了实现 DCE，代码里充满了 eslint-disable 注释，影响代码整洁度。

---

## 六、对 OpenClaw 的优化建议

基于以上学习，对 OpenClaw 的具体优化：

### 优化 1：参考启动优化思路

```typescript
// 目前的 OpenClaw 启动是否有 I/O 阻塞？
// 考虑：配置读取、Keychain/安全存储、远程设置 等是否可并行化
```

### 优化 2：引入 Startup Profiler

参考 `startupProfiler.ts`，给 OpenClaw 增加启动阶段分析能力。

### 优化 3：工具系统参考 Claude Code 的设计

```typescript
// 当前 OpenClaw 的工具注册 vs Claude Code：
// Claude Code: 每个工具独立模块 + Zod schema + 权限模型
// OpenClaw: 可考虑增强工具的描述动态化和权限粒度控制
```

### 优化 4：状态管理优化

参考 Claude Code 的极简 Store 实现，检查 OpenClaw 的状态管理是否冗余。

### 优化 5：AsyncGenerator 流式响应

如果 OpenClaw Gateway 有类似的"长时间运行任务"，可考虑用 AsyncGenerator 实现流式 yield。

---

## 七、核心要点速记

| 概念 | 关键实现 |
|------|---------|
| 启动优化 | Subprocess 并行 + 模块懒加载 |
| QueryEngine | AsyncGenerator 流式循环 |
| 工具执行 | 读写分离 + 并发/串行策略 |
| 权限系统 | 规则引擎 + 分类器 + 交互确认 |
| 状态管理 | 极简 Store + 不可变更新 |
| DCE | `feature('FLAG')` + 条件 require |
| 循环依赖 | 懒 require + 依赖注入 |
| Profiler | 采样率控制 + 环境变量开关 |

---

_Last updated: 2026-03-31_
