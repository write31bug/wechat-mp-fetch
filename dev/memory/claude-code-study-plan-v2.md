# Claude Code 源码学习计划 v2

> 基于文档《前端开发工程师 OpenClaw Agent 学习 Claude Code 源码收益最大化落地方案》调整
> 更新日期：2026-03-31

---

## 核心原则

**不是让 AI 单纯"读取"源码，而是将 Claude Code 的工业级设计转化为 OpenClaw 的原生能力。**

---

## 一、源码筛选（先做这件事）

### P0 模块（必须学习）

| 模块 | 核心内容 | 对 OpenClaw 的价值 |
|------|---------|-------------------|
| **Tool 系统** | 40+ 工具的文件操作、代码分析、Shell 执行、LSP 集成 | 工具注册、权限、描述动态化 |
| **Hooks 引擎** | @before_write、@after_task、@on_error 等自动化规则 | 自动化质检、格式化 |
| **规划引擎** | Plan Mode 的需求拆解与方案设计逻辑 | 需求分析、工作流 |
| **代码评审** | code-review 插件核心规则 | Code Review 自动化 |
| **TS 类型定义** | Node.js 工具链的类型最佳实践 | 类型规范 |

### P1 模块（选择性学习）

| 模块 | 核心内容 | 对 OpenClaw 的价值 |
|------|---------|-------------------|
| 插件系统 | Plugin SDK 开发 | OpenClaw 扩展能力 |
| MCP 协议 | 工具调用逻辑 | OpenClaw 的 MCP 集成 |
| 权限与沙箱 | 安全机制 | 安全设计 |
| CLI UI | Ink 框架渲染 | OpenClaw 控制台 |
| 多 Agent 协同 | 任务管理 | OpenClaw 子 Agent |

### 排除模块（不学）

- Anthropic 内部专属工具
- 与前端无关的后端服务
- 第三方平台适配的非通用逻辑
- 编译打包的底层冗余代码

---

## 二、学习任务框架

```
阶段学习 → 复盘（含落地规划） → 下一阶段
    ↓
整体复盘（串联新旧知识） → 下下阶段
```

**每个阶段复盘必须包含：**
1. 这个模块"是什么"和"为什么"
2. 对 OpenClaw 的落地规划（差距在哪里 + 下一步行动）
3. 和前面学过的模块有没有连接点

---

## 三、P0 模块学习顺序

### 阶段一 ✅ 已完成：架构概览（主流程）
- main.tsx 启动流程
- QueryEngine 核心循环
- 状态管理（Store）
- 工具注册机制

**阶段一落地规划（待补充）**
- [ ] OpenClaw Gateway 启动是否有可优化的 I/O？
- [ ] 状态管理是否需要重构？

### 阶段二 🔨 下一步：Tool 系统与权限系统
- Tool.ts 基类定义
- 工具注册机制（tools.ts）
- useCanUseTool 权限检查
- BashTool 典型工具实现
- toolOrchestration 工具编排

**阶段二落地规划（待填写）**
- [ ] OpenClaw 的 wecom_mcp 工具系统如何对标？
- [ ] 权限模型是否需要增强？

### 阶段二落地规划 ✅ 已完成

**OpenClaw 现状**：
- 工具定义：SKILL.md 文档系统，无代码级定义
- 工具描述：静态字符串，无动态描述
- 权限控制：无，依赖 MCP 协议本身
- 工具注册：MCP 配置，无 Feature Flag

**Claude Code 的做法**：
- Tool.ts：~30 个属性/方法的复杂接口
- 动态 description：根据输入返回不同描述
- 四级权限模式 + 规则引擎
- Feature Flag 条件注册

**下一步行动**：
- **短期（1-2周）**：理解 wecom_mcp 调用链路，不需要改 SKILL.md
- **中期（1个月）**：增强描述动态化（参考 Claude Code）
- **长期（季度）**：如需原生执行工具，再考虑 Tool.ts 架构

