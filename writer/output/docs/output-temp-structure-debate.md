# output/ 和 temp/ 子文件夹结构讨论

## 现状问题

当前 `output/` 只有视觉类子目录，文档类产出要么散落在根目录（乱），要么挤进 `docs/`（不规范）。同时 `temp/` 根本没人用，临时文件散落在根目录。

---

## 一、我实际产生过的文件类型（按产出频率排序）

| 类型 | 具体例子 | 特征 |
|------|---------|------|
| **Markdown 文档** | `parallel-board-fields-draft.md`、`workspace-rule-discussion.md` | 中间产物或最终交付，需要版本管理 |
| **Word 文档** | `洞察框架.docx` | 最终交付物，跨平台流通 |
| **调查/研究报告** | `T008_某Q1Q2调查报告.md` | 重要产出，有长期查阅价值 |
| **会议记录** | `parallel-board-meeting-notes.md` | 团队协作产物，需要存档 |
| **Python 脚本** | `complete_t008.py`、`temp_t008.py` | 工具类，放在根目录极乱 |
| **原始数据/附件** | 从企业微信拉取的 JSON、日程数据 | 中间态，需要临时存储 |

---

## 二、建议的 output/ 子目录结构

```
output/
├── docs/                 # 【已有】文档类根目录
│   ├── drafts/           # 草稿（可覆盖，不算正式产出）
│   ├── final/            # 正式交付文档（Word/Markdown）
│   ├── research/         # 调查报告、竞品分析、行业研究
│   ├── meeting-notes/    # 会议记录（时间戳命名）
│   └── specs/            # 需求文档、方案设计
├── comic/                # 【已有】漫画
├── infographic/          # 【已有】信息图
├── xhs-images/           # 【已有】小红书图片
├── douyin-video/         # 【已有】抖音视频
├── media/                # 【已有】通用媒体资产
├── meme/                 # 【已有】表情包
└── slides/               # 【已有】演示文稿
```

**关键原则：**
- `docs/` 按**内容类型**分，不按平台分（平台分发是发布环节的事，不是存储结构）
- `drafts/` 放草稿同一篇文档的 v1/v2/v3，允许覆盖
- `final/` 放金哥确认过的最终版

---

## 三、建议的 temp/ 结构

```
temp/
├── drafts/               # 写作中间版本（未确认的草稿段落）
├── cache/                # API 响应、数据抓取的缓存（可重新请求生成）
├── scratch/              # 临时测试脚本、一次性 Python 文件
├── images/               # AI 生成的图片初稿（确认后再移入 output/）
└── exports/              # 导出中间文件（如 pandoc 临时 HTML）
```

**清理规则：**

| 类型 | 清理时机 |
|------|---------|
| API 缓存、临时脚本 | **每次会话结束前**自动清理 |
| 图片初稿 | **确认采用后**立即移入 output/，未采用的会话末清 |
| 导出中间文件 | 导出完成后立即清理 |
| drafts/ 中草稿 | 下一会话开始时提示"上次的 drafts 还在，是否清理？" |

---

## 四、根目录散落文件的修复

以下文件应该迁移：

| 当前路径 | 建议去处 |
|---------|---------|
| `output/洞察框架.md` | `output/docs/final/洞察框架.md` |
| `output/洞察框架.docx` | `output/docs/final/洞察框架.docx` |
| `output/T008_某Q1Q2调查报告.md` | `output/docs/research/T008_某Q1Q2调查报告.md` |
| `complete_t008.py` | `output/docs/research/`（与调查报告绑定）或 `temp/scratch/` |
| `temp_t008.py` | `temp/scratch/`（本身就是临时文件命名） |

---

## 五、我的立场

**文档类产出必须进 `output/docs/`，且需要按内容类型分子目录。**

当前 `docs/` 只是个无结构的文件夹，实际操作中大家还是往根目录扔。问题不在于没有 `docs/`，而在于 `docs/` 没有子目录规范，导致没有约束力。

建议金哥在 AGENTS.md 里明确 `docs/` 的子目录结构，并把根目录现有的散落文件做一次清理归档。
