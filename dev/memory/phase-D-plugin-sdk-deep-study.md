# 阶段 D：Plugin SDK — 深度研究报告

> 研究日期：2026-03-31

---

## 一、OpenClaw Plugin SDK 是什么？

### 1.1 定义

**Plugin = OpenClaw 的扩展系统**

Plugin 可以注册：
- 消息渠道（Channel）：Discord、Telegram、企业微信等
- 模型提供商（Provider）：OpenAI、Anthropic 等
- Agent 工具（Tool）：自定义工具
- 事件钩子（Hook）：生命周期拦截
- 命令（Command）：自定义 slash 命令
- HTTP 路由
- CLI 子命令

### 1.2 架构图

```
┌─────────────────────────────────────────────────────────┐
│                   OpenClaw Core                        │
│  ┌─────────────────────────────────────────────────┐  │
│  │              Plugin Registry                     │  │
│  │  发现 → 验证 → 加载 → 生命周期管理               │  │
│  └─────────────────────────────────────────────────┘  │
│                         │                             │
│         ┌───────────────┼───────────────┐             │
│         ▼               ▼               ▼             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐     │
│  │   Channel   │ │  Provider   │ │    Tool     │     │
│  │   Plugin    │ │   Plugin    │ │   Plugin    │     │
│  └─────────────┘ └─────────────┘ └─────────────┘     │
└─────────────────────────────────────────────────────────┘
```

---

## 二、Plugin 的核心概念

### 2.1 Plugin Manifest

每个 Plugin 需要一个 `openclaw.plugin.json`：

```json
{
  "id": "wecom-openclaw-plugin",
  "name": "企业微信插件",
  "description": "企业微信渠道支持",
  "channels": ["wecom"],
  "skills": ["./skills"],
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {}
  }
}
```

### 2.2 Plugin Entry Point

```typescript
// index.ts
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";

export default definePluginEntry({
  id: "my-plugin",
  name: "My Plugin",
  description: "描述",
  register(api) {
    // 注册工具
    api.registerTool({...})
    // 注册渠道
    api.registerChannel({...})
    // 注册 Hook
    api.registerHook({...})
    // 注册命令
    api.registerCommand({...})
  }
})
```

### 2.3 Plugin API

| 方法 | 作用 |
|------|------|
| `api.registerTool()` | 注册 Agent 工具 |
| `api.registerChannel()` | 注册消息渠道 |
| `api.registerProvider()` | 注册模型提供商 |
| `api.registerHook()` | 注册生命周期 Hook |
| `api.registerCommand()` | 注册 slash 命令 |
| `api.registerHttpRoute()` | 注册 HTTP 路由 |
| `api.registerCli()` | 注册 CLI 子命令 |

---

## 三、Plugin 的发现和加载

### 3.1 发现机制

```
Plugin 发现来源：
1. bundled/ — 内置插件（openclaw 源码里）
2. ~/.openclaw/extensions/ — 用户本地插件
3. ClawHub — 远程插件市场
4. npm — npm 包
```

### 3.2 加载流程

```
openclaw plugins discover
    ↓
读取 openclaw.plugin.json manifest
    ↓
验证 configSchema
    ↓
加载 entry point
    ↓
调用 register(api)
    ↓
注册到 Plugin Registry
```

---

## 四、wecom-openclaw-plugin 的现状

### 4.1 现状

```json
{
  "id": "wecom-openclaw-plugin",
  "channels": ["wecom"],
  "skills": ["./skills"]
}
```

**这是旧版 manifest 格式**。

### 4.2 SKILL 系统

```
wecom-openclaw-plugin/
├── skills/
│   ├── wecom-msg/
│   ├── wecom-contact-lookup/
│   ├── wecom-doc-manager/
│   ├── wecom-edit-todo/
│   ├── wecom-get-todo-list/
│   ├── wecom-get-todo-detail/
│   ├── wecom-meeting-create/
│   ├── wecom-meeting-manage/
│   ├── wecom-meeting-query/
│   ├── wecom-preflight/
│   ├── wecom-schedule/
│   ├── wecom-smartsheet-data/
│   └── wecom-smartsheet-schema/
└── openclaw.plugin.json
```

**当前架构**：Plugin = Channel + Skills（SKILL.md 驱动）

### 4.3 与标准 Plugin SDK 的对比

