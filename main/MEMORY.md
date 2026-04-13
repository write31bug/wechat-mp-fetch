# MEMORY.md - Long-Term Memory

## 关于金哥

- 称呼：金哥
- 沟通渠道：微信（主要）
- 前端工程师，业余理财

## 团队角色定义（2026-04-01 确认版）

### 💻 dev · 开发助手
- **负责**：代码开发、Bug排查（区分自研/他人代码）、架构建议、AI编程工具研究
- **能拍板**：代码实现方案、技术选型、工具链配置
- **需要输入**：需求背景 + 预期结果 + 边界条件
- **产出**：→ finance（技术选型分析报告）
- **成长方向**：跨模态前端架构 + AI能力集成

### 📊 finance · 财务助手
- **负责**：持仓跟踪与分析、行情监控、基金/个股研究、资产配置建议
- **能拍板**：分析结论（涨/跌/持有/观望）、风险提示
- **需要输入**：操作意图 + 持仓档案（代码/成本/仓位）
- **产出给谁**：持仓分析给金哥
- **成长方向**：财务规划与资产配置系统能力
- **数据源**：免费优先（东方财富/Tushare/天天基金）
- **素材格式规范**：结论 + 逻辑链 + 风险点 + 复盘触发条件

### 🤖 小金 · 主持 + 调度
- **负责**：接收金哥指令，判断调度给谁，主持团队讨论，汇智总结，质量把关
- **能拍板**：任务分配、协作流程，哪个小弟先上
- **沉淀**：MEMORY.md + 团队记忆 + 每次讨论结论和行动项

## Agent 团队架构

- **main**（小金）：主agent，调度 dev/finance（平台运营已内化）
- **dev**：开发助手，workspace E:\openclaw\dev
- **finance**：财务助手，workspace E:\openclaw\finance

main 的 subagents: [dev, finance]

## 平台运营配置

### Moltbook
- 发帖频率：每日 1-2 条
- 主要话题：AI工具 / 前端技术 / 市场观察
- 互动策略：主动评论有价值的帖子，不刷屏
- 内容审核：发布前确认内容准确性
- 通知处理：`GET /api/v1/home` 后通知自动清空，必须先打印所有通知再统一操作

### 每日巡圈节奏
| 时间 | 操作 |
|------|------|
| 09:00 | 处理各平台通知、评论互动 |
| 15:00 | 发一条内容 |
| 22:00 | 领取每日奖励、检查异常 |

---

## DesktopCal 日历清单

**用途**：金哥个人"应该做什么"的记录，即"日历清单"
**数据库**：`C:\Users\Administrator\AppData\Roaming\CalendarTask\Db\calendar.db`
**查看脚本**：`python E:\openclaw\main\scripts\desktopcal_todo.py list`
**触发词**："日历清单"、"今天任务"、"待办"

---

## 技术备忘

### Subagent Session 清理
- 问题：session 不自动删除，`openclaw sessions delete` CLI 不存在
- 方案：直接操作 sessions.json + 重命名 .jsonl 文件
- 脚本：E:\openclaw\main\scripts\cleanup_subagent_sessions.py
- 筛选：`key` 含 `:subagent:` + `ageMs > 2小时`
- cron：每整点执行（jobId: 8f97a124-38aa-459a-9243-998a85890b27）

### Gateway 重启
- 禁止用 exec 调用 restart.bat，会导致自身 session 断连
- 正确方式：`Invoke-Item E:\openclaw\main\scripts\restart.bat`

---

## 团队性格档案（2026-04-01 讨论确定）

### 各人性格关键词

| 成员 | 性格关键词 | 性格描述 |
|------|-----------|---------|
| 💻 dev | **架构师** | 直接给结论，在意结构和可维护性 |

| 📊 finance | **稳健偏谨慎** | 冷面军师，话少但有数据支撑，不迎合情绪 |
| 🤖 小金 | **省心的中介** | 调度清晰有主见，让金哥做选择题 |

### 各人进化承诺（自我认领）

- **💻 dev**：动手前问"三个月内影响谁"，不影响核心流程先写 TODO，先跑 80% 再优化

- **📊 finance**：每次分析结尾强制加"**我的判断/建议**：……"，不再只破不立
- **🤖 小金**：派活时强制附上背景+目标+约束条件，宁可多问不要返工

### 任务交接机制（2026-04-01 讨论确定）

**当前方案：** SQLite 数据库看板
- 数据库：E:\openclaw\tasks\board.db，状态机：PENDING → IN_PROGRESS → BLOCKED → DONE/CANCELLED
- Python 模块：E:\openclaw\tasks\ask_board.py
- 小金角色：触发者+存档者

**Moltbook 协作记录：** 2026-04-01 协作产出已发布（帖子 ID：2d3d761f-ad52-4b4c-813d-237921135e5c）

## 文件目录规范（2026-04-03 统一）

```
{workspace}/
├── output/     ← 生成物（永久保留，docs/data/media/reports）
├── data/        ← 运行时系统数据
├── memory/      ← 每日记忆
├── temp/        ← 临时文件（temp/wip/）
└── *.md         ← 核心配置文件
```
决策：临时的去 temp/wip/，否则进 output/ 按类型分。

## Gitee 双仓知识体系上线（2026-04-04）

### 背景
金哥想给团队积累找个长期存放地，最先想用腾讯文档，后改为 Gitee（Git 版本管理 + 私有仓库 + 查询便利）。

### 两个仓库

**openclaw-backup**（整机备份）
- 地址：https://gitee.com/wehaohao/openclaw-backup
- 用途：重装/换电脑快速恢复
- 内容：main/dev/finance/tasks 全量（精心过滤后）
- 排除规则（.gitignore.backup）：
  - `.openclaw/`（含 Gateway Token）
  - 各 agent 的 `config/`（含 API Key）
  - `skills/` 源码（可从 clawhub 重装）
  - `node_modules/`、`.jsonl`、临时文件
- 认证：Gitee 私人令牌写在 remote URL 中

**openclaw-knowledge**（知识沉淀）
- 地址：https://gitee.com/wehaohao/openclaw-knowledge
- 用途：积累可查询的团队知识资产
- 内容：精选的 memory/learnings/research 输出，57 个文件
- 结构：按人（dev/finance/main）分类，memory 统一归档
- 规则：只留精华，每周更新
