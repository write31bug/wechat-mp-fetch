# Agent Reach 小红书渠道清理记录

**时间：** 2026-04-04 12:36 GMT+8
**操作人：** 小金
**原因：** 小红书渠道 Cookie 不互通、xhs CLI 登录态频繁过期，维护成本过高

---

## 清理范围

### 已删除

| 项目 | 路径 | 说明 |
|------|------|------|
| 小红书 CLI | `pipx uninstall xiaohongshu-cli` | xhs 命令已不存在 |
| Cookie 目录 | `C:\Users\Administrator\.xiaohongshu-cli` | ~12 KB，已删除 |
| pipx 虚拟环境 | `C:\Users\Administrator\pipx\venvs\xiaohongshu-cli` | ~226 MB，已随 CLI 卸载删除 |

### 已修改

| 文件 | 操作 |
|------|------|
| `~/.openclaw/skills/agent-reach/references/social.md` | 删除「小红书 / XiaoHongShu」章节（约50行） |
| `~/.openclaw/skills/agent-reach/SKILL.md` | 删除小红书触发词路由 |
| `E:\openclaw\main\output\docs\agent-reach安装清单.md` | 标注小红书渠道已移除 |

---

## 保留渠道（未受影响）

| 渠道 | 状态 |
|------|------|
| 抖音 | ✅ 正常 |
| Twitter/X | ✅ 正常 |
| 微博 | ✅ 正常 |
| B站 | ✅ 正常 |
| V2EX | ✅ 正常 |
| Reddit | ✅ 正常 |
| 雪球 | ✅ 正常 |
| 微信公众号 | ✅ 正常 |
| RSS/Atom | ✅ 正常 |
| Exa 全网搜索 | ✅ 正常 |

---

## 备份文件

如需恢复，从以下文件提取：

- `E:\openclaw\main\temp\agent-reach-social-backup.md` — social.md 原始内容
- `E:\openclaw\main\temp\agent-reach-skill-backup.md` — SKILL.md 原始内容

---

## 恢复方式（如需）

如需重新接入小红书，执行以下步骤：

```bash
# 1. 安装 CLI
pipx install xiaohongshu-cli

# 2. 登录授权
xhs login

# 3. 恢复 Skill 文件
# 从备份文件中还原 social.md 小红书章节和 SKILL.md 触发词

# 4. 更新安装清单
# 还原 agent-reach安装清单.md 中的小红书行
```

---

## 清理原因说明

小红书渠道在当前环境下存在以下问题：

1. **Cookie 不互通**：xhs CLI 需要从标准 Chrome profile 读取加密 Cookie，但 baoyu-skills 使用独立 profile，已登录状态下 Cookie value 为空
2. **xhs login QR 码登录失败**：GBK 控制台编码问题 + GitHub API 限速（camoufox 下载 addon 时 403）
3. **登录态有效期短**：session 频繁过期，维护成本高

**决策：** 暂时移除小红书渠道，保留其他稳定渠道。如后续有更好的方案再考虑恢复。
