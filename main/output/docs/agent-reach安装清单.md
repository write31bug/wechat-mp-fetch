# Agent Reach 安装清单

## 概述

agent-reach 多平台内容读取工具集。安装于 2026-04-04，最新清理 2026-04-04 13:03。

## 渠道状态

| 渠道 | 功能 | 状态 | 需要 Cookie |
|------|------|------|-------------|
| 雪球 | 股票行情/热帖 | ✅ 可用 | 是（已配置） |
| B站 | 视频元数据/字幕 | ✅ 可用 | 否 |
| RSS/Atom | 订阅源读取 | ✅ 可用 | 否 |
| 任意网页 | Jina Reader 抓取 | ✅ 可用 | 否 |
| 小红书 | 搜索/阅读/评论 | ❌ 已移除（2026-04-04） | — |
| 抖音 | 视频解析 | ❌ 已移除（2026-04-04） | — |
| Twitter/X | 时间线/推文/搜索 | ❌ 已移除（2026-04-04） | — |
| 微博 | 热搜/动态 | ❌ 已移除（2026-04-04） | — |
| Reddit | 帖子/评论/搜索 | ❌ 已移除（2026-04-04） | — |
| 微信公众号 | 搜索+阅读 | ❌ 已移除（2026-04-04） | — |
| YouTube | 字幕/评论/元数据 | ❌ 已移除（2026-04-04） | — |
| 小宇宙播客 | 转录 | ❌ 已移除（2026-04-04） | — |
| V2EX | 热门/节点/主题/回复 | ❌ 已移除（2026-04-04 13:03） | — |

## 文件清单

| 类别 | 内容 | 路径 | 大小 |
|------|------|------|------|
| Python 工具包 | agent-reach 1.4.0 | `C:\Users\Administrator\AppData\Local\Programs\Python\Python312\Lib\site-packages\agent_reach` | ~1 MB |
| 雪球 Cookie | 登录态 | `C:\Users\Administrator\.agent-reach` | ~2 KB |
| Skill 指南 | Agent Reach SKILL.md | `C:\Users\Administrator\.openclaw\skills\agent-reach` | ~15 KB |

## 重要路径说明

- **全部不在工作区**（`E:\openclaw\main\`），位于用户目录下
- **核心配置**：Cookie 文件最重要，丢了需要重新导出登录态
- **Skill 目录**：`C:\Users\Administrator\.openclaw\skills\agent-reach` 已注册到 OpenClaw

## 故障排查

| 问题 | 解决方案 |
|------|---------|
| 雪球行情返回空 | Cookie 过期或无效，重新导出 |
| 命令输出乱码 | Windows 终端 GBK 编码问题，不影响功能，用 `--json` 参数 |

## 常用命令

```bash
# 雪球股票行情
python -c "from agent_reach.channels.xueqiu import XueqiuChannel; print(XueqiuChannel().get_stock_quote('SH600519'))"

# 检查 Agent Reach 状态
agent-reach doctor
```
