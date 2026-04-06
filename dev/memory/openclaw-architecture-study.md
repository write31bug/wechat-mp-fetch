# OpenClaw 架构研究报告

> 研究日期：2026-03-31 | 基于官方源码

---

## 一、OpenClaw 是什么？

```
OpenClaw = AI Gateway + Agent Runtime + Channel Plugins + Tool System
```

**定位**：通用 AI 助手平台，运行在用户的设备上，通过各种 Channel（消息渠道）与用户交互。

---

## 二、架构概览

### 核心组件

| 组件 | 源码位置 | 作用 |
|------|---------|------|
| **Gateway** | `src/gateway/` | HTTP/WS 服务端，处理节点连接、认证、路由 |
| **Agent Runtime** | `src/agents/pi-embedded-runner/` | Agent 执行引擎（大模型调用循环） |
| **Plugins** | `src/plugins/` | 插件系统（Provider、Channel、Hook） |
| **Channels** | `src/channels/` + 插件 | 消息渠道（Telegram、Discord、Slack 等） |
| **Tools** | `src/agents/tools/` | 内置工具（send、web-fetch、canvas 等） |
| **Skills** | `src/agents/skills/` | Skill 系统（文档驱动的工作流） |
| **MCP** | `src/mcp/` | Model Context Protocol 集成 |

### 层级关系

```
┌─────────────────────────────────────────┐
│         Gateway Server                  │
│   HTTP/WS + 认证 + 路由 + 协议           │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Plugin System                   │
│   Hooks + Provider + Channel            │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│       Agent Runtime                      │
│   runEmbeddedPiAgent()  ← 等于 QueryEngine │
│   Tool 执行 + 上下文管理 + Compaction     │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Tools + Skills                  │
│   内置工具 + MCP 工具 + SKILL 文档       │
└─────────────────────────────────────────┘
```

---

## 三、Agent Runtime（核心链路）

### 3.1 等于 Claude Code QueryEngine 的部分

```typescript
// src/agents/pi-embedded-runner/run.ts
export async function runEmbeddedPiAgent(
  params: RunEmbeddedPiAgentParams,
): Promise<EmbeddedPiRunResult> {
  // 1. 解析配置
  const { model, authStorage } = await resolveModelAsync(provider, modelId, ...)

  // 2. 解析 Hook 选择（Hook 系统）
  const hookSelection = await resolveHookModelSelection({...})
  provider = hookSelection.provider
  modelId = hookSelection.modelId

  // 3. 构建 Payload
  const payloads = await buildEmbeddedRunPayloads({...})

  // 4. 调用模型（循环）
  for await (const event of streamModel({...})) {
    // 处理 text / tool_use 事件
  }

  // 5. 执行工具（Tool 系统）
  // 6. Compaction（上下文压缩）
}
```

### 3.2 OpenClaw vs Claude Code

| 维度 | Claude Code | OpenClaw |
|------|------------|----------|
| 核心循环 | `QueryEngine.query()` AsyncGenerator | `runEmbeddedPiAgent()` Promise |
| 工具调用 | `Tool.call()` 原生方法 | `callGateway()` RPC 调用 |
| 流式处理 | AsyncGenerator yield | for await 迭代器 |
| 上下文管理 | 手动 | Compaction 自动压缩 |

---

## 四、Tool 系统

### 4.1 架构差异巨大

**Claude Code**：Tool 是 TypeScript 类
```typescript
class BashTool {
  name = 'Bash'
  call(input, context, canUseTool, onProgress): Promise<ToolResult>
  description(input): string
}
```

**OpenClaw**：Tool 是通过 Gateway RPC 调用的
```typescript
// src/agents/tools/agent-step.ts
async function runAgentStep(params) {
  const response = await callGateway({
    method: "agent",
    params: { message: params.message, ... }
  })
}
```

**核心区别**：
- Claude Code 的工具在**同一个进程**里执行
- OpenClaw 的工具通过 **Gateway RPC** 调用，属于**分布式架构**

### 4.2 工具类型

| 类型 | 示例 | 调用方式 |
|------|------|---------|
| 内置工具 | send、web-fetch、web-search | 编译进 binary |
| MCP 工具 | wecom_mcp | `src/mcp/` |
| Channel 工具 | telegram_send | Plugin 提供 |
| Skill 工具 | Bash、Read | Skill 系统 |

### 4.3 工具注册

```typescript
// src/agents/pi-tools.ts
function createTools(params) {
  return [
    createExecTool(...),      // Bash
    createReadTool(...),      // Read
    createApplyPatchTool(...), // Edit
    createOpenClawTools(...), // send, web-fetch, etc.
  ]
}
```

---

## 五、Hook 系统（亮点！）

### 5.1 OpenClaw 有强大的 Hook 系统

```typescript
// src/plugins/hooks.ts
export type PluginHookName =
  | "before_agent_start"    // Agent 启动前
  | "after_tool_call"       // 工具调用后
  | "before_tool_call"      // 工具调用前
  | "before_prompt_build"   // Prompt 构建前
  | "before_model_resolve"  // 模型选择前
  | "llm_input"             // LLM 输入
  | "llm_output"            // LLM 输出
  | "session_start"         // 会话开始
  | "session_end"           // 会话结束
  | "message_received"      // 消息收到
  | "message_sending"       // 消息发送
  // ... 共 30+ 个 hook 点
```

### 5.2 Claude Code 的 Hooks

Claude Code 有：
- `@before_write` / `@after_task` 等 Skill 级别 hook
- 但**没有** OpenClaw 这么完整的生命周期 hook

### 5.3 对比

