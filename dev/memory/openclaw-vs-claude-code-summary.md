# OpenClaw vs Claude Code 对比总结

> 2026-03-31

---

## 架构对比

```
Claude Code（单体 CLI）
┌─────────────────────────────────┐
│  REPL UI（Ink + React）          │
├─────────────────────────────────┤
│  QueryEngine（Agent 循环）        │
├─────────────────────────────────┤
│  Tool（原生执行）                 │
├─────────────────────────────────┤
│  Skills（文档驱动）               │
└─────────────────────────────────┘

OpenClaw（分布式 Gateway）
┌─────────────────────────────────┐
│  Gateway Server（HTTP/WS）        │
├─────────────────────────────────┤
│  Plugin System（Hooks + Channel）│
├─────────────────────────────────┤
│  Agent Runtime（runEmbeddedPi）   │
├─────────────────────────────────┤
│  Tools（RPC 调用）                │
├─────────────────────────────────┤
│  Skills（多来源）                 │
└─────────────────────────────────┘
```

---

## 核心差异

| 维度 | Claude Code | OpenClaw |
|------|------------|----------|
| **架构** | 单体 CLI | 分布式 Gateway |
| **Tool 执行** | 原生 call() | Gateway RPC |
| **Tool 描述** | 动态函数 | 静态字符串 |
| **权限模型** | 四级权限模式 | 无细粒度抽象 |
| **Hook 系统** | Skill 级别 | 30+ 生命周期 hook |
| **上下文管理** | 手动 (/context) | 自动 Compaction |
| **Channel** | CLI | 10+ 消息渠道 |
| **Plugin** | 无 | 完整插件系统 |

---

## 对 OpenClaw 有价值的（来自 Claude Code）

| Claude Code 设计 | OpenClaw 现状 | 建议 |
|-----------------|--------------|------|
| 动态 Tool 描述 | 静态 | 考虑增强工具 schema |
| 极简 Store | 无响应式 | 观察是否需要 |
| 权限抽象 | 无 | 研究安全模型是否需要 |

---

## OpenClaw 比 Claude Code 多的（值得学的）

| OpenClaw 特色 | 说明 |
|--------------|------|
| **Hook 系统** | 30+ 生命周期 hook |
| **Compaction** | 自动上下文压缩 |
| **Plugin SDK** | 完整插件架构 |
| **Channel 系统** | 多渠道消息接入 |

---

## 下一步研究

1. OpenClaw Hook 系统深度研究
2. OpenClaw Compaction 机制
3. OpenClaw Plugin SDK
4. Tool 描述增强的可能性

---

_Last updated: 2026-03-31_
