# 阶段 D 落地规划

> 2026-03-31

---

## OpenClaw 现状

**Plugin SDK 已经非常完善**：
- Manifest + Entry Point + SDK API
- 支持 Channel/Provider/Tool/Hook/Command
- 完整的生命周期 Hook

**wecom-openclaw-plugin 当前使用 SKILL.md + MCP 模式**。

---

## Claude Code 的做法

- Claude Code **完全没有 Plugin 系统**
- 扩展方式只有 SKILL.md + Settings.json
- 无法注册自定义 Channel/Provider/Tool

---

## 差距分析

| 维度 | Claude Code | OpenClaw | wecom-openclaw-plugin | 结论 |
|------|------------|----------|----------------------|------|
| Plugin 系统 | ❌ 无 | ✅ 完整 | ❌ SKILL.md 模式 | 足够 |
| Tool 注册 | ❌ 无 | ✅ api.registerTool() | ❌ MCP 调用 | 足够 |
| Hook 注册 | ❌ 无 | ✅ api.registerHook() | ❌ 无 | 足够 |
| Channel | ❌ 无 | ✅ 10+ | ✅ 企业微信 | 最优 |

**结论**：wecom-openclaw-plugin 的 SKILL.md + MCP 模式已经足够，不需要升级到完整 Plugin SDK。

---

## 下一步行动

### 短期（1-2 周）

- [ ] **不需要做任何事**：当前架构已经足够
- [ ] 继续使用 SKILL.md 模式维护企业微信工具
- [ ] 观察是否需要 Hook 或 Tool 增强

### 中期（1 个月）

- [ ] 如果需要 Hook，考虑使用 `api.registerHook()`
- [ ] 如果需要自定义 Tool，考虑使用 `api.registerTool()`
- [ ] 但目前没有明确需求，不需要提前优化

### 长期（季度）

- [ ] Plugin SDK 升级需要明确的业务需求驱动
- [ ] 当前 SKILL.md + MCP 是合理的折中
- [ ] 不为了"技术先进"而升级

---

## 与已学模块的连接

### 阶段一（QueryEngine）
- Plugin 在 Agent Runtime 中被加载

### 阶段二（Tool 系统）
- Plugin 可以注册 Tool（但 wecom 用 MCP）

### 阶段 B（Hook 系统）
- Plugin Hook 是 Hook 系统的基础

### 阶段 C（Compaction）
- Plugin Hook 参与 Compaction

---

_Last updated: 2026-03-31_