| Hook 阶段 | Claude Code | OpenClaw |
|-----------|------------|----------|
| 模型选择前 | ❌ | ✅ `before_model_resolve` |
| Prompt 构建前 | ❌ | ✅ `before_prompt_build` |
| LLM 输入/输出 | ❌ | ✅ `llm_input` / `llm_output` |
| 工具调用前/后 | ✅ Skill hook | ✅ `before_tool_call` / `after_tool_call` |
| 会话生命周期 | ❌ | ✅ `session_start` / `session_end` |

---

## 六、Skill 系统

### 6.1 OpenClaw 的 Skill 来源

```typescript
// src/agents/skills/types.ts
export type SkillEntry = {
  skill: Skill              // 来自 @mariozechner/pi-coding-agent
  frontmatter: ParsedSkillFrontmatter
  metadata?: OpenClawSkillMetadata
  invocation?: SkillInvocationPolicy
}
```

**来源**：
1. Bundled Skills（内置的）
2. Plugin Skills（插件提供的）
3. Workspace Skills（用户工作区的）
4. ClawHub（远程安装的）

### 6.2 vs Claude Code Skill

| 维度 | Claude Code | OpenClaw |
|------|------------|----------|
| 定义格式 | Markdown + frontmatter | 同上 |
| 参数定义 | frontmatter args | 同上 |
| 执行方式 | SkillTool 原生执行 | Gateway RPC + tool |
| 来源 | 本地文件系统 | 多来源（bundled/plugin/workspace/remote）|

**核心区别**：
- Claude Code 的 Skill 通过 `SkillTool.call()` 原生执行
- OpenClaw 的 Skill 通过 **tool 调用**（SkillCommandDispatchSpec）

---

## 七、Compaction（上下文压缩）

### 7.1 OpenClaw 的特色功能

```typescript
// src/agents/pi-embedded-runner/compact.ts
export async function runCompaction(session, params) {
  // 压缩会话历史，释放上下文窗口
}
```

**这是 Claude Code 没有的功能**！

Claude Code 的上下文管理靠手动 /context 命令，而 OpenClaw 有自动 compaction。

### 7.2 Compaction Hook

```typescript
// src/agents/pi-hooks/compaction-hooks.ts
export function runCompactionHooks(session, reason) {
  // Hook: before_compaction / after_compaction
}
```

---

## 八、Channel 系统（OpenClaw 特有）

### 8.1 支持的 Channel

- Telegram
- Discord
- Slack
- Signal
- iMessage
- WhatsApp
- Matrix
- Web（内置）
- 等等...

### 8.2 Channel 架构

```typescript
// src/channels/plugins/types.plugin.ts
export interface ChannelPlugin {
  name: string
  sendMessage(params: SendMessageParams): Promise<void>
  onMessage(handler: MessageHandler): void
  // ...
}
```

**OpenClaw 的 Channel 是插件**，可以动态加载/卸载。

---

## 九、MCP 集成

```typescript
// src/mcp/channel-tools.ts
// MCP 工具通过这里注册到 Agent
```

OpenClaw 通过 `mcporter`（独立工具）集成 MCP，与核心代码解耦。

---

## 十、核心差距分析

### OpenClaw 相比 Claude Code 的优势

| 优势 | 说明 |
|------|------|
| **Channel 插件** | 支持 10+ 消息渠道，Claude Code 只有 CLI |
| **Compaction** | 自动上下文压缩，Claude Code 手动 |
| **Hook 系统** | 30+ 生命周期 hook，Claude Code 只有 Skill hook |
| **分布式架构** | Gateway + Agent 分离，Claude Code 是单体 |
| **Plugin 系统** | 完整的插件系统，Claude Code 没有 |

### Claude Code 相比 OpenClaw 的优势

| 优势 | 说明 |
|------|------|
| **Tool 原生执行** | 同进程执行，无 RPC 开销 |
| **动态 Tool 描述** | description 是函数，可根据输入变化 |
| **极简架构** | 代码量少，容易理解 |
| **CLI 专注** | 单用途，深度优化 |

---

## 十一、真正的差距在哪里

### 11.1 OpenClaw 缺什么

1. **Tool 描述动态化**
   - OpenClaw 的工具描述是静态的
   - Claude Code 的 description 是函数，可根据输入变化

2. **Tool 原生执行**
   - OpenClaw 的工具通过 RPC 调用
   - Claude Code 的工具在同一个进程里

3. **权限模型**
   - OpenClaw 目前**没有**细粒度的工具权限抽象
   - Claude Code 有四级权限模式

### 11.2 OpenClaw 比 Claude Code 多的

1. **Channel 系统**：多渠道消息接入
2. **Compaction**：自动上下文压缩
3. **Hook 系统**：完整生命周期
4. **分布式架构**：Gateway 分离

---

## 十二、下一步研究建议

### 基于 Claude Code 学习的目标

| 目标 | OpenClaw 现状 | 需要做什么 |
|------|-------------|---------|
| 动态 Tool 描述 | 静态 | 研究工具 schema 是否可增强 |
| 权限抽象 | 无 | 研究 OpenClaw 的安全模型 |
| Hook 系统 | 有，但不同 | 研究 OpenClaw Hook 与 Claude Code Hook 的对应关系 |

### 继续学习优先级

1. **OpenClaw Hook 系统深度研究**（OpenClaw 的强项，值得学）
2. **OpenClaw Compaction 机制**（Claude Code 没有的）
3. **OpenClaw Plugin SDK**（完整的插件系统）
4. **Tool 系统的增强可能性**（如何引入动态描述）

---

_Last updated: 2026-03-31_
