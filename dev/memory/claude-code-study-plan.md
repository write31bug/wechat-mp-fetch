# Claude Code 源码学习计划

> 基于 `E:\openclaw\dev\repos\claude-code` 泄露源码（2026-03-31）

## 学习阶段

### 阶段一：概览与核心链路（Day 1）
**目标**：理解整体架构和核心数据流

| 序号 | 内容 | 关键文件 | 预计时间 |
|------|------|---------|---------|
| 1.1 | 项目结构概览 | README.md, main.tsx | 30min |
| 1.2 | CLI入口与启动流程 | main.tsx, REPL.tsx | 1h |
| 1.3 | QueryEngine 核心循环 | QueryEngine.ts | 2h |
| 1.4 | Tool 系统架构 | tools.ts, Tool.ts | 1.5h |
| 1.5 | 状态管理 | state/AppState.tsx, AppStateStore.ts | 1h |

### 阶段二：工具与命令系统（Day 2）
**目标**：掌握工具注册、执行、权限全流程

| 序号 | 内容 | 关键文件 | 预计时间 |
|------|------|---------|---------|
| 2.1 | Tool 注册机制 | tools.ts, tools/AgentTool/ | 1.5h |
| 2.2 | 权限系统 | hooks/toolPermission/, useCanUseTool.tsx | 1.5h |
| 2.3 | BashTool 执行流程 | tools/BashTool/ | 1h |
| 2.4 | FileEditTool 编辑逻辑 | tools/FileEditTool/ | 1h |
| 2.5 | Command 命令系统 | commands.ts, commands/ | 1h |

### 阶段三：Agent 与协作（Day 3）
**目标**：理解多Agent协调机制

| 序号 | 内容 | 关键文件 | 预计时间 |
|------|------|---------|---------|
| 3.1 | Coordinator 模式 | coordinator/coordinatorMode.ts | 1.5h |
| 3.2 | AgentTool 子Agent | tools/AgentTool/ | 1h |
| 3.3 | TeamCreateTool 团队 | tools/TeamCreateTool/ | 1h |
| 3.4 | Skills 系统 | skills/loadSkillsDir.ts, SKILL.md | 1.5h |

### 阶段四：集成与扩展（Day 4）
**目标**：理解插件、IDE集成、远程控制

| 序号 | 内容 | 关键文件 | 预计时间 |
|------|------|---------|---------|
| 4.1 | Bridge IPC 机制 | bridge/bridgeMain.ts | 1.5h |
| 4.2 | MCP 协议集成 | services/mcp/ | 1h |
| 4.3 | Plugin 系统 | plugins/, utils/plugins/ | 1h |
| 4.4 | IDE 集成 | hooks/useIDEIntegration.tsx | 1h |

### 阶段五：进阶专题（Day 5+）
**按需深入**

- REPL UI 渲染（ink/ + components/）
- 上下文管理（context.ts, memdir/）
- 会话恢复（sessionRestore.ts）
- 终端 UI 组件（components/Spinner.tsx 等）

---

## 核心要点速记

### 架构设计亮点

1. **并行预取启动**：MDM配置 + Keychain + API预连接并行，压缩启动时间
2. **懒加载大依赖**：OpenTelemetry/gRPC 动态 import，按需加载
3. **编译时死码消除**：Bun `feature()` 特性开关，剔除未启用功能
4. **权限分层**：default / plan / bypassPermissions / auto 多级模式
5. **Markdown Skill**：以 .md 格式定义工作流，支持 frontmatter 参数

### Tool 执行链路

```
用户输入 → processUserInput() 
         → QueryEngine.query() 
         → Anthropic API 
         → 解析 tool_use 
         → useCanUseTool() 权限检查 
         → Tool.execute() 
         → 返回结果 
         → 循环直到完成
```

### 关键文件速查

| 功能 | 文件 |
|------|------|
| CLI入口 | `src/main.tsx` |
| REPL界面 | `src/screens/REPL.tsx` |
| Agent核心 | `src/QueryEngine.ts` |
| Tool定义 | `src/Tool.ts` + `src/tools/` |
| 权限判断 | `src/hooks/useCanUseTool.tsx` |
| 状态管理 | `src/state/AppState.tsx` |
| MCP集成 | `src/services/mcp/` |
| Bridge通信 | `src/bridge/` |
| Skill加载 | `src/skills/loadSkillsDir.ts` |

---

## 学习产出目标

- [ ] 理解 Claude Code 整体架构
- [ ] 掌握 Tool 系统的注册与执行机制
- [ ] 理解 QueryEngine 的 Agent Loop
- [ ] 理解 Skills 与 OpenClaw SKILL 的异同
- [ ] 理解 Bridge IPC 远程控制原理
- [ ] 输出关键模块的代码解读笔记

---

_Last updated: 2026-03-31_
