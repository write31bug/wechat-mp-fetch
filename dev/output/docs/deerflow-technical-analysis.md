# DeerFlow 技术分析报告

> 研究目标：ByteDance/deer-flow，GitHub stars 增长最快的开源 Agent 框架之一
> 研究日期：2026-04-05
> 研究深度：源码 + README + ARCHITECTURE.md + MCP_SERVER.md + 核心代码文件

---

## 一、核心技术架构

### 1.1 整体系统架构

DeerFlow 是一个**多进程分层架构**，分为三个独立服务：

```
┌─────────────────────────────────────────────────────────────┐
│                    Client (Browser)                         │
└──────────────────────────┬───────────────────────────────────┘
                           │ port 2026
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Nginx (统一反向代理入口)                         │
│  /api/langgraph/*  →  LangGraph Server (2024)               │
│  /api/*            →  FastAPI Gateway (8001)                │
│  /*                →  Next.js Frontend (3000)               │
└──────────────────────────┬───────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
   LangGraph Server   Gateway API      Frontend
     (Port 2024)      (Port 8001)      (Port 3000)
   - Agent Runtime    - Models API     - Next.js
   - Thread Mgmt      - MCP Config     - React UI
   - SSE Streaming    - Skills Mgmt    - Chat
   - Checkpointing    - File Uploads
```

**架构特点**：三层服务各司其职，Nginx 统一入口做协议路由。LangGraph Server 专注 Agent 运行时，Gateway API 专注运维管控（文件上传、MCP 配置、线程清理），Frontend 专注交互。

### 1.2 Harness 机制详解

**Harness（挽具）是 DeerFlow 的核心抽象层**：`packages/harness/deerflow` 是一个包装 LangGraph 的框架，目的是把 Agent 的**执行环境**与**业务逻辑**分离。

```
make_lead_agent(config)
       │
       ▼
┌──────────────────────────────────────────────┐
│         Middleware Chain (8 个中间件)          │
├──────────────────────────────────────────────┤
│ 1. ThreadDataMiddleware   → 初始化 workspace/ │
│    uploads/outputs 路径                         │
│ 2. UploadsMiddleware       → 注入上传文件列表    │
│ 3. SandboxMiddleware      → 获取 sandbox 环境  │
│ 4. SummarizationMiddleware → 上下文压缩         │
│ 5. TitleMiddleware         → 自动生成标题       │
│ 6. TodoListMiddleware      → 任务跟踪          │
│ 7. ViewImageMiddleware     → 视觉模型支持       │
│ 8. ClarificationMiddleware → 处理澄清请求       │
└──────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│              Agent Core                       │
│   Model (from factory) + Tools + System Prompt │
└──────────────────────────────────────────────┘
```

**关键设计**：中间件链是**声明式**的，每个中间件只做一件事。`before_agent` 和 `after_agent` hook 允许在 Agent 执行前后注入逻辑。LangGraph 的 AgentMiddleware 抽象让中间件可以读写 ThreadState。

**依赖关系**（pyproject.toml）：
- `langgraph>=1.0.6,<1.0.10` — 核心图执行引擎
- `langchain-mcp-adapters>=0.1.0` — MCP 协议适配
- `langgraph-api>=0.7.0,<0.8.0` — LangGraph Server 运行时
- `agent-sandbox>=0.0.19` — Sandbox 抽象（第三方包）

### 1.3 Sandbox 实现详解

Sandbox 是 DeerFlow 最精细的安全/执行隔离单元：

#### 抽象层

```python
class Sandbox(ABC):
    def execute_command(command: str) -> str
    def read_file(path: str) -> str
    def write_file(path: str, content: str, append: bool = False) -> None
    def list_dir(path: str, max_depth=2) -> list[str]
    def glob(path: str, pattern: str, ...) -> tuple[list[str], bool]
    def grep(path: str, pattern: str, ...) -> tuple[list[GrepMatch], bool]
    def update_file(path: str, content: bytes) -> None  # 二进制写入
```

#### SandboxProvider 生命周期

```python
class SandboxProvider(ABC):
    def acquire(thread_id: str) -> str      # 获取 sandbox，返回 ID
    def get(sandbox_id: str) -> Sandbox      # 根据 ID 获取实例
    def release(sandbox_id: str) -> None     # 释放资源
```

#### 两种实现

| | LocalSandboxProvider | AioSandboxProvider |
|---|---|---|
| 用途 | 开发环境 | 生产环境 |
| 隔离方式 | 单例模式，直接执行 | Docker 容器隔离 |
| 路径映射 | 虚拟路径 → 本地真实路径 | Docker volume mount |
| 清理 | 不释放（跨 turn 复用） | 容器生命周期管理 |

