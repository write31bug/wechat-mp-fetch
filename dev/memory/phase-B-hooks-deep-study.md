# 阶段 B：Hook 系统对比 — 深度研究报告

> 研究日期：2026-03-31

---

## 一、Claude Code Hook 系统

### 1.1 Hook Events 完整列表（27个）

```typescript
const HOOK_EVENTS = [
  'PreToolUse',           // 工具调用前
  'PostToolUse',          // 工具调用后
  'PostToolUseFailure',   // 工具调用失败后
  'Notification',         // 通知
  'UserPromptSubmit',     // 用户提交输入时
  'SessionStart',         // 会话开始
  'SessionEnd',           // 会话结束
  'Stop',                 // 停止时
  'StopFailure',          // 停止失败时
  'SubagentStart',        // 子Agent启动
  'SubagentStop',         // 子Agent停止
  'PreCompact',           // 压缩前
  'PostCompact',          // 压缩后
  'PermissionRequest',    // 权限请求
  'PermissionDenied',     // 权限拒绝
  'Setup',                // 设置时
  'TeammateIdle',         // 队友空闲
  'TaskCreated',          // 任务创建
  'TaskCompleted',        // 任务完成
  'Elicitation',          // 恳求/提示
  'ElicitationResult',    // 恳求结果
  'ConfigChange',         // 配置变更
  'WorktreeCreate',       // Git worktree 创建
  'WorktreeRemove',       // Git worktree 删除
  'InstructionsLoaded',    // 指令加载
  'CwdChanged',           // 工作目录变更
  'FileChanged',          // 文件变更
]
```

### 1.2 Hook 类型（4种）

```typescript
type HookCommand =
  | { type: 'command', command: string, if?: string }     // Bash 命令
  | { type: 'prompt', prompt: string, model?: string }    // LLM prompt
  | { type: 'agent', prompt: string, model?: string }     // Agent 验证
  | { type: 'http', url: string, headers?: object }        // HTTP POST
```

### 1.3 特点

- **Skill 级别**：Hook 通过 SKILL.md 的 frontmatter 注册
- **本地执行**：Hook 在 Claude Code 进程内执行
- **轻量**：不需要复杂的插件系统
- **场景**：自动化质检、格式化、lint 等

---

## 二、OpenClaw Hook 系统

### 2.1 Hook Events 完整列表（27个）

```typescript
const PLUGIN_HOOK_NAMES = [
  'before_model_resolve',    // 模型选择前
  'before_prompt_build',     // Prompt 构建前
  'before_agent_start',      // Agent 启动前
  'llm_input',              // LLM 输入
  'llm_output',             // LLM 输出
  'agent_end',              // Agent 结束
  'before_compaction',      // 压缩前
  'after_compaction',       // 压缩后
  'before_reset',           // 重置前
  'inbound_claim',          // 入站认领
  'message_received',       // 消息收到
  'message_sending',        // 消息发送
  'message_sent',           // 消息已发送
  'before_tool_call',       // 工具调用前
  'after_tool_call',         // 工具调用后
  'tool_result_persist',    // 工具结果持久化
  'before_message_write',   // 消息写入前
  'session_start',          // 会话开始
  'session_end',            // 会话结束
  'subagent_spawning',     // 子Agent生成中
  'subagent_delivery_target', // 子Agent投递目标
  'subagent_spawned',      // 子Agent已生成
  'subagent_ended',        // 子Agent结束
  'gateway_start',         // Gateway 启动
  'gateway_stop',          // Gateway 停止
  'before_dispatch',       // 分发前
  'before_install',        // 安装前
]
```

### 2.2 特点

- **Plugin 系统**：Hook 通过 Plugin 注册
- **分布式**：Hook 在 Gateway + Agent 架构中运行
- **完整生命周期**：覆盖 Gateway、Session、Agent、Tool、Message 各层
- **安全模型**：有 prompt injection hook 防护

---

## 三、深度对比分析

### 3.1 覆盖阶段对比

