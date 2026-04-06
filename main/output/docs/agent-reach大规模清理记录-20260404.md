# Agent Reach 渠道大规模清理记录

**时间：** 2026-04-04 12:48 GMT+8
**操作人：** 小金
**原因：** 多渠道工具未安装或无法稳定使用，清理避免误导

---

## 清理总览

本次共清理 **7 个渠道**，均已从 Skill 文档和配置中移除。

| 渠道 | 清理方式 | 涉及文件 |
|------|---------|---------|
| Twitter/X | 卸载 pipx（无实际安装）+ 文档删除 | social.md, SKILL.md, 安装清单 |
| 微博 | mcporter weibo 无独立配置 + 文档删除 | social.md, SKILL.md, 安装清单 |
| Reddit | pipx rdt-cli 无安装 + 文档删除 | social.md, SKILL.md, 安装清单 |
| 微信公众号 | mcporter exa 已卸载 + 文档删除 | web.md, search.md, SKILL.md, mcporter.json, 安装清单 |
| YouTube | 工具保留（B站共用 yt-dlp）+ 文档删除 | video.md, SKILL.md, 安装清单 |
| 小宇宙播客 | 工具不存在 + 文档删除 | video.md, SKILL.md, 安装清单 |
| Exa 全网搜索 | mcporter exa 已卸载 | mcporter.json, search.md, 安装清单 |

---

## 各渠道详细说明

### Twitter/X
- **pipx uninstall twitter-cli**：无实际安装，无需操作
- **文档清理**：删除 `references/social.md` 中「Twitter/X」章节（~35行）
- **触发词移除**：`twitter/推特/x.com/推文`

### 微博
- **mcporter**：weibo 未在 mcporter.json 中注册，无需操作
- **文档清理**：删除 `references/social.md` 中「微博/Weibo」章节

### Reddit
- **pipx uninstall rdt-cli**：无实际安装，无需操作
- **文档清理**：删除 `references/social.md` 中「Reddit」章节

### 微信公众号
- **mcporter exa**：从 `~/.mcporter/mcporter.json` 移除 exa 配置
- **文档清理**：删除 `references/web.md` 中「微信公众号/WeChat Articles」章节；清空 `references/search.md` 中 Exa 内容

### YouTube
- **yt-dlp**：保留（B站共用 yt-dlp，删除会影响 B站渠道）
- **文档清理**：删除 `references/video.md` 中 YouTube 章节；删除选择指南中的 YouTube 行

### 小宇宙播客
- **工具不存在**：`~/.agent-reach/tools/xiaoyuzhou/transcribe.sh` 不存在，无需卸载
- **文档清理**：删除 `references/video.md` 中「小宇宙播客」章节；删除选择指南中的播客转录行

### Exa 全网搜索
- **mcporter exa**：已从 mcporter.json 移除
- **文档清理**：清空 `references/search.md`，改为说明通用搜索方式

---

## 当前保留渠道

| 渠道 | 状态 | 备注 |
|------|------|------|
| 雪球 | ✅ 正常 | 有 Cookie |
| B站 | ✅ 正常 | yt-dlp（2026.03.17） |
| V2EX | ✅ 正常 | 公开 API，无需认证 |
| RSS/Atom | ✅ 正常 | feedparser |
| 任意网页 | ✅ 正常 | Jina Reader |

---

## 备份文件清单

| 文件 | 内容 |
|------|------|
| `E:\openclaw\main\temp\agent-reach-social-backup.md` | social.md（含小红书+抖音） |
| `E:\openclaw\main\temp\agent-reach-video-backup.md` | video.md（含抖音+YouTube+小宇宙） |
| `E:\openclaw\main\temp\agent-reach-skill-v2-backup.md` | SKILL.md（含抖音） |
| `E:\openclaw\main\temp\agent-reach-social-v3-backup.md` | social.md（含 Twitter/微博/Reddit） |
| `E:\openclaw\main\temp\agent-reach-skill-v3-backup.md` | SKILL.md（含各渠道完整触发词） |
| `E:\openclaw\main\temp\agent-reach-install-doc-backup.md` | 安装清单原始版 |

---

## 决策原因

- **微博**：无独立 CLI/MCP，文档与实际不符
- **Reddit**：rdt-cli 未安装，文档与实际不符
- **微信公众号**：依赖 Exa MCP，Exa 已卸载；Jina Reader 无法读微信（被 CAPTCHA 拦截）
- **YouTube**：yt-dlp 保留给 B站使用
- **小宇宙播客**：工具不存在，无恢复必要
- **Exa**：依赖微信公众号场景，微信公众号已移除
