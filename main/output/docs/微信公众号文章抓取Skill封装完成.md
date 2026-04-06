# 微信公众号文章抓取 Skill 封装完成

> 完成时间：2026-04-04
> 状态：✅ 已封装，可使用

---

## 1. 功能

从微信公众号文章链接提取：
- 文章标题
- 正文内容（纯文本）
- 实际 URL（处理重定向后）

## 2. 文件结构

```
E:\openclaw\main\skills\wechat-article-fetch\
├── SKILL.md                    # 技能说明（AI 读取）
├── package.json                # Node.js 依赖
├── node_modules\               # Playwright 依赖
└── scripts\
    └── wx-article-fetch.js     # 核心抓取脚本
```

## 3. 使用方式

### CLI 调用

```bash
node E:\openclaw\main\skills\wechat-article-fetch\scripts\wx-article-fetch.js "<url>"
```

### AI 触发

用户发送微信公众号链接并表达"抓取"、"保存"、"转笔记"意图时，AI 自动调用。

**示例：**
- "帮我抓取这篇微信文章：https://mp.weixin.qq.com/s/xxx"
- "把这个公众号文章转成笔记"

### 返回值

```json
{
  "success": true,
  "title": "文章标题",
  "content": "正文内容...",
  "url": "https://mp.weixin.qq.com/s/xxx"
}
```

## 4. 依赖

| 依赖 | 说明 |
|------|------|
| Node.js 18+ | 运行环境 |
| Playwright | 浏览器自动化（已安装） |
| Chromium | 无头浏览器（已安装） |

## 5. 测试验证

```bash
node scripts/wx-article-fetch.js "https://mp.weixin.qq.com/s/Pn_b2O6xVWk29ZjpmdXHEw"
```

**结果**：✅ 成功抓取标题和正文

## 6. 已知限制

| 限制类型 | 说明 |
|---------|------|
| 需微信登录 | 部分文章需授权，无法获取 |
| 付费内容 | 无法获取 |
| 私有公众号 | 无法获取 |
| 图片 | 目前只提取文本，图片保留原始 URL |

## 7. 技术原理

使用 Playwright 启动无头 Chromium 浏览器：
1. 访问微信文章 URL
2. 等待 JS 渲染完成
3. 从 `#js_content` 容器提取正文
4. 返回 JSON 格式结果

---

## 附录：相关文档

- 技术方案详细版：`E:\openclaw\dev\output\docs\微信公众号文章抓取技术方案.md`
