# Skill 健康报告

**任务：** T-D-002  
**状态：** ✅ DONE  
**生成时间：** 2026-04-05  
**检查范围：** `E:\openclaw\main\skills\` 下全部 skill（共 29 个）

---

## 概览

| 状态 | 数量 | 说明 |
|------|------|------|
| ✅ 正常 | 21 | 有 SKILL.md，描述清晰，有实际功能 |
| ⚠️ 警告 | 5 | 有问题或需要关注 |
| 🔴 异常 | 3 | 功能异常或重复 |

---

## 各 Skill 详情

### ✅ 正常（可用）

| Skill | 用途 | 评价 |
|-------|------|------|
| baoyu-imagine | AI 图片生成（多 API） | 主力工具，配置完整 |
| baoyu-translate | 文章翻译 | 三个模式（快/常/精），有术语表支持 |
| baoyu-cover-image | 封面图生成 | 五维生成法，实用 |
| baoyu-infographic | 信息图生成 | 21种布局+20种风格，完整 |
| baoyu-comic | 知识漫画生成 | 面板布局清晰，支持多风格 |
| baoyu-xhs-images | 小红书图片生成 | 11种视觉风格+8种布局 |
| baoyu-slide-deck | PPT/幻灯片生成 | 有输出结构规范 |
| baoyu-markdown-to-html | MD 转 HTML | 支持代码高亮/PlantUML/脚注 |
| baoyu-post-to-wechat | 公众号发布 | 支持三种格式，CDP 发布 |
| baoyu-post-to-weibo | 微博发布 | 头条文章+普通微博 |
| baoyu-post-to-x | X (Twitter) 发布 | 支持 X Article |
| baoyu-url-to-markdown | 网页转 MD | Chrome CDP 渲染，支持 JS 页面 |
| baoyu-youtube-transcript | YouTube 字幕/封面 | 多语言+翻译+章节 |
| baoyu-format-markdown | MD 格式化 | 有 frontmatter、标题、代码块 |
| baoyu-article-illustrator | 文章配图 | Type×Style 二维矩阵 |
| baoyu-compress-image | 图片压缩 | WebP/PNG 自动选择 |
| serper-search | Google 搜索 | Serper API，速快 |
| skill-vetter | Skill 安全审查 | 安装前检查 |
| self-improving-agent | 自我改进 | 记录学习教训 |
| humanizer | 去 AI 味 | 去除 AI 写作特征 |
| find-skill | 搜索 ClawHub | 发现新 skill |

### ⚠️ 警告（需关注）

| Skill | 问题 | 建议 |
|-------|------|------|
| baoyu-image-gen | SKILL.md 存在但标注为 DEPRECATED，指向 baoyu-imagine | 建议卸载或标注为 baoyu-imagine 的别名 |
| eastmoney | 安装失败（clawhub 校验问题），需 web search 兜底 | 等待 skill 修复或手动安装 |
| mcp-client | 文档较少，仅一个 SKILL.md | 需补充使用文档 |
| openclaw-agent-browser-clawdbot | ⚠️ **依赖未装**：`agent-browser` CLI 需要 `npm install -g agent-browser` | 需在目标机器安装，或在 skill 文档中注明前置依赖 |
| baoyu-danger-gemini-web | 反向工程 Gemini Web API，可能有法律/合规风险 | 建议仅用于开发测试，不用于生产 |

### 🔴 异常

| Skill | 问题 | 建议 |
|-------|------|------|
| baoyu-danger-x-to-markdown | X (Twitter) 反向工程 API，有合规风险 | 同上，谨慎使用 |
| wechat-mp-fetch | 微信公众号抓取需要微信授权，技术上无法完全绕过 | 只能抓取公开文章，付费/授权内容无法访问 |
| wechat-search-release | 名称带有 release，可能和 wechat-mp-fetch 是同一 skill 的变种 | 建议合并 |

---

## 重复 Skill 整理

```
内容发布类（重复）:
  baoyu-post-to-wechat  ← ✅ 正常
  baoyu-post-to-weibo
  baoyu-post-to-x
  
图片生成类（重复）:
  baoyu-image-gen      ← DEPRECATED，别名 baoyu-imagine
  baoyu-imagine       ← ✅ 正常

微信相关（重复/互补）:
  wechat-mp-fetch      ← 抓取（有限制）
  wechat-search-release ← 可能是 wechat-mp-fetch 的打包版

危险类（标注清晰）:
  baoyu-danger-gemini-web
  baoyu-danger-x-to-markdown
```

---

## 关键风险

1. **agent-browser 未安装**：`openclaw-agent-browser-clawdbot` 依赖全局 CLI，但未预装。解决方案：在安装 skill 时附带依赖检查脚本。
2. **eastmoney 安装失败**：clawhub 安装校验失败，需要手动处理或等官方修复。
3. **微信文章抓取有限制**：wechat-mp-fetch 只能抓公开文章，付费内容无法访问，需告知用户预期。

---

## 建议行动

**立即可做：**
- [ ] 卸载 `baoyu-image-gen`（DEPRECATED）
- [ ] 在 `openclaw-agent-browser-clawdbot` SKILL.md 顶部加前置依赖说明
- [ ] 合并 `wechat-search-release` 到 `wechat-mp-fetch`（如确认重复）

**后续优化：**
- [ ] 给 `mcp-client` 补充完整使用文档
- [ ] 给所有 baoyu-* skill 统一加版本号，方便升级管理
- [ ] 考虑做一个「skill 安装健康检查」脚本，自动检测依赖是否满足