| 阶段 | Claude Code | OpenClaw |
|------|------------|----------|
| **模型选择** | ❌ | ✅ `before_model_resolve` |
| **Prompt 构建** | ❌ | ✅ `before_prompt_build` |
| **LLM 输入/输出** | ❌ | ✅ `llm_input` / `llm_output` |
| **Agent 生命周期** | ✅ `Setup` | ✅ `before_agent_start` / `agent_end` |
| **工具调用前** | ✅ `PreToolUse` | ✅ `before_tool_call` |
| **工具调用后** | ✅ `PostToolUse` | ✅ `after_tool_call` |
| **工具失败** | ✅ `PostToolUseFailure` | ❌ 无 |
| **会话生命周期** | ✅ `SessionStart/End` | ✅ `session_start/end` |
| **压缩** | ✅ `PreCompact/PostCompact` | ✅ `before_compaction/after_compaction` |
| **子Agent** | ✅ `SubagentStart/Stop` | ✅ `subagent_spawning/spawned/ended` |
| **消息** | ❌ | ✅ `message_received/sending/sent` |
| **文件变更** | ✅ `FileChanged/CwdChanged` | ❌ 无 |
| **Worktree** | ✅ `WorktreeCreate/Remove` | ❌ 无 |
| **权限** | ✅ `PermissionRequest/Denied` | ❌ 无 |
| **Gateway** | ❌ | ✅ `gateway_start/stop` |
| **安装** | ❌ | ✅ `before_install` |

### 3.2 设计哲学差异

| 维度 | Claude Code | OpenClaw |
|------|------------|----------|
| **架构** | 单体 CLI | 分布式 Gateway |
| **Hook 来源** | SKILL.md frontmatter | Plugin 系统注册 |
| **Hook 类型** | command/prompt/agent/http | 全部是 async 函数 |
| **触发机制** | 嵌入式 | 插件 + 生命周期 |
| **使用场景** | Skill 自动化质检 | 平台级扩展 |

### 3.3 各自独特的能力

**Claude Code 独有**：
- `FileChanged` / `CwdChanged`：文件变更监听
- `WorktreeCreate` / `WorktreeRemove`：Git worktree 管理
- `PermissionRequest` / `PermissionDenied`：权限管理
- `Notification`：系统通知
- `Elicitation`：用户交互提示

**OpenClaw 独有**：
- `before_model_resolve`：模型选择拦截
- `llm_input` / `llm_output`：LLM 输入输出拦截
- `gateway_start` / `gateway_stop`：Gateway 生命周期
- `message_received` / `message_sending`：消息通道拦截
- `before_dispatch`：消息分发拦截
- `tool_result_persist`：工具结果持久化
- `inbound_claim`：入站消息认领

---

## 四、多问几个"为什么"

### Q1：为什么 Claude Code 有 FileChanged Hook，但 OpenClaw 没有？

**分析**：
- Claude Code 是**本地 CLI 工具**，直接访问文件系统
- 文件变更是核心场景（编码时文件随时变）
- OpenClaw 是**分布式 Gateway**，文件访问通过 Tool RPC

**结论**：架构差异导致需求不同。OpenClaw 如果需要文件监听，应该通过 Tool 实现，而不是 Hook。

### Q2：为什么 OpenClaw 有 `llm_input` / `llm_output`，但 Claude Code 没有？

**分析**：
- Claude Code 的 LLM 调用在 `QueryEngine` 内部，Hook 难以注入
- OpenClaw 的 Agent Runtime 和 LLM 调用分离，有明确的 hook 注入点

**结论**：这是架构决定的。OpenClaw 的分离架构让 LLM Hook 成为可能。

### Q3：OpenClaw 的 Hook 为什么需要 Plugin 系统？

**分析**：
- OpenClaw 支持多渠道、多 Provider
- Hook 需要跨渠道生效
- Plugin 系统提供了统一的 Hook 注册和分发机制

**结论**：Plugin 系统让 Hook 可以模块化、热插拔。

---

## 五、对 OpenClaw 的启发

### 5.1 OpenClaw 目前的 Hook 系统已经很完整

**OpenClaw 的 Hook 覆盖了**：
- ✅ Gateway 生命周期
- ✅ 会话生命周期
- ✅ Agent 生命周期
- ✅ LLM 输入/输出
- ✅ 工具调用前后
- ✅ 消息通道
- ✅ Compaction

