# BOOTSTRAP.md - auto-xyyan 启动检查

## 每次 auto-xyyan 启动时执行

### 第一步：检查今日是否已学习
读取 `daily/last_run.txt`：
- **日期 = 今天** → 静默完成，不重复，直接进入待机
- **日期 ≠ 今天** → 执行完整文献搜索任务

### 第二步：执行文献搜索（如需要）
1. 搜索 PubMed/ArXiv 最新脓毒症文献（内皮损伤、凝血病、DIC、生物标志物、ICU临床研究），重点2025-2026年
2. 生成结构化速报，保存 `daily/YYYY-MM-DD.md`
3. 更新 MEMORY.md
4. 更新 `daily/last_run.txt` 为今天日期

### 第三步：注册每日定时
确认 `auto-xyyan-daily-lit` cron 任务已注册（08:30 Asia/Shanghai）

### 去重保证
- 停机 N 天后重启：只补今天一次
- 定时任务和启动检查共用同一去重逻辑（比对 last_run.txt）
