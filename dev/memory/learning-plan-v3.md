# Claude Code + OpenClaw 学习计划 v3

> 基于阶段一、二 + OpenClaw 架构研究后的重新规划
> 更新日期：2026-03-31

---

## 核心问题

**我们学 Claude Code 是为了给 OpenClaw 找参考。**

经过研究，我们发现：

| | Claude Code | OpenClaw | 结论 |
|--|-----------|----------|------|
| Tool 系统 | 原生执行，Tool.ts 类 | Gateway RPC 调用 | 架构差异太大，不照搬 |
| Hook 系统 | Skill 级别 hook | 30+ 生命周期 hook | **OpenClaw 更完整** |
| 权限模型 | 四级权限模式 | 无细粒度抽象 | **值得研究** |
| Compaction | 无（手动 /context） | 有（自动） | **Claude Code 缺这个** |
| 上下文管理 | 手动 | Compaction 自动 | 同上 |
| Skill 系统 | Markdown 文档 | 同上 + 多来源 | 可以对比 |

---

## 调整后的学习原则

1. **架构差异太大的不深学**（如 Tool 原生执行）
2. **OpenClaw 比 Claude Code 强的，优先学 OpenClaw**（如 Hooks、Compaction）
3. **Claude Code 有而 OpenClaw 没有的，重点研究**（如权限模型、动态描述）
4. **每个阶段都要回答：OpenClaw 有没有？怎么改？**

---

## 调整后的计划

### 阶段 A ✅ 已完成的沉淀

- ✅ 阶段一：Claude Code 架构概览
- ✅ 阶段二：Tool 系统与权限系统
- ✅ 阶段 B：Hook 系统对比
- ✅ 阶段 C：Compaction 机制
- ✅ 阶段 D：Plugin SDK
- ✅ OpenClaw 架构研究
- ✅ 阶段 A+B 整体复盘
- ✅ 阶段 A+B+C 整体复盘
- ✅ 阶段 A+B+C+D 整体复盘

### 阶段 B ✅ 已完成：Hook 系统对比

**已完成**：
- Claude Code Skill Hook（4种类型：command/prompt/agent/http）
- OpenClaw Plugin Hook（27个生命周期事件）
- 深度对比分析

**落地规划**：
- OpenClaw 的 Hook 系统已经足够强大，不需要新增
- Claude Code 的 Skill Hook 模式可作为参考

### 阶段 C ✅ 已完成：Compaction 机制

**已完成**：
- OpenClaw Compaction 完整流程
- Claude Code 手动 /context vs OpenClaw 自动摘要
- Compaction Hooks（before/after）
- Compaction 安全保障（Safety Timeout + Safeguard）

**落地规划**：
- OpenClaw 的 Compaction 已经很完善，不需要改动
- 这是 OpenClaw 比 Claude Code 强的独特价值

### 阶段 D ✅ 已完成：Plugin SDK

**已完成**：
- OpenClaw Plugin SDK 架构
- Plugin Manifest + Entry Point + SDK API
- wecom-openclaw-plugin 现状分析
- Claude Code vs OpenClaw Plugin 对比

**落地规划**：
- 当前 SKILL.md + MCP 模式已经足够
- 不需要升级到完整 Plugin SDK
- 如需 Hook/Tool 增强，可以按需引入

### 阶段 E 🔨 可选：总结与展望

**目标**：理解两者的 Hook 机制差异，找出可借鉴的点

**学习内容**：
1. Claude Code 的 Skill Hooks（`@before_write` 等）
2. OpenClaw 的 Plugin Hooks（`before_tool_call` 等）
3. **对比**：OpenClaw 的 Hook 比 Claude Code 完整在哪里？

**落地规划**：
- OpenClaw 的 Hook 系统是否足够？需不需要增强？
- Claude Code 的 Skill Hook 能否迁移到 OpenClaw？

### 阶段 C：OpenClaw Compaction 机制

**目标**：理解 Claude Code 没有的自动上下文压缩

**学习内容**：
1. OpenClaw 的 Compaction 机制（`compact.ts`）
2. Compaction Hooks（`before_compaction` / `after_compaction`）
3. **对比**：Claude Code 的手动 /context vs OpenClaw 的自动

**落地规划**：
- OpenClaw 的 Compaction 对我们有什么参考价值？
- Claude Code 能否借鉴？

### 阶段 D：权限模型研究（可选）

**目标**：理解 Claude Code 的权限抽象

**学习内容**：
1. Claude Code 的四级权限模式
2. `alwaysAllowRules` / `alwaysDenyRules`
3. **对比**：OpenClaw 目前没有，是否需要？

**落地规划**：
- OpenClaw 的企业微信工具需要权限控制吗？
- 如果需要，Claude Code 的模式可以借鉴

### 阶段 E：Skill 系统深化（可选）

**目标**：对比两者的 Skill 实现

**学习内容**：
1. Claude Code 的 SkillTool 执行机制
2. OpenClaw 的 Skill 多来源加载
3. **对比**：SKILL.md 格式是否足够？

**落地规划**：
- SKILL.md 需要升级吗？
- Claude Code 的动态 description 能否引入？

---

## 总体优先级

| 优先级 | 阶段 | 原因 |
|--------|------|------|
| 🔴 高 | B：Hook 系统对比 | OpenClaw 更完整，值得学 |
| 🔴 高 | C：Compaction 机制 | Claude Code 没有的，独特价值 |
| 🟡 中 | D：权限模型 | 按需研究 |
| 🟡 中 | E：Skill 系统 | 格式对比 |
| ❌ 跳过 | Tool 原生执行 | 架构差异太大 |

---

## 每个阶段的固定产出

每个阶段结束后，必须回答：

```
1. Claude Code 怎么做？
2. OpenClaw 怎么做？
3. 差距在哪里？
4. 下一步行动是什么？
```

---

_Last updated: 2026-03-31_
