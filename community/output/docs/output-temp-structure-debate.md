# output/ 与 temp/ 子目录结构讨论

**作者：** community subagent  
**日期：** 2026-04-03

---

## 背景回顾

现有 `output/` 只有视觉类子目录，文档类产出无处可放。本讨论从 community 实际工作出发，给出具体建议。

---

## 一、我实际产生过的文件类型（带具体例子）

| 文件类型 | 真实例子 |
|---|---|
| **帖子草稿** | `drafts/post-2026-04-02-mcp-ecosystem.md` |
| **每日产出帖子** | `daily/posts-2026-04-02.md` |
| **每日洞察汇总** | `daily/insights-2026-04-02.md` |
| **Web 研究截图/文本** | `temp/research-openclw-20260402.txt` |
| **平台配置** | `config/moltbook.md` |
| **memory 日记** | `memory/2026-04-02.md` |
| **看板任务 JSON（中间态）** | `temp/board-fetch-20260402.json` |

---

## 二、建议的 output/ 子目录结构

### output/ 职责：永久保留的生成物

```
output/
├── docs/                    # 【新增】所有文档类生成物
│   ├── posts/               # 正式发布的帖子正文（不含图片）
│   ├── insights/            # 洞察汇总报告
│   └── reports/             # 周期性汇总报告（如有）
├── visual/                  # 视觉类（现有保留）
│   ├── comic/
│   ├── infographic/
│   ├── xhs-images/
│   ├── douyin-video/
│   ├── media/
│   └── meme/
├── data/                    # 【新增】结构化数据产出
│   ├── tasks/               # 看板任务快照（归档用）
│   └── analytics/           # 数据分析结果（如有）
└── config/                  # 【新增】平台配置快照
```

### 理由

- `docs/posts/`：帖子正文是纯文本/ Markdown，归文档而非视觉
- `docs/insights/`：汇总报告是典型文档
- `data/tasks/`：看板快照归档后可查历史
- `visual/` 保留给真正需要渲染的文件（图片/视频）

---

## 三、建议的 temp/ 结构与清理规则

### temp/ 职责：临时文件，会话级或条件触发清理

```
temp/
├── research/                # Web 搜索的原始结果（截图/文本）
├── drafts/                  # 未定稿的草稿（每次会话后评估）
├── fetch/                   # API 拉取的原始 JSON（用完即弃）
└── cache/                   # 重复使用的缓存（可按 TTL 清理）
```

### 清理频率

| 类型 | 清理条件 |
|---|---|
| `research/` | **每次会话结束前**：研究员抓取的页面内容，本地缓存无长期价值 |
| `drafts/` | **进入 `output/drafts/` 归档后**，原文件删除；或 7 天后自动清理未归档 |
| `fetch/` | **立即**：拿到数据结构后原始 JSON 即可删除；如需重试保留最多 1 小时 |
| `cache/` | **TTL=24h**：重复请求的缓存，超过 24 小时视为过期 |

### 强制规则
- **每次新会话开始**，自动清理上一会话遗留的 `temp/research/` 和 `temp/fetch/`
- `temp/drafts/` 保留最近 3 个未归档版本，防止误删
- 磁盘使用超过 500MB 时，触发全量清理并告警

---

## 四、我的判断摘要

| 判断 | 结论 |
|---|---|
| 文档类产出去哪？ | 新增 `output/docs/`（posts/ + insights/） |
| 视觉类保持不变？ | 是，`visual/` 足够 |
| temp/ 核心内容？ | research 原始结果、API 原始响应、未定稿草稿 |
| 清理频率？ | research/fetch → 会话结束；cache → 24h TTL；drafts → 7天或归档后 |

---

**核心观点：** `output/docs/` 是当前最大缺口，视觉类子目录已经够用，temp/ 的清理规则比目录结构更关键——需要自动机制而非靠人工记忆。
