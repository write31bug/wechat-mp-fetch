# output/ 和 temp/ 子目录结构讨论

**Author:** finance subagent
**Date:** 2026-04-03

---

## 一、背景

现有 `output/` 只有视觉类子目录（comic/infographic/xhs-images/douyin-video/media/meme），但 Agent 的产出远不止图片，还包括大量文档类、数据类文件，无处可放，导致实践中完全无法执行。

---

## 二、我（finance agent）实际产生过的文件类型

| 文件类型 | 具体例子 |
|---|---|
| **Markdown 分析报告** | `2026-03-28-宁德时代分析.md`、`2026-04-02-光伏板块周报.md` |
| **JSON 数据文件** | `stock_quotes_20260328.json`、`tushare_fetch_20260401.json` |
| **CSV 数据导出** | `持仓明细_20260325.csv`、`基金净值历史.csv` |
| **Excel 文件** | `估值对比表.xlsx`、`财务指标汇总.xlsx` |
| **图片/图表** | K线截图、MACD图、板块资金流向图（由搜索或爬取得来） |
| **HTML 临时页面** | 行情页面抓取的临时缓存 |
| **Txt 日志** | 爬虫/抓取过程的 debug log |
| **PDF** | 研报下载、招股书等 |
| **Memoy 日记** | `memory/2026-03-28.md` 等每日工作记录 |

---

## 三、output/ 子目录建议

### 方案：按「内容性质」+ 「媒介形式」混合划分

```
output/
├── docs/              # 文字类生成物（核心新增）
│   ├── analysis/      # 分析报告（Markdown 为主）
│   ├── data/          # 结构化数据文件（CSV/JSON/Excel）
│   └── research/      # 研究资料（PDF/HTML 研报等）
├── visual/            # 视觉类（原有改名，更清晰）
│   ├── comic/
│   ├── infographic/
│   ├── xhs-images/
│   ├── douyin-video/
│   └── meme/
├── images/            # 非创作性截图/照片（K线图等分析附图）
└── memory/            # 每日工作记录（memory/ 里的东西本质是生成物）
```

### 说明

- **`docs/analysis/`**：存放最终交付的分析报告，一个主题一个文件，如 `宁德时代-20260328.md`
- **`docs/data/`**：存放原始/清洗后的数据文件，如行情 JSON、基金净值 CSV
- **`docs/research/`**：存放下载的研报、招股书等参考资料
- **`images/`**：区分于 `visual/` 的"创作图"，这里放分析附带的行情截图、K线图等
- **`memory/`**：内存日记本是 Agent 的工作日志，属于有价值的历史记录，应永久保留

---

## 四、temp/ 内容建议

```
temp/
├── cache/             # 爬虫/抓取的原始页面（未清洗）
├── debug/             # debug log、报错记录
├── wip/               # 未完成的分析草稿
└── fetch_tmp/         # 一次性 API 调用结果，用完即弃
```

### 清理规则

| 子目录 | 清理触发条件 |
|---|---|
| `cache/` | 每次新分析任务开始前清空，或保留≤7天 |
| `debug/` | 每次会话结束时清空 |
| `wip/` | 超过 3 天未完成的草稿→通知用户确认后删除 |
| `fetch_tmp/` | 当前会话结束前删除 |

---

## 五、总结建议

**核心问题：** `output/` 的分类维度不统一（有的按媒介形式 comic/meme，有的按内容类型），导致文档类文件无家可归。

**解决思路：**
1. 新增 `docs/` 大类，覆盖所有文字/数据类产出
2. `temp/` 作为纯缓存，明确清理规则，不承载任何有价值的生成物
3. `memory/` 作为 Agent 的生命线，单独保留，不混淆于 temp

**最关键的规则：** 任何用户可能想回头查阅的内容 → `output/`，用完即弃的临时的 → `temp/`。
