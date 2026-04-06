# 外部 AI Agent 文件存放规范调研报告

**调研时间**：2026-04-03
**调研目标**：了解行业内 AI Agent workspace 文件结构的最佳实践

---

## 一、调研对象概览

本次调研覆盖了以下来源：

| 来源 | 类型 | 特点 |
|------|------|------|
| **Claude Agent Workspace Model**（danielrosehill） | 社区提出的开放规范 | 追求标准化的 AI Agent 工作区结构 |
| **WebbyWisp 的 SOUL.md 体系** | 个人实践经验分享 | 强调文件作为 Agent 的"制度记忆" |
| **Mastra 项目结构指南** | 开源 AI 框架官方博客 | 面向 LLMs 的文档和技能结构化实践 |
| **LangChain / LangGraph 官方文档** | 主流 Agent 开发框架 | 工程化的图结构目录组织 |
| **CrewAI Quickstart** | 多 Agent 框架 | 以任务和 Agent 为核心的结构 |
| **OpenDevin** | AI 软件开发 Agent | Docker 沙箱隔离 + workspace 目录 |
| **Reddit: 5 AI Agents with Claude Code** | 实战多 Agent 管理 | 每个 Agent 独立 workspace |

---

## 二、各方案文件结构对比

### 2.1 Claude Agent Workspace Model（Daniel Rosehill）

这是最接近"行业标准"呼声的方案，提出了强制性的 4 目录 + 1 根文件结构：

```
my-workspace/
├── CLAUDE.md                    # 主指令文件（轻量级入口）
├── context/                     # 项目上下文（用户提供）
│   ├── project.md               # 项目名称、目标
│   ├── role.md                  # 用户角色
│   ├── constraints.md           # 边界、截止日期
│   └── for-agent/               # Agent 专用详细指令
│       ├── environment.md        # 环境细节（OS、工具、路径）
│       └── workflows.md          # 工作流指令
├── work-log/                    # 每日操作日志（Agent 维护）
│   └── YYYY-MM-DD.md
├── planning/                    # 规划目录
│   ├── plan.md                  # 当前活跃计划
│   └── pivots/                  # 计划变更记录
│       └── YYYY-MM-DD-reason.md
├── user-docs/                   # 用户可见的交付文档
└── .claude/
    └── commands/
        └── onboard.md           # 初始化 slash 命令
```

**核心理念**：
- **渐进披露（Progressive Disclosure）**：CLAUDE.md 只放高层 stub，详细内容在 `context/for-agent/` 按需读取
- **仓库即记忆**：用 Git 管理所有上下文，Agent 不依赖内置记忆功能
- **三阶段生命周期**：SCAFFOLD → PERSONALIZE（通过 `/onboard`）→ SUCCESS

---

### 2.2 WebbyWisp 的 SOUL.md 体系（dev.to 实践派）

这位作者构建了以"文件即制度记忆"为核心的工作区结构，灵感来自企业组织架构：

```
agent-workspace/
├── SOUL.md          # Agent 人格、价值观、角色定义
├── USER.md          # 服务对象（人类）的信息
├── OPS.md           # 操作手册：任务清单、任务范围、凭证、工作流规则
├── MEMORY.md        # 长期记忆：重要决策、经验教训
├── TOOLS.md         # 本地环境特定配置（SSH host、频道等）
├── memory/
│   ├── YYYY-MM-DD.md           # 每日原始日志
│   └── projects/
│       └── [project-name].md    # 各项目的动态文档
└── [output files...]
```

**核心理念**：
- Agent 需要人格（SOUL）、服务对象（USER）、操作规程（OPS）才能真正自主运行
- 每日日志是 append-only，保证历史可追溯
- 项目文件是 living document，状态实时更新

---

### 2.3 LangChain / LangGraph 官方结构

LangChain/LangGraph 是面向**开发者**的框架，目录结构偏向传统软件工程：

```
my-app/
├── my_agent/              # 所有项目代码在此
│   ├── utils/
│   │   ├── tools.py       # Agent 工具
│   │   ├── nodes.py       # 图节点函数
│   │   └── state.py       # 状态定义
│   └── agent.py            # 图构造代码
├── .env
├── requirements.txt
└── langgraph.json         # 部署配置（graphs/dependencies/env）
```

**核心理念**：
- 以 **Graph（图）** 为核心组织单元，每个节点是独立函数
- 部署配置文件（`langgraph.json`）与代码分离，支持 LangSmith 托管
- 工具（tools）、节点（nodes）、状态（state）分离

> ⚠️ 注意：LangChain 的 workspace 概念和我们完全不同——它是**开发者编写代码**的目录，不是 Agent **自己生成文件**的工作区。

---

### 2.4 CrewAI 项目结构