#### 虚拟路径映射

| 虚拟路径 | 本地物理路径 |
|---|---|
| `/mnt/user-data/workspace` | `.deer-flow/threads/{thread_id}/user-data/workspace` |
| `/mnt/user-data/uploads` | `.deer-flow/threads/{thread_id}/user-data/uploads` |
| `/mnt/user-data/outputs` | `.deer-flow/threads/{thread_id}/user-data/outputs` |
| `/mnt/skills` | `deer-flow/skills/` |
| `/mnt/acp-workspace` | `.deer-flow/acp-workspace/` |

#### Sandbox 安全机制（tools.py 核心逻辑）

1. **路径遍历防护**：所有 `..` 段检查，`reject_path_traversal()`
2. **虚拟路径替换**：`replace_virtual_path()` 把 `/mnt/user-data/...` 映射到真实路径
3. **输出脱敏**：`mask_local_paths_in_output()` 把物理路径替换回虚拟路径返回给 Agent
4. **bash 命令校验**：`validate_local_bash_command_paths()` 检查命令中的绝对路径是否合法
5. **读写权限分离**：`validate_local_tool_path()` 对 skills、ACP workspace 强制只读
6. **自定义挂载隔离**：config.yaml 中的 `mounts` 配置，冲突路径拒绝映射

#### SandboxMiddleware 生命周期

```python
class SandboxMiddleware(AgentMiddleware):
    def __init__(lazy_init=True):
        # lazy_init=True: 首次 tool call 时才获取 sandbox（默认）
        # lazy_init=False: before_agent 时立即获取

    def before_agent(state, runtime):
        if "sandbox" not in state:
            sandbox_id = acquire(thread_id)
            return {"sandbox": {"sandbox_id": sandbox_id}}

    def after_agent(state, runtime):
        release(sandbox_id)  # 注意：实际代码中默认不 release（lazy 模式）
```

---

## 二、与 OpenClaw 的对比

### 2.1 架构模式对比

| 维度 | DeerFlow | OpenClaw |
|---|---|---|
| **语言生态** | Python + LangGraph | Node.js/TypeScript + 自研框架 |
| **协议层** | LangGraph API（REST + SSE）+ 自定义 MCP | ACP (Agent Communication Protocol) |
| **服务架构** | 多进程分离（LangGraph Server + Gateway + Frontend） | Gateway 统一入口，内嵌 Agent Runtime |
| **部署复杂度** | 高（需要 Nginx 反向代理、多服务） | 低（Gateway + 嵌入式 Runtime） |
| **配置方式** | YAML 配置（config.yaml）+ JSON 扩展配置 | JSON 配置文件（SKILL.md frontmatter） |
| **Checkpoint** | SQLite（`langgraph-checkpoint-sqlite`） | 内置持久化机制 |

### 2.2 核心能力矩阵

| 能力 | DeerFlow | OpenClaw |
|---|---|---|
| **Agent 运行时** | LangGraph（基于消息图） | 自研（基于状态机） |
| **多 Agent 编排** | Subagent（并发 task 调用，max 3/response） | Subagent（深度嵌套的 agent 树） |
| **MCP 集成** | langchain-mcp-adapters（支持 stdio/SSE/HTTP） | MCP Client（stdio 为主） |
| **Sandbox 隔离** | 虚拟路径映射 + 容器隔离 | 文件系统级别的工具封装 |
| **Skills 系统** | SKILL.md（YAML frontmatter + 内容注入 prompt） | SKILL.md（自定义格式） |
| **记忆系统** | LLM 驱动的 Fact Extraction + 注入 prompt | 基础 session 记忆 |
| **上下文压缩** | SummarizationMiddleware（token 阈值触发） | 无（依赖模型上下文窗口） |
| **Clarification** | Middleware 级别的澄清请求处理 | 工具级别的 ask_clarification |
| **文件上传处理** | Gateway 接收 → markitdown 转 MD → Middleware 注入 | 工具系统集成 |
| **子进程池** | ThreadPoolExecutor（subagent 执行）+ asyncio | ACP 协议调度 |

### 2.3 各自优劣

#### DeerFlow 优势

1. **生产级隔离**：Docker Sandbox 支持真正的容器级隔离，适合运行不可信代码
2. **Middleware 组合性**：8 个中间件各司其职，扩展 agent 行为不需要改核心代码
3. **Subagent 并发**：有 max_concurrent 硬限制，防止过度委托
4. **MCP 生态**：通过 langchain-mcp-adapters 接入所有 MCP 服务器（GitHub、filesystem、postgres 等）
5. **虚拟路径抽象**：Agent 看到的是 `/mnt/user-data/...`，完全不感知真实文件系统结构
6. **工具安全**：完整的路径遍历防护、读写权限分离、bash 命令白名单

