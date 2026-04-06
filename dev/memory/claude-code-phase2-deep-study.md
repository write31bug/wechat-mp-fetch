# Claude Code 源码深度学习 — 阶段二：Tool 系统与权限系统

> 学习日期：2026-03-31 | 深度思考版

---

## 一、Tool 接口设计：为什么这么复杂？

### 1.1 Tool 接口的全貌

```typescript
// Tool.ts — 一个 Tool 竟然有 ~30 个属性/方法
type Tool = {
  // 核心
  name: string
  call(args, context, canUseTool, onProgress): Promise<ToolResult>
  description(input, options): Promise<string>  // ← 动态的！
  readonly inputSchema: Input  // ← Zod schema
  
  // 输入验证
  validateInput?(input, context): Promise<ValidationResult>
  inputsEquivalent?(a, b): boolean
  
  // 权限
  checkPermissions(input, context): Promise<PermissionResult>
  
  // 并发
  isConcurrencySafe(input): boolean
  isReadOnly(input): boolean
  isDestructive?(input): boolean
  
  // UI 相关
  isSearchOrReadCommand?(input): { isSearch, isRead, isList }
  userFacingName(input): string
  getActivityDescription?(input): string
  getToolUseSummary?(input): string
  
  // 生命周期
  isEnabled(): boolean
  interruptBehavior?(): 'cancel' | 'block'
  
  // 延迟加载
  shouldDefer?: boolean
  alwaysLoad?: boolean
  
  // MCP
  mcpInfo?: { serverName, toolName }
  
  // ... 还有更多
}
```

### 1.2 多问几个"为什么"

**Q1：为什么 Tool 是一个对象而不是一个函数？**

Claude Code 的设计选择：Tool 是有状态和行为的对象。

```typescript
// 我的理解
class BashTool {
  name = 'Bash'
  inputSchema = BashSchema
  
  async call(input, context, canUseTool, onProgress) {
    // 执行逻辑
  }
  
  description(input, options) {
    return `Run command: ${input.command}`  // 动态的！
  }
  
  checkPermissions(input, context) {
    // 工具自己的权限检查逻辑
  }
}
```

**trade-off**：
- **好处**：工具可以封装自己的权限逻辑、验证逻辑、UI 逻辑
- **坏处**：每个工具都要实现 ~30 个属性/方法，增加了工具开发的复杂度
- Claude Code 选择"高内聚"，愿意承担复杂度

**Q2：为什么 `description` 是函数而不是字符串？**

```typescript
// 静态描述（OpenClaw 当前做法）
description: "发送消息给用户"

// 动态描述（Claude Code 做法）
async description(input) {
  return `Send message to user: ${input.touser} with content: ${input.content}`
}
```

**为什么重要？**
- 用户在授权前看到权限提示："正要执行什么操作"
- "发送消息给用户" vs "给 zhangsan 发消息：明天下午3点开会"
- 动态描述让用户更清楚地知道"我在授权什么"

**对 OpenClaw 的参考价值**：
- OpenClaw 的 skill 描述是静态的
- 如果要增强权限体验，动态描述很有价值

**Q3：为什么 `validateInput` 和 `checkPermissions` 是分开的方法？**

```typescript
// validateInput: 检查输入是否合法（不需要用户授权）
validateInput = async (input) => {
  if (!input.touser) {
    return { result: false, message: "Missing touser", errorCode: 1 }
  }
  return { result: true }
}

// checkPermissions: 检查用户是否授权（需要用户确认）
checkPermissions = async (input, context) => {
  if (context.mode === 'bypassPermissions') {
    return { behavior: 'allow' }
  }
  return { behavior: 'ask' }
}
```

**设计原理**：
- Validation 失败：用户输入错误，直接报错，不需要问用户
- Permission 失败：需要用户决定是否授权

**Q4：Tool 的 `isConcurrencySafe` 是怎么用的？**

```typescript
// 工具自己的声明
isConcurrencySafe = (input) => {
  return this.isReadOnly(input)  // 只读工具可以并发
}

// 编排层用它做分组
// — 只读工具（Read/Grep/WebFetch）并行执行
// — 写操作工具串行执行
```

**这是一个性能优化**：多个只读操作可以同时执行，减少等待时间。

---

## 二、权限系统：多层规则引擎

### 2.1 权限检查的完整链路