CrewAI 的 quickstart 示例结构：

```
src/project_name/
├── crew.py                 # Agent 定义、任务编排（CrewBase 装饰器）
├── agents.yaml             # Agent 配置
├── tasks.yaml              # 任务配置
└── output/
    └── report.md           # Agent 生成的输出文件
```

**核心理念**：
- Agent 和 Task 配置 YAML 化，与代码分离
- 明确的 `output_file` 参数指定生成物路径
- Crew = Agent 团队 + Task 编排，强调协作

---

### 2.5 Reddit 用户实践：5 个 Claude Code Agent

每个 Agent 是独立目录，有自己的 CLAUDE.md 和 `.claude/` 配置：

```
agent-name/
├── CLAUDE.md             # Agent 身份和使命
├── .claude/
│   ├── rules/            # 自动加载的上下文（始终生效）
│   │   ├── 01-business-context.md
│   │   ├── 02-agent-ecosystem.md
│   │   ├── 03-roadmap.md
│   │   ├── 05-daily-routine.md
│   │   ├── 08-control-center.md
│   │   ├── 98-end-of-session.md  # 收尾 ritual
│   │   └── 99-content-capture.md
│   └── skills/           # 按需加载的技能
├── inbox/                # 来自其他 Agent 的输入
├── outputs/              # 生成物
└── archive/              # 归档（文件不删除，只归档）
```

**核心理念**：
- **多 Agent 协作**：inbox 用于接收其他 Agent 的消息，archive 用于归档
- **编号前缀**强制规则文件的加载顺序（01, 02…）
- **end-of-session ritual**：每次会话结束必须更新 roadmap、捕获知识

---

### 2.6 OpenDevin 的沙箱隔离

OpenDevin 通过 Docker 沙箱隔离 Agent 的 workspace：

```
workspace/           # 挂载到 Docker 容器内
├── [agent generated files]
└── ...
```

**核心理念**：
- workspace 目录作为**可插拔存储**挂载到沙箱
- 宿主机文件和 Agent 操作空间严格分离
- 支持 `/docs` → Box 云存储，`/memories` → SQLite 等虚拟文件系统映射

---

## 三、与我们现有规范的对比分析

### 3.1 我们的现有结构（AGENTS.md 定义）

```
{workspace}/
├── output/              # 生成物（永久保留）
│   ├── docs/             # 文本文档
│   ├── data/             # 结构化数据
│   ├── media/            # 视觉素材
│   └── reports/          # 正式报告
├── data/                 # 运行时系统数据
├── memory/               # 每日记忆
├── temp/                 # 临时文件
│   └── wip/              # 工作中临时脚本
└── *.md                  # 核心配置文件（AGENTS/SOUL/IDENTITY/USER/HEARTBEAT/TOOLS）
```

---

### 3.2 相似之处 ✅

| 方面 | 我们的做法 | 外部类似做法 |
|------|-----------|-------------|
| **output/ 生成物隔离** | output/ 下按类型分子目录 | CrewAI 的 `output/`、Reddit 的 `outputs/` |
| **身份/人格文件** | SOUL.md、IDENTITY.md | WebbyWisp 的 SOUL.md、Reddit 的 CLAUDE.md |
| **用户上下文文件** | USER.md | WebbyWisp 的 USER.md |
| **工具/环境配置** | TOOLS.md | WebbyWisp 的 TOOLS.md |
| **每日记忆/日志** | memory/YYYY-MM-DD.md | Claude Workspace 的 work-log/、WebbyWisp 的 memory/ |
| **临时文件处理** | temp/ + 清理规则 | Reddit 的 archive/（归档而非删除）|

---

### 3.3 他们有、我们缺失的 ⭐