#### DeerFlow 劣势

1. **部署重**：三服务架构 + Nginx，需要 Docker/Kubernetes 环境
2. **Python GIL**：Agent Runtime 是 Python，并发受 GIL 限制（subagent 用线程池绕过）
3. **复杂度高**：middleware 链、sandbox provider、path mapping 等概念多，学习曲线陡
4. **性能开销**：虚拟路径替换、输出脱敏等操作有性能损耗
5. **前端绑定 Next.js**：不支持自定义前端或 API-only 模式

#### OpenClaw 优势

1. **轻量**：Gateway 统一入口，本地运行无依赖
2. **实时能力强**：Gateway + node 的 SSE 推送延迟低
3. **灵活扩展**：SKILL.md + 工具系统 + MCP，扩展路径清晰
4. **TypeScript 生态**：npm 包丰富，前端集成方便
5. **移动端支持**：Companion App（iOS/Android）+ Tailscale 组网

#### OpenClaw 劣势

1. **Sandbox 隔离较弱**：本地执行模式，无容器级隔离
2. **多 Agent 编排**：子 agent 作为独立 session，缺乏统一的中控协调机制
3. **记忆系统基础**：session 记忆，无 LLM 驱动的 fact extraction
4. **上下文压缩**：无内置方案
5. **中文文档**：DeerFlow 有完整中文文档

---

## 三、代码结构分析

### 3.1 目录结构

```
backend/
├── app/
│   └── gateway/           # FastAPI 网关（端口 8001）
│       ├── app.py         # FastAPI 入口
│       ├── models.py      # /api/models
│       ├── mcp.py         # /api/mcp（MCP 服务器配置）
│       ├── skills.py      # /api/skills
│       ├── uploads.py     # /api/threads/{id}/uploads
│       ├── threads.py     # 线程数据清理
│       ├── artifacts.py   # 工件服务
│       └── suggestions.py # 跟进建议生成
│
├── packages/harness/deerflow/
│   ├── agents/
│   │   ├── lead_agent/
│   │   │   ├── agent.py          # make_lead_agent() — 入口
│   │   │   └── prompt.py         # apply_prompt_template() — prompt 拼接
│   │   ├── thread_state.py       # ThreadState = AgentState + sandbox/artifacts/title/todos
│   │   ├── memory/               # LLM Fact Extraction + 记忆存储
│   │   └── middlewares/          # 8 个中间件
│   │
│   ├── sandbox/
│   │   ├── sandbox.py           # 抽象 Sandbox 基类
│   │   ├── sandbox_provider.py  # Provider 抽象 + get_sandbox_provider()
│   │   ├── middleware.py         # SandboxMiddleware（LangGraph hook）
│   │   ├── tools.py             # bash/ls/read_file/write_file/glob/grep 工具（1314 行）
│   │   ├── security.py          # 路径安全检查
│   │   ├── search.py            # GrepMatch 数据结构
│   │   ├── file_operation_lock.py
│   │   ├── local/
│   │   │   └── local_sandbox_provider.py   # 单例 LocalSandbox
│   │   └── community/
│   │       └── aio_sandbox/     # Docker 容器隔离
│   │
│   ├── skills/
│   │   ├── loader.py            # load_skills() — 扫描 skills/ 目录
│   │   ├── parser.py            # 解析 YAML frontmatter
│   │   └── types.py             # Skill dataclass
│   │
│   ├── mcp/
│   │   ├── client.py            # build_server_params() — MCP 参数构建
│   │   ├── cache.py             # get_cached_mcp_tools() — mtime 缓存失效
│   │   ├── tools.py             # get_mcp_tools() — 返回 BaseTool 列表
│   │   └── oauth.py
│   │
│   ├── subagents/
│   │   ├── executor.py           # SubagentExecutor — async 执行 + thread pool
│   │   ├── registry.py          # get_subagent_config() — 查配置 + config.yaml 覆盖
│   │   ├── config.py            # SubagentConfig dataclass
│   │   └── builtins/
│   │       ├── general_purpose.py   # 通用子 agent
│   │       └── bash_agent.py        # bash 子 agent
│   │
│   ├── tools/
│   │   └── __init__.py          # get_available_tools() — 聚合所有工具
│   │
│   ├── models/
│   │   └── factory.py           # create_chat_model() — 反射机制加载 LangChain 模型
│   │
│   ├── config/
│   │   ├── app_config.py        # 主配置（models/sandbox/skills/mcp 等）
│   │   ├── extensions_config.py # MCP servers + skills 启用状态（热加载）
│   │   ├── sandbox_config.py
│   │   ├── skills_config.py
│   │   ├── subagents_config.py
│   │   └── paths.py             # 路径解析
│   │
│   └── community/               # 内置搜索工具
│       ├── tavily/
│       ├── firecrawl/
│       ├── ddg_search/
│       └── ...

skills/
├── public/                      # 内置 skills（20+ 个）
│   ├── bootstrap/              # SOUL.md 生成引导
│   ├── deep-research/
│   ├── pdf-processing/
│   ├── frontend-design/
│   ├── skill-creator/
│   └── ...
└── custom/                     # 用户自定义 skills（gitignored）

langgraph.json                  # LangGraph Server 配置入口
```

