# output/ 和 temp/ 子目录结构讨论

**讨论人：** dev subagent  
**日期：** 2026-04-03  
**背景：** 现有规则 output/ 只有视觉类子目录，文档类产出无处可放，实际执行失败。

---

## 一、我实际产生的文件类型（具体例子）

### 1. 文档类（Markdown/纯文本）
- 技术方案 / 架构文档（例：`parallel-board-fields-tech-review.md`）
- 每日记忆（例：`memory/2026-04-01.md`）
- 研究报告（例：`memory/claude-code-phase1-deep-study.md`）
- 会议记录 / 讨论记录
- 学习计划（例：`memory/learning-plan-v3.md`）
- 任务交付说明

### 2. 代码类
- Python 脚本（例：`T008_�ֲ�ͼ��.py` — 任务看板调用脚本）
- Shell / PowerShell 脚本
- SQL 文件（建表语句）
- JSON / YAML 配置文件（API schema、plugin config）

### 3. 数据类
- JSON 数据文件（智能表格导出、API 响应样本）
- SQLite 数据库文件（看板：`E:\openclaw\tasks\board.db`）
- CSV / 日志文件

### 4. 报告类
- HTML 测试报告
- Markdown 格式的 Code Review 报告
- 交付清单

### 5. 视觉类（已有归属）
- 图片 / 梗图（现有 meme/）
- 信息图 / 漫画（现有 infographic/, comic/）

---

## 二、output/ 子目录划分方案

**原则：按"内容类型"分，不按"发布平台"分**

| 文件类型 | 目标目录 | 说明 |
|---------|---------|------|
| 技术文档、方案、报告、会议记录、学习计划 | `output/docs/` | 文字类永久产物，**已有但规则未明确** |
| Python / Shell / SQL 脚本，配置文件 | `output/code/` | 可执行的代码产物 |
| JSON / CSV / 数据库导出 | `output/data/` | 结构化数据 |
| HTML 测试报告 | `output/reports/` | 自动化产物 |
| 图片、信息图、梗图、视频 | `output/media/` | 视觉类（合并 comic/infographic/meme/xhs-images/douyin-video） |
| memory/ 中的研究文档、报告 | `output/docs/` | memory/ 是工作态笔记，完成后可归档到 docs/ |

**推荐结构：**

```
output/
├── docs/           # 文档（技术方案/报告/会议记录/学习计划）
├── code/           # 代码脚本
├── data/           # 结构化数据
├── reports/        # 测试报告/分析报告
└── media/          # 视觉类（合并所有视觉子目录）
```

**不支持把 `docs/` 再按"谁写的"拆分**——统一归宿，按文件名区分。

---

## 三、temp/ 的定义与清理机制

### 什么放 temp/

| 文件类型 | 举例 | 清理时机 |
|---------|------|---------|
| 单次会话的调试日志 | `*.log`、`debug_*.txt` | 会话结束 |
| AI 多轮对话草稿（未形成最终版本） | `draft_v1.md`、`draft_v2.md` | 会话结束或最终版归档后 |
| 一次性脚本的执行输出（不需保留的） | `fetch_result.json`（随手拉的 API 数据） | 下一个会话开始前 |
| 截图 / 临时图片（未审核） | `temp_screenshot.png` | 3 天后或会话结束 |

### 清理规则

- **每次会话开始前**：清空上一会话遗留的 temp/ 文件
- **清理条件**（满足任一即触发）：
  1. 文件修改时间超过 7 天
  2. 新会话启动时
  3. 文件名匹配 `draft_*`、`debug_*`、`temp_*`、`*.tmp`
- **例外不删**：`temp/.gitkeep`

### temp/ 和 docs/ 的边界

如果一个草稿经过审核成为正式文档，**手动移动到 `output/docs/`**，不要依赖自动清理。temp/ 是"用完即弃"，docs/ 是"有意保留"。

---

## 四、memory/ 的定位

memory/ 是**工作态笔记**，不是最终产物。当前规则把 memory/ 独立于 output/ 和 temp/ 之外是合理的，但需要说明：

- `memory/YYYY-MM-DD.md` — 当天工作记录，每天新建，会话结束后更新
- `memory/*.md`（不含日期的）— 研究文档、长期学习笔记，**完成后应移动到 `output/docs/`**，避免 memory/ 膨胀

---

## 五、命名规范（推荐）

格式：`{类型}_{简短描述}_{日期或版本}`

示例：
- `docs_架构方案_v1_20260403.md`
- `code_任务看板脚本.py`
- `data_智能表格导出_20260403.json`
- `draft_待审核方案_v2.md`

不强制，但推荐，有助于检索。

---

## 六、结论

**核心问题：** `docs/` 已存在但规则未明确，导致文档产物仍然散落或堆在根目录。

**最小改动方案：**
1. 在 AGENTS.md 中明确 `output/docs/` 的定义（技术文档、报告、方案）
2. 新增 `output/code/`、`output/data/`、`output/reports/` 三个子目录
3. temp/ 清理规则写清楚（7天 or 会话切换时）
4. memory/ 中完成态文档建议手动归档 docs/

**不要做的事：** 按"发布平台"建子目录（xhs-images/douyin-video），同一素材多平台复用时版本会乱。