```
用户触发工具调用
    ↓
QueryEngine.canUseTool (wrapper)
    ↓
hasPermissionsToUseTool()
    ↓
┌→ alwaysAllowRules? → 直接 allow
├→ alwaysDenyRules?  → 直接 deny
├→ classifier?        → ML 自动决策
├→ hooks?             → 自定义规则
└→ 用户确认?          → 弹窗问用户
```

### 2.2 三类规则：Allow / Deny / Ask

```typescript
type PermissionRule = {
  source: 'cliArg' | 'command' | 'session' | 'settings'
  ruleBehavior: 'allow' | 'deny' | 'ask'
  ruleValue: {
    toolName: string        // e.g., "Bash"
    ruleContent?: string    // e.g., "git *"（通配符）
  }
}
```

**规则示例**：
```json
// settings.json
{
  "permissions": {
    "alwaysAllow": ["Bash(git *)", "Read(*.ts)", "WebSearch"]
  }
}
```

### 2.3 四种权限模式

```typescript
type PermissionMode = 
  | 'default'      // 首次询问，之后记住
  | 'plan'         // Plan 模式下自动允许
  | 'bypassPermissions'  // 完全跳过（CI 模式）
  | 'auto'         // ML 分类器自动决策
```

### 2.4 "为什么需要这么多规则来源？"

```typescript
// 来源 1: CLI 参数
claude --dangerously-enable-permissions "Bash(*)"
// 来源 2: 命令中设置（/config）
// 来源 3: 会话中动态添加
// 来源 4: settings.json（持久化）
```

**设计原理**：
- 不同场景需要不同粒度的权限控制
- CLI 适合临时测试
- settings 适合团队规范
- 会话适合临时放开某个命令

**trade-off**：
- **好处**：灵活性极高
- **坏处**：规则多了难以追踪，"这个操作为什么被允许？"

---

## 三、工具注册：Feature Flag 驱动的条件注册

### 3.1 条件注册的多种模式

```typescript
// 模式 1: 环境变量
...(process.env.USER_TYPE === 'ant' ? [ConfigTool] : [])

// 模式 2: Feature Flag
...(SleepTool ? [SleepTool] : [])
...(MonitorTool ? [MonitorTool] : [])

// 模式 3: 懒函数（避免循环依赖）
const getTeamCreateTool = () => require(...).TeamCreateTool
...(isAgentSwarmsEnabled() ? [getTeamCreateTool()] : [])

// 模式 4: 函数返回值
...(getPowerShellTool() ? [getPowerShellTool()] : [])
```

### 3.2 "为什么需要这么复杂的条件注册？"

**原因 1：A/B 测试**
- 新工具先给 10% 用户开启
- 观察效果再全量推广

**原因 2：差异化构建**
- `ant` 版本（Anthropic 内部）有额外的工具
- 外部版本没有 TungstenTool 等内部工具

**原因 3：性能优化**
- 不需要的工具不进入产物
- 减少 bundle size

**trade-off**：
- **好处**：灵活性高，可控性强
- **坏处**：`getAllBaseTools()` 变得非常复杂
- 300+ 行的函数，满是条件判断
- **这是代码腐败的迹象**

---

## 四、与阶段一的连接

### 4.1 架构上的连接

```
阶段一：QueryEngine 核心循环
    ↓
submitMessage() 创建 ToolUseContext
    ↓
context 包含 canUseTool（权限检查函数）
    ↓
工具执行时，context 传递给 tool.call()
    ↓
tool.call() 内部调用 checkPermissions()
```

### 4.2 状态管理的连接

阶段一学的 Store：
```typescript
// 工具的权限状态存在 AppState 里
toolPermissionContext: {
  mode: 'default'
  alwaysAllowRules: {...}
  alwaysDenyRules: {...}
}
```

工具执行时读取这个 context：
```typescript
// tool.call() 内部
const permission = await tool.checkPermissions(input, context)
if (permission.behavior === 'ask') {
  // 弹窗
}
```

### 4.3 整体架构串起来

```
main.tsx（启动）
    ↓
launchRepl → AppStateProvider（状态）
    ↓
REPL → 用户输入
    ↓
QueryEngine.submitMessage()
    ↓
query() → API 调用
    ↓
工具调用：canUseTool() → Tool.call()
    ↓
工具执行结果 → Store 更新
    ↓
REPL 重新渲染
```