### 3.2 MCP Server 集成方式

**配置来源**：`extensions_config.json`（Gateway API 写入）

```json
{
  "mcpServers": {
    "github": {
      "enabled": true,
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {"GITHUB_TOKEN": "$GITHUB_TOKEN"}
    }
  }
}
```

**集成流程**：

1. `build_server_params()` 把配置转成 `langchain-mcp-adapters` 的 ServerParams
2. `MultiServerMCPClient` 同时管理多个 MCP 服务器进程
3. `get_cached_mcp_tools()` 用文件 mtime 做缓存失效：配置变更 → mtime 变 → 重新初始化 MCP Client
4. 工具通过 `get_mcp_tools()` 返回 `list[BaseTool]`，汇入 `get_available_tools()`
5. Gateway 的 `PUT /api/mcp/config` 改文件 → 下次 Agent 调用自动 reload

**支持传输类型**：stdio / SSE / HTTP（通过 `langchain-mcp-adapters` 实现）

### 3.3 Skill 扩展机制

**SKILL.md 格式**：

```yaml
---
name: Bootstrap Soul
description: Generate a personalized SOUL.md through a warm, adaptive onboarding conversation.
license: MIT
---

# Skill Instructions
Content injected into system prompt...
```

**加载流程**：

```
load_skills()
  → 扫描 skills/public/ 和 skills/custom/
  → 每个 SKILL.md 用 parse_skill_file() 解析 frontmatter
  → 从 ExtensionsConfig 读取 enabled 状态
  → 返回 list[Skill]
```

**注入 Prompt 方式**（`get_skills_prompt_section()`）：

```xml
<skill_system>
You have access to skills that provide optimized workflows...

**Skills are located at:** /mnt/skills

<available_skills>
    <skill>
        <name>Bootstrap Soul</name>
        <description>Generate a personalized SOUL.md...</description>
        <location>/mnt/skills/public/bootstrap/SKILL.md</location>
    </skill>
    ...
</available_skills>
</skill_system>
```

**Agent 使用 Skill**：`read_file("/mnt/skills/public/bootstrap/SKILL.md")` → 加载并执行

### 3.4 工具系统

**工具来源三层聚合**：

```
Built-in Tools           Configured Tools        MCP Tools
(bash/ls/read/write)     (web_search/bash/...)   (github/filesystem/...)
     │                         │                       │
     └─────────────────────────┴───────────────────────┘
                               │
                    get_available_tools()
                               │
                         list[BaseTool]
                               │
                          注入 Agent
```

**安全工具 bash** 流程（最复杂）：
1. `validate_local_bash_command_paths()` 扫描绝对路径
2. `replace_virtual_paths_in_command()` 把虚拟路径替换为真实路径
3. `_apply_cwd_prefix()` 自动 `cd /mnt/user-data/workspace &&`
4. `sandbox.execute_command()` 执行
5. `mask_local_paths_in_output()` 脱敏输出
6. `_truncate_bash_output()` 中间截断（保留头尾）

---

## 四、是否值得借鉴

### 4.1 值得借鉴的设计

#### 🥇 1. 虚拟路径抽象（最高优先级）

DeerFlow 的 `/mnt/user-data/{workspace,uploads,outputs}` 抽象非常精妙：
- Agent 完全不感知真实文件系统结构
- 安全检查和路径映射在工具层透明完成
- Workspace 隔离天然支持多租户（每个 thread_id 独立目录）

**OpenClaw 落地建议**：工具层引入虚拟路径前缀 `/mnt/workspace/`、`/mnt/uploads/`、`/mnt/outputs/`，工具执行前做路径映射和校验。