| 维度 | 标准 Plugin SDK | wecom-openclaw-plugin |
|------|----------------|----------------------|
| Manifest | `openclaw.plugin.json` | ✅ 同上 |
| Entry Point | `definePluginEntry()` | ❌ 无 |
| Tool 注册 | `api.registerTool()` | ❌ 无（MCP 调用） |
| Hook 注册 | `api.registerHook()` | ❌ 无 |
| Skill | SKILL.md 驱动 | ✅ SKILL.md |

**结论**：wecom-openclaw-plugin 使用的是 SKILL.md 驱动模式，不是完整的 Plugin SDK。

---

## 五、Claude Code 有 Plugin 系统吗？

**没有。**

Claude Code 完全**没有 Plugin 系统**。

Claude Code 的扩展方式：
1. **SKILL.md** — 自定义命令/工作流
2. **Settings.json** — 配置调整
3. **环境变量** — 行为控制

**没有**：
- Plugin Manifest
- Plugin SDK API
- Plugin Registry

---

## 六、深度对比分析

### 6.1 OpenClaw Plugin vs Claude Code Skill

| 维度 | OpenClaw Plugin | Claude Code Skill |
|------|----------------|------------------|
| **定义方式** | Manifest + Entry Point | SKILL.md 文档 |
| **能力范围** | Channel/Provider/Tool/Hook/Command | Skill 命令 |
| **注册方式** | 代码注册（register()） | 文档解析 |
| **生命周期** | 完整的 Hook 系统 | 有限的 Skill Hook |
| **配置** | Zod Schema | Frontmatter |

### 6.2 OpenClaw Plugin 的优势

1. **完整的生命周期 Hook**：27 个 Hook 点
2. **多类型注册**：Channel/Provider/Tool/Command
3. **类型安全**：TypeScript SDK API
4. **热插拔**：动态安装/卸载
5. **隔离性**：Plugin 之间相互独立

### 6.3 Claude Code Skill 的优势

1. **简单**：只需要写 Markdown
2. **轻量**：不需要写代码
3. **门槛低**：任何人都可以写

---

## 七、对 OpenClaw 的启发

### 7.1 wecom-openclaw-plugin 的定位

**当前**：使用 SKILL.md 驱动，不需要完整的 Plugin SDK。

**原因**：
- 企业微信的工具通过 MCP 调用，不需要原生 Tool
- Skill 是文档驱动的，更轻量
- 不需要 Channel/Provider 等能力

### 7.2 未来可能的方向

**如果需要**：
- 注册自定义 Hook → 使用 `api.registerHook()`
- 注册自定义 Tool → 使用 `api.registerTool()`
- 注册自定义 Command → 使用 `api.registerCommand()`

**不需要**：
- Channel（企业微信已有）
- Provider（已有 Anthropic）

### 7.3 Plugin SDK 的学习价值

**Plugin SDK 展示了 OpenClaw 的扩展能力上限**：

```
Plugin 可以做到的事：
├── 注册 Agent 工具（Tool）
├── 注册消息渠道（Channel）
├── 注册模型提供商（Provider）
├── 注册生命周期 Hook
├── 注册 slash 命令
├── 注册 HTTP 路由
├── 注册 CLI 子命令
└── 注册服务（Service）
```

---

## 八、阶段 D 复盘

### 8.1 核心发现

1. **OpenClaw 有完整的 Plugin SDK**
   - Manifest + Entry Point + SDK API
   - 支持 Channel/Provider/Tool/Hook/Command
   - Claude Code 完全**没有** Plugin 系统

2. **wecom-openclaw-plugin 使用 SKILL.md 驱动**
   - 不是完整的 Plugin SDK
   - 不需要 Channel/Provider 能力
   - Skill 文档驱动更轻量

3. **Plugin SDK 是 OpenClaw 的扩展上限**
   - 如果未来需要更多能力，可以升级到完整 Plugin
   - 但当前 SKILL.md 模式已经足够

### 8.2 与前面的连接

- **阶段一**：Plugin 在 Agent Runtime 中被加载和执行
- **阶段二**：Plugin 可以注册 Tool（但 wecom 用 MCP）
- **阶段 B**：Plugin Hook 是 Hook 系统的基础
- **阶段 C**：Plugin Hook 参与 Compaction

---

_Last updated: 2026-03-31_