---

## 五、对 OpenClaw 的落地规划

### 5.1 OpenClaw 现状（vs Claude Code）

| 维度 | OpenClaw | Claude Code | 差距 |
|------|----------|------------|------|
| 工具定义 | SKILL.md（文档） | Tool.ts（代码） | ❌ 无代码级定义 |
| 工具描述 | 静态字符串 | 动态函数 | ❌ 无动态描述 |
| 输入验证 | 无 | `validateInput()` | ❌ 无验证 |
| 权限控制 | 无 | 四级模式+规则引擎 | ❌ 无权限抽象 |
| 工具注册 | MCP 配置 | Feature Flag | ❌ 无条件注册 |
| 工具执行 | wecom_mcp 调用 | 原生 `call()` | ❌ 无原生执行 |

### 5.2 下一步行动

**短期（1-2 周）：**

1. **理解现有架构**
   - OpenClaw 的 wecom_mcp 工具调用链路是什么？
   - SKILL.md 是怎么被解析和执行的？

2. **不需要做的事情**
   - 不需要把 SKILL.md 改成 Tool.ts（成本太高）
   - 不需要引入权限规则引擎（OpenClaw 场景不需要）
   - 不需要实现 `isConcurrencySafe`（MCP 调用是同步的）

**中期（1 个月）：**

1. **增强 SKILL.md 的描述能力**
   - 让 description 支持动态参数
   - 参考 Claude Code 的动态 description

2. **权限模型（如果需要）**
   - 如果 OpenClaw 要控制"谁能调用什么 skill"
   - 可以参考 Claude Code 的 `alwaysAllowRules` 模式

**长期（季度）：**

1. **Skill → Tool 演进（如果需要）**
   - 如果 OpenClaw 需要"原生执行"的工具
   - 可以考虑引入 Tool.ts 的设计

### 5.3 OpenClaw 真正需要学的是什么？

**不需要学 Claude Code 的：**
- Ink/React CLI UI（OpenClaw 没有终端 UI）
- CLI 启动优化（Gateway 场景不同）
- Bash 工具的各种复杂逻辑（企业微信工具不需要）

**真正需要学的：**
- 工具描述的动态化（让用户知道"正在操作什么"）
- 权限抽象的设计思路（如果未来需要）
- 工具注册的条件模式（Feature Flag）

---

## 六、深度反思：Claude Code Tool 系统的"红旗"

### 6.1 代码腐败警告

**红旗 1：Tool.ts 有 693 行**
- 一个接口定义文件，接近 700 行
- 说明接口承担了太多职责

**红旗 2：tools.ts 的 getAllBaseTools() 有 300+ 行**
- 满是条件判断的数组构建
- 每加一个工具，改动都很大
- 这是"shotgun surgery"（霰弹修改）味道

**红旗 3：eslint-disable 满天飞**
- 为了 DCE，代码充满特殊注释
- 这是"用代码整洁换产物优化"的代价

### 6.2 过度工程的迹象

**Tool 接口的 30+ 方法**：
- `isSearchOrReadCommand()` — UI 显示用
- `getToolUseSummary()` — UI 显示用
- `getActivityDescription()` — UI 显示用
- `userFacingName()` — UI 显示用
- `interruptBehavior()` — 生命周期

**问题**：这些方法把 UI 逻辑耦合进了 Tool 接口。

如果 Claude Code 换一个 UI 框架（比如不用 Ink），这些代码都要改。

### 6.3 我的结论

Claude Code 的 Tool 系统是一个**高内聚、高复杂度**的设计。

**适合 Claude Code 的场景**：
- CLI 工具，工具是核心功能
- 需要细粒度的权限控制
- 需要动态描述和 UI 反馈
- 需要复杂的编排策略

**不适合 OpenClaw 的场景**：
- 企业微信工具是"MCP 调用"，不是原生执行
- 工具的复杂度在 MCP 服务端，不在 OpenClaw
- SKILL.md 文档驱动是合理的折中

**真正对 OpenClaw 有价值的**：
1. 动态描述的设计思路（让用户知道"正在操作什么"）
2. 工具注册的条件模式（Feature Flag）
3. 不要过度设计：SKILL.md 文档驱动是合理的

---

_Last updated: 2026-03-31_
