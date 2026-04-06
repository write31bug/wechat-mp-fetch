# MEMORY.md - 开发助手记忆

> Last updated: 2026-03-31

---

## 关于金哥

- 前端工程师，Vue / React / TypeScript / Node.js / Vite
- 喜欢先理解业务再动手，不喜欢直接开干
- 喜欢分阶段汇报，不喜欢憋很久没有进度更新
- 今天折腾了 baoyu-skills 全套：公众号 + 小红书 + 抖音

---

## 2026-03-31 Claude Code × OpenClaw 研究

### 核心结论

**OpenClaw 是平台，Claude Code 是工具，架构不同，不能互相套用。**

### OpenClaw 的核心优势（Claude Code 没有的）

1. **Compaction**：自动上下文压缩
2. **Hook 系统**：30+ 生命周期 Hook
3. **Plugin SDK**：完整扩展系统
4. **Channel 系统**：多渠道接入

### Claude Code 的核心优势（OpenClaw 可以学的）

1. **动态 Tool 描述**：description 是函数
2. **极简 Store**：40 行手写，不引入重量库
3. **四级权限模式**：细粒度权限控制

### wecom-openclaw-plugin 的建议

**当前 SKILL.md + MCP 模式已经足够，不需要升级到完整 Plugin SDK。**

### 不要做的事

- ❌ 不引入 zustand/jotai（当前模块级状态足够）
- ❌ 不升级到完整 Plugin SDK（SKILL.md 够用）
- ❌ 不做 DCE（Gateway 场景不需要）
- ❌ 不做启动优化（Gateway 不是 CLI）

---

## 技术认知

### 架构决定设计

- Claude Code：单体 CLI → 简单、高性能、无平台扩展性
- OpenClaw：分布式 Gateway → 可扩展、可运维、多渠道

### 学习的正确方式

- ✅ 问"为什么这样设计"
- ✅ 理解"适不适合 OpenClaw"
- ✅ 架构差异大的不照搬
- ❌ 不为了"技术先进"而抄

---

## 重要决策

1. **不引入重量级状态管理**：当前模块级状态足够
2. **不升级 Plugin SDK**：SKILL.md + MCP 是合理的折中
3. **Compaction 不需要改**：OpenClaw 的自动摘要已经完善

_Last updated: 2026-04-04_
