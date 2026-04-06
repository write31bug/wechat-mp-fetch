# Claude Code 源码关键洞察

> 来源：泄露源码（2026-03-31）粗略分析

---

## 1. 启动优化：并行预取模式

```typescript
// main.tsx — 在任何 import 之前就触发副作用
startMdmRawRead();           // MDM 配置（企业设备管理）
startKeychainPrefetch();     // macOS Keychain（OAuth + API Key）
```

**原理**：MDM 和 Keychain 原本是同步阻塞读取，通过提前触发 subprocess 并行化，可节省 ~65ms 启动时间。

---

## 2. 工具系统架构

### Tool 基类设计

```typescript
// Tool.ts — 所有工具的基类型
interface Tool {
  name: string
  description: string
  inputSchema: JSONSchema     // Zod schema
  permission: PermissionMode  // 权限级别
  execute(input: unknown): Promise<ToolResult>
}
```

### 权限模式

| 模式 | 行为 |
|------|------|
| `default` | 首次询问用户 |
| `plan` | Plan 模式下绕过 |
| `bypassPermissions` | 完全跳过（CI模式） |
| `auto` | 根据风险自动决策 |

---

## 3. QueryEngine 核心循环

```
query() 
  → API stream → 解析 content_block (tool_use)
  → useCanUseTool() 检查权限
  → tool.execute()
  → 追加到 messages
  → 循环直到收到 final message
```

**关键机制**：
- Streaming 流式响应
- Thinking mode 支持（`thinking.ts`）
- Token 用量追踪（`cost-tracker.ts`）
- 重试逻辑（`categorizeRetryableAPIError`）

---

## 4. Skill 系统（与 OpenClaw SKILL 对比）

Claude Code Skill 是 Markdown 文件：

```markdown
---
description: 我的技能
args:
  - name: target
    description: 目标文件
---
# 技能执行步骤
1. 读取 {{target}}
2. 分析 ...
```

**OpenClaw SKILL 异同**：
- 同样是 Markdown 格式（SKILL.md）
- Claude Code 支持 frontmatter args，OpenClaw 支持更多工具元数据
- Claude Code Skill 通过 `SkillTool` 执行，OpenClaw 通过 `wecom_mcp` 协议

---

## 5. Bridge IPC 机制

```typescript
// bridgeMain.ts — 主循环
// VS Code / JetBrains 插件 <→ Claude Code CLI 双向通信
// 协议：WebSocket + JWT 认证
```

**核心场景**：IDE 内点击代码 → 传递上下文 → Claude Code 执行 → 结果回传

---

## 6. 懒加载与代码消除

### 懒加载大依赖

```typescript
// 需要时才 import
const { heavyModule } = await import('./heavy.js')
```

### 编译时消除（ Bun 特性）

```typescript
import { feature } from 'bun:bundle'

const voiceCommand = feature('VOICE_MODE')
  ? require('./commands/voice/index.js').default
  : null
```

**效果**：未启用 VOICE_MODE 的构建，Voice 代码完全不存在于产物中。

---

## 7. Agent Swarms（多Agent协调）

```typescript
// coordinatorMode.ts
isCoordinatorMode() // 检查环境变量
// Coordinator 模式下：
// - AgentTool 可创建子Agent
// - TeamCreateTool 创建并行工作团队
// - SendMessageTool Agent间通信
```

---

## 8. 上下文管理

```typescript
// context.ts — 收集系统上下文
getSystemContext()  // OS/平台/语言等
getUserContext()    // 用户偏好/历史

// memdir/ — 持久化记忆
loadMemoryPrompt()  // 加载记忆用于上下文
memoryScan()        // 自动提取关键信息
```

---

## 9. REPL UI（Ink + React）

```typescript
// src/ink/ — 自定义 React 渲染器
// 基于 Ink（React for CLI）构建终端UI
// 支持：颜色/ANSI/动画/焦点管理
```

---

## 10. 会话恢复机制

```typescript
// sessionRestore.ts
// 意外中断后恢复工作区状态
// 存储：messages + tool_results + file_changes
```

---

## 对 OpenClaw 的参考价值

| Claude Code 模块 | OpenClaw 可借鉴点 |
|-----------------|------------------|
| Tool 系统 | 工具注册 + 权限管理 |
| Skill 系统 | SKILL.md 格式完善 |
| QueryEngine | Agent Loop 实现 |
| Bridge | 远程控制 IPC |
| 懒加载 | 插件按需加载 |
| 启动优化 | Gateway 启动加速 |

---

_Last updated: 2026-03-31_
