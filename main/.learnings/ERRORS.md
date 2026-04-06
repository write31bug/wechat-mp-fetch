# ERRORS.md

Errors, failures, and exceptions encountered during development.

**Statuses**: pending | in_progress | resolved | wont_fix | promoted

---

## [ERR-20260403-002] gateway restart 方案设计失败（kill schtasks self-destruct）

**Logged**: 2026-04-03T13:44:00+08:00
**Priority**: critical
**Status**: wont_fix
**Area**: infra

### Summary
设计了「创建 schtasks 辅助任务来杀 gateway」的方案，但执行时仍然通过 exec 发出 kill 命令，导致 gateway 被杀后 CLI session 也跟着断开，工具返回错误。连续失败两次。

### Root Cause
任何通过 exec 发出的 kill 命令，只要目标进程是当前连接着的 gateway，都会导致 CLI 连接断开。这是因为进程树结构：gateway 是通过 schtasks 的 PowerShell wrapper 拉起的 node.exe 进程，杀掉它会连带断开所有连接 gateway 的 named pipe / WebSocket 客户端（包括当前 session）。

### Errors Observed
```
[openclaw] missing tool result in session history; inserted synthetic error result for transcript repair.
```

### Context
- 尝试1：直接执行 `python restart_gateway.py` → 失败
- 尝试2：写 schtasks 辅助任务 `OpenClaw-Gateway-Restart`，通过 exec 触发 `schtasks /Run /TN ...` → 失败
- 尝试3：写 PowerShell 脚本 `kill_gateway.ps1`，通过 exec 执行 → 失败
- 尝试4：改用 `schtasks /Change` 修改任务 → 失败
- 所有方案都在 exec 发命令，gateway 被杀后 exec 连接断开

### Why "Fix" via cron didn't work either
cron isolated session 也是通过 gateway 转发命令的，杀掉 gateway 后 cron 命令也传不到。

### Suggested Fix
**没有自动化方案能绕过这个限制。** 唯一可行的方式是让用户手动在 PowerShell（独立于 gateway 的终端）里执行 schtasks 命令。

**总结教训：**
1. 不要设计任何「通过 exec 发 kill 命令杀掉 gateway」的方案
2. gateway restart 属于「破坏自身连接」的操作，必须用户手动执行
3. 正确做法：用户打开一个独立 PowerShell 窗口执行 `schtasks /Run /TN "OpenClaw Gateway"`，不经过 CLI

### Metadata
- Reproducible: yes
- Related Files: E:\openclaw\main\scripts\kill_gateway.cmd, kill_gateway.ps1, restart_gateway.py
- All deleted: 2026-04-03T13:44:00+08:00
- See Also: ERR-20260403-001, LRN-20260403-004

---