#### 🥈 2. Middleware 链组合（高优先级）

`before_agent` / `after_agent` hook 机制让行为扩展不需要改核心代码：

```python
# OpenClaw 可以类似设计
class Middleware(ABC):
    def before_agent(state, context) -> dict | None
    def after_agent(state, context) -> dict | None
```

目前 OpenClaw 的 `before_agent` / `after_agent` 已经在用，可以进一步抽象成链式调用。

#### 🥉 3. MCP 工具缓存失效（mtime 机制）

```python
def get_cached_mcp_tools():
    config_mtime = os.path.getmtime(CONFIG_FILE)
    if config_mtime != _cached_mtime:
        reinitialize_mcp_client()
```

**借鉴点**：任何配置文件变更驱动缓存失效，不需要重启服务。

#### 4. Skills 渐进加载模式

```xml
**Progressive Loading Pattern:**
1. read_file on skill's main file
2. Load referenced resources only when needed
```

Agent 主动 `read_file` skill 文件，而不是把整个 skill 内容塞进 prompt。这是更优雅的 long-context 处理方式。

#### 5. Subagent 并发限制

`max_concurrent=3` 是硬限制，超出直接丢弃。这比让 Agent 自由委托更安全。OpenClaw 的 subagent 树也需要类似的并发上限控制。

#### 6. 多级 Checkpointer

SQLite checkpointer + async provider，支持多实例并发读写。OpenClaw 目前没有显式的 checkpoint 机制，如果要做多轮对话记忆持久化，可以参考这个设计。

### 4.2 不适合借鉴的

1. **三服务架构**：DeerFlow 的 Nginx + LangGraph Server + Gateway + Frontend 四层架构对于个人 Agent 框架来说过于重量，OpenClaw 的单 Gateway 模式更合理。

2. **Python 生态**：OpenClaw 是 TypeScript/Node.js，换语言不现实。DeerFlow 的 Python 依赖（LangGraph、LangChain）在 Node.js 生态没有直接等价物。

3. **Docker Sandbox**：容器级隔离需要 Docker 环境，个人使用场景下配置成本高，虚拟路径 + 权限校验的轻量方案更实际。

4. **过度封装的复杂度**：DeerFlow 一个 `bash` 工具写了 1314 行（含安全、路径、输出处理），虽然严谨但维护成本高。OpenClaw 应该保持更扁平的架构。

### 4.3 落地优先级建议

| 优先级 | 借鉴项 | 理由 |
|---|---|---|
| P0 | 虚拟路径抽象 + 安全校验 | 核心安全能力，直接提升工具安全性 |
| P0 | MCP 集成 + 热加载 | 生态扩展，OpenClaw 已部分实现 |
| P1 | Middleware 链机制 | 行为扩展的基础设施 |
| P1 | Skill 渐进加载 | 解决 long-context 的优雅方案 |
| P2 | Subagent 并发上限 | 防止 Agent 过度委托 |
| P2 | LLM Fact Extraction 记忆 | 高价值但实现复杂度高 |
| P3 | Docker Sandbox | 个人场景优先级低 |
| P3 | 多服务架构 | OpenClaw 定位不同 |

---

## 五、附录

### 5.1 DeerFlow 核心技术栈

```
Python 3.12+
├── langgraph 1.0.6~1.0.9        # Agent 图执行引擎
├── langgraph-api 0.7~0.8        # LangGraph Server 运行时
├── langchain-mcp-adapters 0.1.0  # MCP 协议适配层
├── agent-sandbox 0.0.19         # Sandbox 抽象（第三方）
└── FastAPI + uvicorn            # Gateway API
```

### 5.2 关键源码文件索引

| 功能 | 文件路径 |
|---|---|
| Agent 入口 | `packages/harness/deerflow/agents/lead_agent/agent.py` |
| Prompt 模板 | `packages/harness/deerflow/agents/lead_agent/prompt.py` |
| Sandbox 抽象 | `packages/harness/deerflow/sandbox/sandbox.py` |
| 工具实现（安全重点） | `packages/harness/deerflow/sandbox/tools.py` |
| 本地 Sandbox | `packages/harness/deerflow/sandbox/local/local_sandbox_provider.py` |
| MCP 集成 | `packages/harness/deerflow/mcp/` |
| Skills 加载 | `packages/harness/deerflow/skills/loader.py` |
| Subagent 执行器 | `packages/harness/deerflow/subagents/executor.py` |
| 架构文档 | `backend/docs/ARCHITECTURE.md` |
| MCP 文档 | `backend/docs/MCP_SERVER.md` |