**与已学模块的连接**：
- 阶段一（QueryEngine）+ 阶段二（Tool）= 完整调用链
- Tool.call() 在 QueryEngine 的 queryLoop 中被调用
- 工具权限状态存在 AppState（阶段一学的 Store）

### 阶段三：Hooks 自动化规则引擎
- hooks/ 目录结构
- @before_write、@after_task 等事件
- hook 执行机制

**阶段三落地规划（待填写）**
- [ ] OpenClaw 能否实现类似的自动化 Hooks？
- [ ] 落地场景：文件写入前自动格式化？

### 阶段四：规划引擎（Plan Mode）
- coordinator/ 目录
- 需求拆解逻辑
- 方案生成机制

**阶段四落地规划（待填写）**
- [ ] OpenClaw 是否需要 Plan Mode？
- [ ] 什么样的场景适合？

### 阶段五：代码评审
- commands/review/
- 评审规则定义
- 评审执行流程

**阶段五落地规划（待填写）**
- [ ] OpenClaw 能否实现 Code Review 自动化？
- [ ] 评审维度有哪些？

### 阶段六：TS 类型最佳实践
- types/ 目录
- 类型定义模式
- Node.js 工具链类型

**阶段六落地规划（待填写）**
- [ ] OpenClaw 代码的类型规范有哪些可以改进？

---

## 四、整体复盘节点

| 节点 | 内容 |
|------|------|
| P0 全部学完后 | 综合输出「OpenClaw 对标 Claude Code 的能力差距 & 落地计划」 |
| 开始 P1 时 | 整体复盘 P0，重新评估 P1 的优先级 |
| 全部学完后 | 最终综合报告 |

---

## 五、OpenClaw 架构研究（已做）

### 已完成研究

**核心发现**：
- OpenClaw 的 Agent Runtime = `runEmbeddedPiAgent()` ≈ Claude Code 的 `QueryEngine`
- OpenClaw 的 Tool = Gateway RPC 调用 ≠ Claude Code 的原生 `Tool.call()`
- OpenClaw 有强大的 Hook 系统（30+ 生命周期 hook）
- OpenClaw 有 Compaction（自动上下文压缩）

**对学习的帮助**：
带着 Claude Code 的框架去看 OpenClaw，理解更深了。

---

## 六、OpenClaw 研究结论（对 Claude Code 学习的影响）

### 最重要的发现

1. **OpenClaw 有更完整的 Hook 系统**
   - Claude Code 的 Hook 只在 Skill 层面
   - OpenClaw 有 30+ 生命周期 hook
   - 这是 OpenClaw 比 Claude Code 强的地方

2. **OpenClaw 有 Compaction**
   - Claude Code 靠手动 /context 命令管理上下文
   - OpenClaw 有自动 compaction
   - Claude Code 没有这个

3. **Tool 系统架构完全不同**
   - Claude Code：Tool 是 TypeScript 类，原生执行
   - OpenClaw：Tool 是 RPC 调用，分布式

### 对继续学习的启发

| Claude Code 模块 | OpenClaw 对应 | 还需要学吗？ |
|-----------------|--------------|------------|
| Tool 系统 | RPC Tool | 架构不同，但可以了解 |
| Hooks | 30+ hook | **值得学！OpenClaw 更完整** |
| 规划引擎 | ？ | 需要研究 |
| 代码评审 | ？ | 需要研究 |
| TS 类型 | TypeScript 写得很规范 | 可能不需要 |

---

## 七、落地规划模板（每个阶段复盘时填写）

```markdown
### 阶段 N 落地规划

**OpenClaw 现状**：
- [ ] 当前是怎么做的
- [ ] 差距在哪里

**Claude Code 的做法**：
- [ ] 核心设计
- [ ] 可借鉴的点

**下一步行动**：
- [ ] 短期（1-2周）：可以做哪个改进？
- [ ] 中期（1个月）：需要规划哪个能力？
- [ ] 长期（季度）：需要立项哪个大功能？

**与已学模块的连接**：
- 阶段 N 和阶段 X 的关联是什么？
- 能否组合出新的能力？
```

---

_Last updated: 2026-03-31_
