# 2026-04-06 额外任务研究记录

## 任务①：Claude Code 实战踩坑记录

**工具状态：** `npx @anthropic-ai/claude-code` 版本 2.1.92，已安装但未登录

**踩坑点：**

1. **必须登录，无法绕过**
   - 即使使用 `--bare` 和 `--dangerously-skip-permissions` 组合，依然提示 `Not logged in · Please run /login`
   - 这意味着在 subagent 环境中，Claude Code CLI **无法直接使用**
   - 可能的解法：需要预先配置 `~/.claude/settings.json` 或环境变量认证，但当前 session 没有配置

2. **MCP 工具链研究价值有限**
   - 之前对 Claude Code MCP 工具链的研究（读文件、执行命令等）在 subagent 环境里无法实际调用
   - 实际上只有在**本地已登录 Claude Code 的桌面环境**才能作为 MCP server 使用

**结论：** Claude Code 在 subagent 中无法使用，待有桌面环境再说。已有的 Claude Code MCP 工具链研究笔记是理论储备，实际发挥要等金哥本地环境。

---

## 任务④：MiniMax API 限速问题研究（2062 错误）

**核心发现：**

### 1. 2062 不是 MiniMax 标准错误码

MiniMax 官方标准错误码（来自 platform.minimax.io/docs/api-reference/errorcode）：

| 错误码 | 含义 |
|--------|------|
| 10001-10006 | 特定参数/字段校验错误 |
| 10011 | 模型不支持 |
| 1002 | **rate limit（标准限速代码）** |
| 1003 | 无余额/配额耗尽 |

**2062 不在标准列表中**。可能来源：
- MiniMax 代理商/中间层（通过 MiniMax portal）的私有错误码
- 需要查 MiniMax portal 专属错误码文档

### 2. OpenClaw 限速检测机制

**`isApiKeyRateLimitError()`** 只检查错误消息字符串：
```typescript
if (lower.includes("rate_limit")) return true;
if (lower.includes("rate limit")) return true;
if (lower.includes("429")) return true;
// ... (无 2062)
```

**问题：** 如果 2062 不出现在错误消息的文本中，当前检测机制会**漏掉这个限速**，导致 profile 不会进入 cooldown 状态

### 3. 正确的 failover 机制

OpenClaw 的 rate limit failover 依赖 `classifyFailoverReasonFromSymbolicCode()`，支持：
- `RATE_LIMIT`
- `RATE_LIMIT_EXCEEDED`  
- `TOO_MANY_REQUESTS`
- HTTP 429

如果 MiniMax portal 返回的错误包含这些关键字，就能正确 failover

### 4. MiniMax 实际限速额度

- **MiniMax-M2.7：500 RPM（请求/分钟），20M TPM**
- 配额相当充足，触发限速说明并发量大

### 5. 建议：规避 subagent 并发限速

在 `E:\openclaw\.openclaw\openclaw.json` 中已有 fallback 配置：

```json
"default_model": "minimax-portal/MiniMax-M2.7",
"fallback_models": [
  { "model": "modelstudio/qwen/qwen-Plus-200k", ... },
  { "model": "modelstudio/zhipu/glm-4-flash", ... }
]
```

**实际可行的规避策略：**
1. 确认 2062 是否是 MiniMax portal 专属错误码，若是则提 bug 到 OpenClaw repo（`isApiKeyRateLimitError` 应补充检测 2062）
2. 如果 2062 是中间层返回的，错误消息中是否包含 "rate_limit" 或 "quota" 等关键字？
3. 增加更多 fallback model 数量，减少对 MiniMax portal 的单点依赖
4. 考虑给 subagent 设置 `model: "modelstudio/..."` 来完全绕过 MiniMax portal

---

**附：MiniMax portal 相关文件**
- `src/agents/live-auth-keys.ts` - 限速检测（isApiKeyRateLimitError）
- `src/agents/failover-error.ts` - 错误分类和 failover 状态机
- `src/agents/auth-profiles/usage.ts` - profile cooldown 机制
- `src/infra/provider-usage.fetch.minimax.ts` - MiniMax 用量获取 API