| 实践 | 来源 | 说明 | 可借鉴程度 |
|------|------|------|-----------|
| **规划目录 planning/** | Claude Workspace Model | 包含 plan.md 和 pivots/ 变更记录 | ⭐⭐⭐ 高 |
| **onboard 初始化流程** | Claude Workspace Model | 首次使用 slash 命令引导初始化 | ⭐⭐⭐ 高 |
| **context/for-agent/** 渐进披露 | Claude Workspace Model | 根文件放 stub，详细内容按需加载，避免 token 浪费 | ⭐⭐⭐ 高 |
| **用户文档 user-docs/** | Claude Workspace Model | 区分"Agent 操作日志"和"用户可见交付物" | ⭐⭐ 高 |
| **inbox/（多 Agent 收件箱）** | Reddit 多 Agent 实践 | Agent 间通过 inbox 传递消息 | ⭐⭐ 中（单 Agent 可暂不需要）|
| **archive/（归档目录）** | Reddit 多 Agent 实践 | 文件不删除只归档，保留完整性 | ⭐⭐ 中 |
| **end-of-session ritual** | Reddit 多 Agent 实践 | 会话结束强制更新 roadmap + 捕获知识 | ⭐⭐⭐ 高 |
| **编号规则文件** | Reddit 多 Agent 实践 | 01, 02… 强制加载顺序 | ⭐ 低（Windows 不友好）|
| **skills/ 按需技能目录** | Reddit + Mastra | 技能与主指令分离，按需加载 | ⭐⭐⭐ 高（OpenClaw 已有 SKILL.md 机制）|
| **多 workspace 协作结构** | Reddit 多 Agent | 每个 Agent 独立 workspace，顶级协调 | ⭐ 单 Agent 暂不需要 |
| **YAML 配置分离** | CrewAI | Agent/Task 配置与代码分离 | ⭐⭐ 中（任务导向 Agent 可能需要）|
| **Docker 沙箱隔离** | OpenDevin | workspace 挂载到隔离环境 | ⭐ 架构相关，暂不需要 |

---

## 四、值得重点借鉴的地方

### 4.1 高价值借鉴（推荐采纳）

#### ① 渐进披露原则（Progressive Disclosure）
**问题**：我们的 AGENTS.md 可能随时间变得臃肿，所有 token 每次都加载。

**做法**：根目录 CLAUDE.md（我们对应 AGENTS.md）只放高层 stub + stub 引用，详细内容放在 `context/` 或 `memory/` 子目录，需要时才读取。

> 我们已经有了 memory/ 和 output/ 子目录结构，可以在 AGENTS.md 中加入 stub 引用机制，将详细规则分散到子目录文件中。

#### ② 规划与 pivot 记录（planning/plan.md + pivots/）
**问题**：Agent 的计划变更没有记录，回头不知道为什么改了方向。

**做法**：增加 `planning/plan.md` 作为当前计划，`planning/pivots/YYYY-MM-DD-reason.md` 记录每次重大变更的原因。

> 这对社区运营 Agent 很有价值——为什么这周发了这个话题的帖子，而不是另一个？需要记录。

#### ③ 会话收尾 ritual（end-of-session ritual）
**问题**：每次会话结束没有强制归档动作，信息容易散落。

**做法**：定义会话结束时的标准动作——更新 memory/ 当日日志、检查 output/ 是否有新生成物、确认 next_step。

> 这与我们看板任务的 block_task → complete_task 流程有协同价值。

#### ④ 技能目录（skills/）的按需加载
**问题**：所有 Agent 能力都堆在系统 prompt 里。

**做法**：技能文件（SKILL.md）与主配置文件分离，按任务类型调用不同技能目录。OpenClaw 已有 `skills/` 目录机制，可以进一步规范化哪些技能属于"始终加载"、哪些属于"按需加载"。

#### ⑤ onboard 初始化流程
**问题**：新 Agent 或新 workspace 启动时缺少标准引导流程。

**做法**：定义 `/onboard` 流程，引导输入项目/任务基本信息，写入 `memory/` 或 `data/`。

---

### 4.2 中等价值借鉴（视情况采纳）

- **user-docs/ vs work-log/ 分离**：我们目前的 output/docs 和 memory/ 已经有类似功能，但 memory/ 的定位可以更清晰——操作日志归 memory/，用户交付物归 output/docs/
- **archive/ 归档目录**：temp/ 清理规则已经有了，但 archive/ 概念可以作为 temp/ 清理前的过渡层
- **CrewAI 的 YAML 配置化**：如果我们增加任务类型定义，可以考虑将 task templates YAML 化

---

## 五、总结

| 维度 | 评价 |
|------|------|
| **整体完备性** | 我们的规范与 Claude Workspace Model 和 WebbyWisp 体系高度趋同，结构完整 |
| **多 Agent 协作** | 我们是单 Agent，缺少 inbox/outbox 等协作机制，但这不是当前优先级 |
| **规划与记忆** | 我们有 memory/ 但缺少 planning/ 和 pivot 记录，这是最值得补充的 |
| **渐进披露** | 我们尚无 stub 引用机制，AGENTS.md 存在臃肿风险 |
| **会话收尾** | 我们通过看板任务流程有类似机制，但 temp/ 清理可以更规范 |
| **技能系统** | OpenClaw 已有 SKILL.md，Mastra 的 Skills 理念值得参考 |

**最值得优先采纳的三件事**：
1. 增加 `planning/` 目录（plan.md + pivots/），记录计划变更
2. 在 AGENTS.md 中引入 stub 引用机制，将详细规则分散到子目录
3. 定义 end-of-session ritual，明确每次会话结束的归档动作

---

*调研完成。信息来源于公开的 GitHub 仓库、官方文档、dev.to 文章和 Reddit 讨论。*
