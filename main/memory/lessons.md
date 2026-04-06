# lessons.md - 踩坑记录

按严重程度分级：D = 已解决/不会再犯，C = 需留意，B = 重要，A = 反复踩过

---

## A-1: exec 对 TTY/服务管理命令有限制

**问题：** 遇到需要 gateway 重启等需要 TTY 或服务管理的命令时，exec 一直返回"missing tool result"或失败，但我没有意识到这是 session 权限问题，反复试同一类命令。

**教训：**
- exec 在 capabilities=none 的 runtime 下对需要 TTY 的命令（interactive CLI、service management）有限制
- 遇到同类问题失败两次后必须换方向，不能循环试
- `openclaw gateway restart` 这类命令需要交互式终端，exec 跑不通应该直接告知用户手动执行
- 遇到 `elevated is not available` 时，说明当前 session 没有提权，不能反复试 elevated 方式

**D / 2026-03-30**

---

## A-2: Gateway 重启必须用 Invoke-Item，不能用 exec

**问题（2026-04-03）：** 用 `exec` 调用 restart.bat，gateway 停止时当前 session 断连，报错"missing tool result"

**根本原因：** gateway 停止 → 当前 agent session 中断 → tool result 丢失

**正确方式：** 用 PowerShell `Invoke-Item`（模拟双击），不走 exec 路径
```powershell
Invoke-Item E:\openclaw\main\scripts\restart.bat
```

**教训：** 涉及服务重启的命令，不能用 exec，要用 Invoke-Item 模拟人工操作。

**D / 2026-04-03**

---

## B-1: PowerShell 编码问题

**问题：** 写 JSON 时用 PowerShell 的 `ConvertTo-Json` 输出中文会乱码（GBK 编码问题），导致 xyyyan 的名字写入失败。

**教训：**
- PowerShell 直接写 JSON 到文件时避免中文，用 Python 更可靠
- 验证写入结果时用文件读取而不是直接 print

**D / 2026-03-30**

---

## C-1: 确认优于执行

**问题：** 今天在 gateway 重启这件事上，没有先确认配置文件是否正确就开始反复尝试重启，浪费了很多轮。

**教训：**
- 先确认现状（配置/状态），再判断需要什么操作
- 不要在不确定的情况下反复执行同一类操作

**D / 2026-03-30**
