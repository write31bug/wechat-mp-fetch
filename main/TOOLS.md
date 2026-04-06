# TOOLS.md - Local Notes

## 微信消息格式规范

通过微信发送时，格式要求：
- ❌ 不用 Markdown 表格
- ❌ 不用 `#` 标题
- ✅ 用 `•` 或 `-` 列表
- ✅ 用 **粗体** 或 CAPS 强调
- ✅ 链接用 `<>` 包裹

## 打开桌面微信

- 桌面快捷方式名称：`΢�ſ����߹���.lnk`（显示为"微信开发者工具"）
- 方式：Shell.Application 遍历桌面项，匹配名称含 `΢` 或 `WeChat` 的项目，然后 InvokeVerb("打开(&O)")

## 截图工具

- `E:\openclaw\main\tools\Snap.exe` — 全屏截图（2560x1440，DPI 125% 下仍完整）
- 用法：直接告诉我"截图"，我执行 Snap.exe 后用 image 工具分析
- 适用：读取浏览器页面内容、验证界面状态

## 历史上的今天

- 数据源：Tavily 搜索
- 用法：每天 9 点自动查，也可以随时问「今天历史上发生了什么」
- 展示：选取 2-3 条有代表性的历史大事件

## MiniMax Token 查询

- 网址：`https://platform.minimaxi.com/user-center/payment/token-plan`
- 流程：cmd → `start <url>` → 等待加载 → Snap.exe 截图 → image 工具读取
- 当前套餐：Starter 月度（600次/5小时窗口，2026-04-16 到期）

## 信息准确性红线（金哥要求）

处理新闻/信息时必须遵守：

- **官方/权威来源 + 正式发布** → 可直接陈述
- **传闘/拟议/征求意见/尚未正式确认** → 必须标注"传闘/消息显示/尚未确认"，禁止直接当事实陈述
- **搜不到确切来源** → 说"没找到确切出处，不确定"
- 禁止用"据说" → 应改为"有报道显示"
- 不确定的信息宁可说"查不到确切来源"，也不拼凑结论

> 这条规则优先级高于其他表达习惯，发现不确定信息时必须主动标注。

## 网页搜索工具优先级

**搜索顺序（优先级从高到低）：**
1. **Serper** → Google 搜索 API，速度快，额度多（2500次/月）
2. **Tavily** → AI 优化搜索，结构化结果
3. **web_fetch** → 兜底方案，适合简单页面文本提取

**注意：** 微信公众号/需要 JS 渲染的页面，用 `baoyu-url-to-markdown`（Chrome 渲染）而非 `web_fetch`

**触发规则：**
- "搜索 XX" / "查一下 XX" → 按优先级依次尝试（Serper → Tavily → web_fetch）
- "Google搜索 XX" / "帮我用 Google 查一下" → 直接用 Serper（`skills/serper-search/scripts/search.py`）
- "帮我看看这个网页" + URL → `baoyu-url-to-markdown`

## Why Separate?

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

## Skill 配置存放规则

详见 AGENTS.md - 文件目录规范 / Skill 配置存放规则（config/skills）。

**补充注意事项：**
- `.env` 和 `skills\` 同级，都放在 `config\` 下

## Gateway 重启脚本

**路径：** `E:\openclaw\main\scripts\restart.bat`

**正确方式：用 `Invoke-Item`（模拟双击），不能用 `exec` 直接调用**

原因：`exec` 会触发 gateway 停止，当前 session 断连报错"missing tool result"。`Invoke-Item` 通过 Shell 打开文件，不影响当前 session。

PowerShell 执行：
```
Invoke-Item E:\openclaw\main\scripts\restart.bat
```

原理：脚本内用 `start /wait cmd /c` 新开独立子窗口执行 stop/start，不影响调用者。

**注意：这是手动脚本，不适合放进 cron 自动任务。**
