# 阶段 C：Compaction 机制 — 深度研究报告

> 研究日期：2026-03-31

---

## 一、Claude Code 的上下文管理

### 1.1 手动 /context 命令

Claude Code 的上下文管理**完全靠用户手动**：

```
/context      — 查看当前上下文使用情况
/context 100  — 保留最近 100 条消息
/context 0    — 清空所有上下文（从头开始）
```

### 1.2 特点

- **用户主动触发**：LLM 不会自动触发 compaction
- **简单粗暴**：直接截断历史
- **无摘要**：不生成摘要，直接丢弃
- **依赖 LLM 记忆**：用户需要重新告诉 LLM 之前的状态

### 1.3 为什么 Claude Code 没有自动 Compaction？

**可能的原因**：
1. CLI 场景：用户实时看到上下文使用量，可以手动控制
2. 截断 vs 摘要：Claude Code 选择截断，不做摘要（因为摘要可能丢失重要信息）
3. 架构限制：`@mariozechner/pi-coding-agent` 才有 Compaction，Claude Code 用的是自己的 QueryEngine

---

## 二、OpenClaw 的 Compaction 机制

### 2.1 触发时机

```typescript
type CompactEmbeddedPiSessionParams = {
  trigger?: "budget" | "overflow" | "manual"
  force?: boolean
  tokenBudget?: number
}
```

**三种触发方式**：
- `budget`：Token 预算达到阈值时自动触发
- `overflow`：上下文窗口溢出前触发
- `manual`：用户手动触发

### 2.2 完整流程

```
compactEmbeddedPiSession() 执行
    ↓
runBeforeCompactionHooks() ← Hook: before_compaction
    ↓
session.compact() ← 核心：调用 pi-coding-agent 的 compaction
    ↓
runPostCompactionSideEffects() ← 副作用处理
    ↓
runAfterCompactionHooks() ← Hook: after_compaction
    ↓
truncateSessionAfterCompaction() ← 截断会话文件
```

### 2.3 Compaction 核心逻辑

```typescript
// compact.ts — 核心 compaction 流程
const result = await compactWithSafetyTimeout(
  () => {
    return session.compact(params.customInstructions)
  },
  compactionTimeoutMs,
  { abortSignal, onCancel }
)
```

**session.compact() 做了什么**：
1. 分析会话历史消息
2. 识别"可压缩"的消息（工具调用结果等）
3. 生成摘要（summary）
4. 保留最近的关键消息
5. 返回：`{ summary, tokensBefore, firstKeptEntryId }`

### 2.4 Compaction 包含的内容

```typescript
type CompactionMessageMetrics = {
  messages: number           // 消息数量
  historyTextChars: number   // 历史文本字符数
  toolResultChars: number   // 工具结果字符数
  estTokens?: number        // 估算 token 数
  contributors: Array<{     // 最大贡献者
    role: string
    chars: number
    tool?: string
  }>
}
```

---

## 三、Compaction Hooks

### 3.1 before_compaction Hook

```typescript
// compact.ts
const beforeHookMetrics = buildBeforeCompactionHookMetrics({
  originalMessages,
  currentMessages: session.messages,
  observedTokenCount,
  estimateTokensFn: estimateTokens,
})
const { hookSessionKey, missingSessionKey } = await runBeforeCompactionHooks({
  hookRunner,
  sessionId: params.sessionId,
  sessionKey: params.sessionKey,
  sessionAgentId,
  workspaceDir: effectiveWorkspace,
  messageProvider: resolvedMessageProvider,
  metrics: beforeHookMetrics,
})
```

**Hook 收到的信息**：
- 原始消息数量
- 当前消息数量
- 观察到的 token 数
- 各消息的字符贡献

### 3.2 after_compaction Hook

```typescript
// compact.ts
await runAfterCompactionHooks({
  hookRunner,
  sessionId: params.sessionId,
  sessionAgentId,
  hookSessionKey,
  missingSessionKey,
  workspaceDir: effectiveWorkspace,
  messageProvider: resolvedMessageProvider,
  messageCountAfter,
  tokensAfter,
  compactedCount,        // 删除了多少条消息
  sessionFile: params.sessionFile,
  summaryLength: result.summary.length,
  tokensBefore: result.tokensBefore,
  firstKeptEntryId: result.firstKeptEntryId,
})
```

**Hook 收到的信息**：
- 压缩后消息数
- 压缩后 token 数
- 删除的消息数
- 摘要长度
- 保留的第一个消息 ID

