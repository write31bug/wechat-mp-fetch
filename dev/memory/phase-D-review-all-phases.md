# 阶段 D 整体复盘 — 阶段一 + 二 + B + C + D

> 2026-03-31 | 连接所有阶段的知识

---

## 一、完整架构对比总结

### Claude Code 架构

```
┌─────────────────────────────────────────────────────────┐
│                     Claude Code                          │
│                                                          │
│  CLI（REPL）                                             │
│      ↓                                                   │
│  QueryEngine（AsyncGenerator 循环）                      │
│      ↓                                                   │
│  Tool.call()（原生执行）                                 │
│      ↓                                                   │
│  Hook（Skill 级别）                                      │
│                                                          │
│  无 Plugin 系统                                           │
│  无自动 Compaction                                        │
│  无 Channel                                               │
└─────────────────────────────────────────────────────────┘
```

### OpenClaw 架构

```
┌─────────────────────────────────────────────────────────┐
│                     OpenClaw                            │
│                                                          │
│  Gateway Server                                          │
│      ↓                                                   │
│  Plugin Registry → Plugin（Hook/Tool/Channel/Provider） │
│      ↓                                                   │
│  Agent Runtime（runEmbeddedPiAgent）                     │
│      ↓                                                   │
│  callGateway()（RPC 调用）                               │
│      ↓                                                   │
│  Hook（30+ 生命周期 Hook）                               │
│      ↓                                                   │
│  Compaction（自动摘要）                                  │
│                                                          │
│  Plugin SDK（完整扩展系统）                              │
└─────────────────────────────────────────────────────────┘
```

---

## 二、Claude Code vs OpenClaw 全对比

| 维度 | Claude Code | OpenClaw | 优势方 |
|------|------------|----------|-------|
| **架构** | 单体 CLI | 分布式 Gateway | 各有 |
| **Agent 循环** | QueryEngine（AsyncGenerator） | runEmbeddedPiAgent（Promise） | 持平 |
| **Tool 执行** | 原生 call() | RPC 调用 | Claude Code |
| **Tool 描述** | 动态函数 | 静态字符串 | Claude Code |
| **Hook 系统** | Skill 级别（4种） | 30+ 生命周期 | **OpenClaw** |
| **Plugin 系统** | ❌ 无 | 完整 SDK | **OpenClaw** |
| **Compaction** | 手动截断 | 自动摘要 | **OpenClaw** |
| **Channel** | ❌ 无 | 10+ 渠道 | **OpenClaw** |
| **权限模型** | 四级权限模式 | 无 | Claude Code |
| **上下文管理** | 手动 /context | Compaction 自动 | **OpenClaw** |

---

## 三、我们的研究成果

### OpenClaw 比 Claude Code 强的（可以借鉴的）

1. **Compaction**（阶段 C）
   - 自动摘要保留上下文
   - Claude Code 完全没有

2. **Hook 系统**（阶段 B）
   - 30+ 生命周期 Hook
   - Claude Code 只有 Skill Hook

3. **Plugin SDK**（阶段 D）
   - 完整的扩展系统
   - Claude Code 没有

### Claude Code 比 OpenClaw 强的（可以学的）

1. **动态 Tool 描述**（阶段二）
   - description 是函数
   - OpenClaw 可以考虑增强

2. **四级权限模式**（阶段二）
   - 细粒度权限控制
   - 如果需要可以参考

---

## 四、wecom-openclaw-plugin 的定位

### 当前架构

```
wecom-openclaw-plugin
    │
    ├── Channel：企业微信渠道 ✅
    │
    ├── Skills：SKILL.md 驱动（不是完整 Plugin SDK）
    │
    └── MCP：通过 mcporter 集成企业微信 API
```

### 是否需要升级？

| 维度 | 当前 | 升级到完整 Plugin | 结论 |
|------|------|-----------------|------|
| Tool 注册 | MCP 调用 | 可以升级到 `api.registerTool()` | ❌ 不需要 |
| Hook 注册 | 无 | 可以升级到 `api.registerHook()` | 🟡 按需 |
| Channel | ✅ 已支持 | 已经是最优 | ✅ 足够 |
| Provider | ❌ 无 | 不需要 | ✅ 不需要 |

**结论**：当前 SKILL.md + MCP 模式已经足够，不需要升级到完整 Plugin SDK。

---

## 五、未来的可能改进

### 短期（1-2 周）

- [ ] **观察现状**：当前架构是否满足需求
- [ ] **不需要改动**：Plugin SDK 不是必须的

### 中期（1 个月）

- [ ] 如果需要 Hook 能力，考虑 `api.registerHook()`
- [ ] 如果需要增强 Tool，考虑 `api.registerTool()`

### 长期（季度）

- [ ] 如果企业微信需要更深的集成，再考虑 Plugin SDK 升级
- [ ] 当前 SKILL.md + MCP 模式是合理的折中

---

## 六、我的新认知

### 6.1 OpenClaw 的平台能力

OpenClaw 不只是一个 Agent 运行时，而是一个**平台**：

```
OpenClaw 平台 = Gateway + Plugin Registry + Agent Runtime + Compaction
                    ↓
              Plugin SDK
                    ↓
    ┌─────────┬─────────┬─────────┐
    │ Channel │Provider │  Tool   │
    │ Plugin  │ Plugin  │  Plugin │
    └─────────┴─────────┴─────────┘
```

### 6.2 Claude Code 的专注

Claude Code 是一个**单用途工具**，不是平台：

```
Claude Code = CLI + QueryEngine + Tool System + Skill System
```

### 6.3 设计哲学差异

| Claude Code | OpenClaw |
|------------|----------|
| 单用途 | 平台化 |
| 简单直接 | 可扩展 |
| 手动控制 | 自动智能 |
| CLI 优先 | 分布式 |

---

_Last updated: 2026-03-31_
