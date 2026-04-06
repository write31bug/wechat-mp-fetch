# OpenClaw 记忆持久化机制调研报告

**调研日期：** 2026-04-06
**调研范围：** OpenClaw v24.x 本地源码 + 官方文档
**源码路径：** `D:\work\software\nvm\v24.0.0\node_modules\openclaw\dist\`
**文档路径：** `D:\work\software\nvm\v24.0.0\node_modules\openclaw\docs\concepts\`

---

## 一、整体架构概览

OpenClaw 的记忆系统分为**两层**，互相配合但机制不同：

| 层次 | 存储位置 | 生命周期 | 加载方式 |
|------|---------|---------|---------|
| **Memory Files** (Markdown) | `~/.openclaw/workspace/MEMORY.md` + `memory/*.md` | 持久，手动写入 | 仅 DM Session 启动时注入到 System Prompt |
| **Session Transcript** (JSONL) | `~/.openclaw/agents/<agentId>/sessions/<sessionId>.jsonl` | 按 Session 维护，默认 30d 清理 | 每次 Assemble 阶段从磁盘读取 |
| **Vector Index** (SQLite) | `~/.openclaw/memory/<agentId>.sqlite` | 持久，跟随文件变化自动重建 | `memory_search` tool 触发 |

---

## 二、核心文件存储路径

### 2.1 状态根目录
```
~/.openclaw/                    ← 默认（可通过 OPENCLAW_STATE_DIR 覆盖）
~/.clawdbot/                    ← 旧版兼容
```
**源码依据：** `paths-DQgqpvCf.js` → `resolveStateDir()`，行 ~55-70

### 2.2 Session 存储
```
~/.openclaw/agents/<agentId>/sessions/sessions.json     ← Session 索引（key-value map）
~/.openclaw/agents/<agentId>/sessions/<sessionId>.jsonl ← 实际对话记录（JSONL，append-only）
~/.openclaw/agents/<agentId>/sessions/<sessionId>-topic-<threadId>.jsonl ← 话题线程
```
**源码依据：** `sessions-DhKmXFAO.js` 行 ~350-400；`paths-BC0JJAKv.js` 行 ~30-50

### 2.3 Workspace 文件（Agent 配置）
```
~/.openclaw/workspace/          ← 默认 workspace（可通过 agent.workspace 配置覆盖）
├── AGENTS.md                   ← Agent 工作规范
├── SOUL.md                     ← Agent 人格
├── TOOLS.md                    ← 工具说明
├── IDENTITY.md                 ← Agent 身份
├── USER.md                     ← 用户信息
├── HEARTBEAT.md                ← 心跳配置
├── BOOTSTRAP.md                ← 初始化引导
├── MEMORY.md                   ← 【长期记忆】长程事实、偏好、决策
└── memory/
    └── YYYY-MM-DD.md           ← 【每日笔记】日常上下文和观察
```
**源码依据：** `workspace-BUc4RCkE.js` 行 ~62-72（文件名常量定义），行 ~200-350（bootstrap 文件加载逻辑）

### 2.4 内存向量索引（Memory Search）
```
~/.openclaw/memory/<agentId>.sqlite   ← 内置引擎 SQLite DB
~/.openclaw/memory/<agentId>-qmd/     ← QMD 引擎（可选）
```
**源码依据：** `memory-search-weSJLcII.js` 行 ~30-35

### 2.5 Subagent Registry
```
~/.openclaw/subagents/runs.json       ← Subagent 运行记录
```
**源码依据：** `session-utils-Jgzk2Bo-.js` 行 ~181-200（`resolveSubagentRegistryPath`）

---

## 三、Session 创建/销毁的 Context 生命周期

### 3.1 Session 启动流程

```
1. 收到用户消息
2. 解析 sessionKey（来自 session store 或新建）
3. 加载 Session Store（sessions.json 中的 entry）
4. 加载/创建 Transcript 文件（<sessionId>.jsonl）
5. 执行 Bootstrap Hook（加载 workspace 文件）
6. Assemble 阶段：构建 LLM Context
   - 读取 Transcript 历史消息
   - 注入 Bootstrap 文件（MEMORY.md + memory/ 日记）
   - 注入 System Prompt
7. 调用 LLM
8. 响应写入 Transcript
9. Session 结束
```

**源码依据：** `sessions-DhKmXFAO.js` 行 ~60-150（`appendAssistantMessageToSessionTranscript`）

### 3.2 Session Entry 结构（sessions.json 中的每条记录）

```typescript
interface SessionEntry {
  sessionId: string;       // UUID，session 唯一标识
  updatedAt: number;       // 最后活动时间（毫秒）
  sessionFile?: string;     // 可选，手动指定 transcript 路径
  // ... 其他字段
}
```

**源码依据：** `session-file-CvpVqi4V.js` 行 ~30-60（`resolveAndPersistSessionFile`）

### 3.3 Transcript 文件格式（JSONL）

每行一个 JSON 对象，包含 role/content/timestamp 等字段：

```jsonl
{"type":"session","version":1,"id":"<sessionId>","timestamp":"...","cwd":"..."}
{"role":"user","content":[{"type":"text","text":"..."}],"timestamp":...}
{"role":"assistant","content":[{"type":"text","text":"..."}],"timestamp":...,"usage":{...}}
```

**源码依据：** `sessions-DhKmXFAO.js` 行 ~80-100（`ensureSessionHeader` + `appendAssistantMessageToSessionTranscript`）

---

## 四、`memory/` 目录文件的读写时机

### 4.1 读取时机

**不是自动加载**，而是通过 `memory_search` 和 `memory_get` 工具按需访问。

- `MEMORY.md` 特殊：DM Session 启动时注入到 System Prompt（不是工具调用，是直接文本注入）
- `memory/YYYY-MM-DD.md`：Today 和 Yesterday 的笔记自动加载（见 `workspace-BUc4RCkE.js` 的 `loadWorkspaceBootstrapFiles`）

**源码依据：** `workspace-BUc4RCkE.js` 行 ~330-380（`resolveMemoryBootstrapEntry` + `loadWorkspaceBootstrapFiles`）

### 4.2 写入时机

**无自动写入**。由 Agent 主动调用 `write` 工具写 Markdown 文件，或通过 Memory Flush 机制。

Memory Flush 在 Compaction 之前触发（见下节）。

### 4.3 索引时机

`memory/YYYY-MM-DD.md` 文件被修改后，触发**防抖索引**（debounce 1.5s），自动重建向量索引。

**源码依据：** `memory-search-weSJLcII.js` 行 ~70-80（watch 配置）

---

## 五、`MEMORY.md` 的加载时机和方式

### 5.1 加载时机

**DM Session 启动时**，作为 Bootstrap 文件之一，注入到 System Prompt。

关键条件：
- Session 类型必须是 DM（direct message）
- Cron Session 和 Subagent Session **不加载** MEMORY.md（仅加载 AGENTS.md / TOOLS.md / SOUL.md / IDENTITY.md / USER.md）

**源码依据：** `workspace-BUc4RCkE.js` 行 ~360-390（`filterBootstrapFilesForSession`）

```typescript
// 行 360-365 附近
const MINIMAL_BOOTSTRAP_ALLOWLIST = new Set([
  DEFAULT_AGENTS_FILENAME,
  DEFAULT_TOOLS_FILENAME,
  DEFAULT_SOUL_FILENAME,
  DEFAULT_IDENTITY_FILENAME,
  DEFAULT_USER_FILENAME,
  // MEMORY.md 不在其中！
]);
function filterBootstrapFilesForSession(files, sessionKey) {
  if (!sessionKey || !isSubagentSessionKey(sessionKey) && !isCronSessionKey(sessionKey)) return files;
  return files.filter((file) => MINIMAL_BOOTSTRAP_ALLOWLIST.has(file.name));
}
```

### 5.2 加载方式

1. 调用 `loadWorkspaceBootstrapFiles(workspaceDir)` → 读取 workspace 下所有 Bootstrap 文件
2. 文件内容经过 `readWorkspaceFileWithGuards` 安全读取（限制 2MB，防越界）
3. 内容通过 `buildBootstrapContextFiles` 注入到 System Prompt
4. 有总长度限制（默认 20000 字符/文件），超限会 truncate

**源码依据：** `workspace-BUc4RCkE.js` 行 ~81-110；`pi-embedded-helpers-0c94i8Rl.js`

### 5.3 每日笔记（memory/YYYY-MM-DD.md）的加载规则

Today + Yesterday 的日记会自动加载（通过日期判断），其他日期的日记需要通过 `memory_search` 工具查找。

**文档依据：** `docs/concepts/memory.md` — "Today and yesterday's notes are loaded automatically"

---

## 六、Subagent Session 的存储位置和格式

### 6.1 Subagent Registry 路径

```javascript
// session-utils-Jgzk2Bo-.js 行 ~183-187
function resolveSubagentRegistryPath() {
  return path.join(resolveSubagentStateDir(process.env), "subagents", "runs.json");
}
```

存储路径：`~/.openclaw/subagents/runs.json`

### 6.2 Registry 数据格式（version 2）

```json
{
  "version": 2,
  "runs": {
    "<runId>": {
      "runId": "...",
      "sessionId": "...",          // 子 session 的 UUID
      "sessionKey": "...",         // agent:subagent:<runId>:<depth>
      "spawnMode": "session",       // or "run"
      "startedAt": 1743916800000,
      "endedAt": 1743916900000,
      "cleanupCompletedAt": ...,
      "cleanupHandled": true/false,
      "requesterOrigin": { channel, accountId },
      // ... 其他字段
    }
  }
}
```

**源码依据：** `session-utils-Jgzk2Bo-.js` 行 ~189-230（`loadSubagentRegistryFromDisk`）

### 6.3 Subagent Session 的 Context 隔离

Subagent 有自己独立的 Session Transcript（独立 JSONL 文件），**不自动继承父 session 的 memory context**。

父 session 的信息只能通过以下方式传递：
1. **消息传递**：父 session 发送的消息内容
2. **工具调用**：父 session 调用工具（如 `memory_search`）后，结果作为消息传给 subagent
3. **System Prompt 注入**：父 session 可以在 system prompt 中传递上下文

Subagent Session 结束后，结果写回父 session 的 Transcript（通过 `sessions_yield` 机制）。

**关键断裂点：** Subagent 完成前，如果父 session 被 compaction，包含 memory flush 结果的上下文可能被压缩，导致 subagent 丢失重要信息。

---

## 七、Memory Flush 机制（Compaction 前置步骤）

### 7.1 触发时机

在 Compaction（上下文压缩）**之前**，自动运行一个静默的 memory flush turn。

**源码依据：** `agent-runner.runtime-DTOpEPW0.js` 行 ~941-950（`runMemoryFlushIfNeeded`）

### 7.2 流程

```
1. Context 接近上限（或收到 context overflow 错误）
2. 调用 resolveMemoryFlushPlan(cfg) 获取 flush 配置
3. 执行静默 turn（不对用户可见）：
   → 提醒 Agent 将重要信息写入 MEMORY.md 或 memory/ 日记
4. 执行 Compaction（压缩旧消息为摘要）
5. 继续对话
```

### 7.3 Flush Plan 解析

**源码依据：** `memory-state-BXdwDW2w.js` 行 ~15-20（`resolveMemoryFlushPlan`）

Flush Plan 配置项包括：
- `reserveTokensFloor`: 保留 token 下限
- `softThresholdTokens`: 软阈值
- 其他内存策略配置

**文档依据：** `docs/concepts/memory.md` — "Before compaction summarizes your conversation, OpenClaw runs a silent turn that reminds the agent to save important context to memory files"

---

## 八、当前机制已知断裂点

### 断裂点 1：Subagent Session 不加载 MEMORY.md
- **影响：** Subagent 无法访问父 session 的长期记忆，必须通过消息传递
- **程度：** 高
- **源码依据：** `workspace-BUc4RCkE.js` 行 ~360，`filterBootstrapFilesForSession`

### 断裂点 2：Cron Session 不加载 MEMORY.md
- **影响：** 定时任务触发的 session 是"空白"上下文启动的
- **程度：** 高
- **源码依据：** 同上，`isCronSessionKey` 的判断

### 断裂点 3：memory_search 是"主动工具"而非"被动注入"
- **影响：** Agent 必须主动调用 `memory_search`，记忆才进入上下文；不调用则不记得
- **程度：** 中高（依赖于 Agent 主动行为，无法保证）
- **文档依据：** `docs/concepts/memory.md` — "The agent has two tools for working with memory"

### 断裂点 4：Subagent 结果在 Session 结束时的传递
- **影响：** Subagent 完成后的结果，如果父 session 已经 compaction 或结束，可能丢失或延迟
- **程度：** 中
- **机制：** 通过 `sessions_yield` 推送到父 session，但需要父 session 处于活跃状态

### 断裂点 5：Memory 文件变更 → 向量索引有时间差
- **影响：** 新写入的 memory 内容，在 1.5s debounce 之后才可被 `memory_search` 找到
- **程度：** 低（这是合理的设计，非 bug）

### 断裂点 6：Session 过期被清理时，memory 是否同步清理？
- **状态：** 待验证（未在源码中找到 memory 与 session 清理联动的逻辑）
- **程度：** 待验证

### 断裂点 7：Compaction 摘要内容是否写入 memory
- **状态：** 仅通过 memory flush 机制"提醒" Agent 写入，不保证写入
- **程度：** 中
- **源码依据：** `agent-runner.runtime-DTOpEPW0.js` 行 ~1030（`activeMemoryFlushPlan`）

---

## 九、关键源码文件索引

| 功能 | 文件路径 | 关键行号 |
|------|---------|---------|
| 状态目录解析 | `paths-DQgqpvCf.js` | 行 ~55-70 |
| Session 路径解析 | `paths-BC0JJAKv.js` | 行 ~10-80 |
| Session Store 读写 | `store-BxkQpm3m.js` | 行 ~201-300 |
| Session 文件持久化 | `session-file-CvpVqi4V.js` | 行 ~30-60 |
| Transcript 写入 | `sessions-DhKmXFAO.js` | 行 ~60-150 |
| Workspace 文件加载 | `workspace-BUc4RCkE.js` | 行 ~200-380 |
| Bootstrap 文件过滤 | `workspace-BUc4RCkE.js` | 行 ~360-365 |
| Memory 状态管理 | `memory-state-BXdwDW2w.js` | 全文 |
| Memory 配置解析 | `memory-search-weSJLcII.js` | 行 ~20-100 |
| Memory 向量索引 Schema | `memory-core-host-engine-storage-Dlg-rajS.js` | 行 ~90-150 |
| Memory Flush 触发 | `agent-runner.runtime-DTOpEPW0.js` | 行 ~941-950, ~1027-1033 |
| Subagent Registry 路径 | `session-utils-Jgzk2Bo-.js` | 行 ~183-187 |
| Subagent Registry 加载/保存 | `session-utils-Jgzk2Bo-.js` | 行 ~189-250 |
| Session Key 类型判断 | `session-key-4QR94Oth.js` | 全文 |
| Memory 提示注入 | `pi-embedded-bukGSgEe.js` | 行 ~83（import buildMemoryPromptSection） |
| Context Engine 注册 | `loader-BrGpIitI.js` | 行 ~17（registerMemoryPromptSection） |

---

## 十、文档参考

| 文档 | 路径 |
|------|------|
| Memory 概念总览 | `docs/concepts/memory.md` |
| Builtin 内存引擎 | `docs/concepts/memory-builtin.md` |
| Memory 配置参考 | `docs/reference/memory-config.md` |
| Session 管理深度解析 | `docs/reference/session-management-compaction.md` |
| Session 概念 | `docs/concepts/session.md` |
| Compaction 机制 | `docs/concepts/compaction.md` |
| Context Engine | `docs/concepts/context-engine.md` |

---

## 十一、待验证项

以下信息在调研中未能通过源码确认，留待进一步验证：

1. **Session 被 cleanup 时，关联的 memory chunks 是否同步清理？**
2. **Subagent session 的 transcript 具体存储在什么路径？**（subagent 有独立 sessionId，但路径解析逻辑未确认）
3. **memory_flush 的 silent turn 具体是怎样一个 LLM 调用？**（是否真的是一次 LLM 调用，还是只是系统内部逻辑）
4. **Compaction 摘要内容写入了 transcript，但有没有作为 memory 文件备份？**
5. **Session Pruning 和 Memory 系统的联动关系？**

---

## 十二、结论

OpenClaw 的记忆系统是一个**混合架构**：
- **显式持久化**：通过 Markdown 文件（`MEMORY.md`、`memory/*.md`）做到长程记忆，但依赖 Agent 主动写入
- **Transcript 持久化**：通过 JSONL 文件做到 session 级别的历史记录，但默认 30d 后清理
- **向量索引**：通过 SQLite 做到语义搜索，但需要 Agent 主动调用 `memory_search`

**核心问题**：Agent 没有"被动记忆"——记忆不会自动进入上下文，必须通过 Agent 主动写入文件或主动调用搜索工具。这使得系统行为高度依赖 Agent 的决策质量。

---

_调研完成。结论基于源码 + 官方文档，如有不确定处已在文中标注「待验证」。_