---

## 四、Compaction 的安全保障

### 4.1 Safety Timeout

```typescript
// compact.ts
const compactionTimeoutMs = resolveCompactionTimeoutMs(params.config)
const result = await compactWithSafetyTimeout(
  () => session.compact(params.customInstructions),
  compactionTimeoutMs,  // 默认 30 秒
  { abortSignal, onCancel }
)
```

**防止 compaction 无限挂起**。

### 4.2 Compaction Safeguard

```typescript
// pi-hooks/compaction-safeguard-runtime.ts
// 防止低质量 compaction
const qualityResult = await runCompactionSafeguardQualityCheck({
  summary,
  sessionManager,
})
```

---

## 五、与 Claude Code 的对比

### 5.1 上下文管理方式对比

| 维度 | Claude Code | OpenClaw |
|------|------------|----------|
| **触发方式** | 手动 `/context` | 自动 + 手动 |
| **处理方式** | 直接截断 | 生成摘要 + 截断 |
| **用户控制** | 完全手动 | 可配置阈值 |
| **Hook** | ❌ 无 | ✅ before/after compaction |
| **安全保障** | 无 | Safety Timeout + Safeguard |

### 5.2 为什么 OpenClaw 需要自动 Compaction？

**原因**：
1. **Gateway 场景**：用户不实时在线，无法手动控制
2. **长会话**：企业微信等渠道可能持续数天
3. **多渠道**：多个渠道同时运行，上下文增长更快
4. **摘要价值**：生成摘要比直接截断更能保留信息

### 5.3 Claude Code 为什么不需要自动 Compaction？

**原因**：
1. **CLI 用户实时在线**：用户看到上下文快满了，手动处理
2. **单会话**：每次启动是一个新会话
3. **简单截断足够**：CLI 场景不需要复杂摘要

---

## 六、多问几个"为什么"

### Q1：为什么 OpenClaw 的 Compaction 要生成摘要？

**分析**：
- 直接截断会丢失历史信息
- 摘要保留了关键上下文
- 对于多轮对话场景，摘要比截断更有价值

**结论**：这是设计选择，OpenClaw 选择了更智能的方案。

### Q2：为什么需要 before/after compaction Hook？

**分析**：
- `before_compaction`：允许插件在 compaction 前做清理（如关闭文件句柄）
- `after_compaction`：允许插件在 compaction 后更新状态（如记忆系统）

**结论**：Hook 让 Compaction 可扩展、可干预。

### Q3：为什么 Compaction 需要 Safety Timeout？

**分析**：
- Compaction 需要调用 LLM 生成摘要
- 如果 LLM 无响应，compaction 会无限等待
- Timeout 防止系统挂起

**结论**：Safety Timeout 是工程实践，防止异常情况。

---

## 七、对 OpenClaw 的启发

### 7.1 Compaction 是 OpenClaw 的独特价值

Claude Code 完全**没有**自动 Compaction，这是 OpenClaw 作为平台的核心优势之一。

### 7.2 Hook 让 Compaction 更强大

```typescript
// before_compaction: 清理资源
before_compaction:
  - type: command
    command: "echo 'compaction starting'"

// after_compaction: 更新记忆
after_compaction:
  - type: agent
    prompt: "Update memory with summary: $SUMMARY"
```

### 7.3 下一步

**阶段 C 落地规划**：
- OpenClaw 的 Compaction 已经很完善
- 不需要大的改动
- 可以考虑增强 before/after Hook 的使用场景

---

## 八、阶段 C 复盘

### 8.1 核心发现

1. **Claude Code 没有自动 Compaction**
   - 完全靠用户手动 `/context` 命令
   - 直接截断，不生成摘要

2. **OpenClaw 有完整的 Compaction 机制**
   - 自动 + 手动两种触发方式
   - 生成摘要保留上下文
   - before/after Hook 让过程可扩展

3. **Compaction Hook 的价值**
   - `before_compaction`：清理资源、准备状态
   - `after_compaction`：更新记忆、记录日志

### 8.2 与前面的连接

- **阶段一**（QueryEngine）：Compaction 发生在 Agent 循环中
- **阶段二**（Tool 系统）：Compaction 影响工具调用的历史上下文
- **阶段 B**（Hook 系统）：`before_compaction` / `after_compaction` 是 Hook 系统的一部分

---

_Last updated: 2026-03-31_