### 5.2 Claude Code 的 Hook 有什么值得借鉴？

| Claude Code Hook | OpenClaw 现状 | 是否需要借鉴 |
|-----------------|-------------|------------|
| `PermissionRequest/Denied` | OpenClaw 无 | ❌ 企业微信 API 已有权限控制 |
| `Notification` | OpenClaw 无 | 🟡 可考虑消息通知 Hook |
| `Elicitation` | OpenClaw 无 | ❌ 场景不同 |
| `FileChanged` | 通过 Tool 实现 | ❌ 不需要 |

### 5.3 OpenClaw Hook 的潜在增强方向

1. **Notification Hook**（可选）
   - 在 `message_sent` 基础上增加通知机制
   - 用于跨渠道通知

2. **权限 Hook**（可选）
   - 如果未来需要细粒度工具权限
   - 可以参考 Claude Code 的 `PermissionRequest` 模式

---

## 六、Claude Code Skill Hook 的实现原理

### 6.1 Hook 在 Skill 中的定义

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
          if: "Write(*.ts)"  # 条件过滤
        - type: prompt
          prompt: "Should I allow this write? $ARGUMENTS"
---
```

### 6.2 Hook 执行流程

```
Skill 执行
  ↓
parseHooksFromFrontmatter() 解析 hook 配置
  ↓
HookRunner 执行匹配的 hook
  ↓
根据 type 执行：
  - command: 启动 subprocess
  - prompt: 调用 LLM
  - agent: 启动子 Agent
  - http: POST 请求
```

### 6.3 `if` 条件过滤

```typescript
// if 条件使用 permission rule 语法
// 例如："Bash(git *)" 表示只匹配 git 命令
if: IfConditionSchema()  // "Bash(git *)", "Read(*.ts)"
```

---

## 七、阶段 B 复盘

### 7.1 核心发现

**1. OpenClaw 的 Hook 系统比 Claude Code 更完整**
- OpenClaw 有 27 个 Hook，覆盖 Gateway、Session、Agent、Tool、Message 各层
- Claude Code 有 27 个 Hook，但偏向 Skill 级别的自动化

**2. 架构差异决定了 Hook 设计**
- Claude Code 是单体 CLI，Hook 在进程内执行
- OpenClaw 是分布式 Gateway，Hook 通过 Plugin 注册

**3. OpenClaw 缺少 Claude Code 的一些 Hook**
- `PermissionRequest` / `PermissionDenied`：权限管理
- `Notification`：系统通知
- `FileChanged`：文件变更监听

**4. Claude Code 缺少 OpenClaw 的一些 Hook**
- `llm_input` / `llm_output`：LLM 输入输出拦截
- `before_model_resolve`：模型选择拦截
- `gateway_start/stop`：Gateway 生命周期

### 7.2 落地规划

**短期（1-2 周）**：
- OpenClaw 的 Hook 系统已经足够强大
- 不需要新增 Hook

**中期（1 个月）**：
- 如果企业微信工具需要通知功能，可以考虑增加 `Notification` Hook
- 如果需要细粒度权限控制，可以参考 Claude Code 的 `PermissionRequest` 模式

**长期（季度）**：
- Hook 系统不需要大的改动
- 重点是 Plugin 生态的完善

### 7.3 与前面阶段的连接

- **阶段一**（QueryEngine）：QueryEngine 的 queryLoop 调用 Tool，Hook 在 Tool 执行前后插入
- **阶段二**（Tool 系统）：Tool.call() 内部调用 checkPermissions()，Hook 在权限检查前后执行
- **阶段 B**（Hook 系统）：Hook 是横切关注点，贯穿整个生命周期

---

## 八、下一步：阶段 C

**OpenClaw Compaction 机制**

这是 Claude Code 没有的特色功能：
- Claude Code 靠手动 `/context` 命令管理上下文
- OpenClaw 有自动 Compaction

需要研究：
- Compaction 是什么时候触发的？
- Compaction Hook（`before_compaction` / `after_compaction`）是怎么用的？

---

_Last updated: 2026-03-31_
