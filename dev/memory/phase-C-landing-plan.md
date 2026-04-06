# 阶段 C 落地规划

> 2026-03-31

---

## OpenClaw 现状

**Compaction 机制已经非常完善**：
- 自动触发（budget / overflow）
- 生成摘要保留上下文
- before/after Hook 支持
- Safety Timeout + Safeguard 保障

---

## Claude Code 的做法

- 完全没有自动 Compaction
- 完全靠用户手动 `/context` 命令
- 直接截断历史，不生成摘要

---

## 差距分析

| 维度 | Claude Code | OpenClaw | 差距 |
|------|------------|----------|------|
| Compaction 触发 | 手动 | 自动 + 手动 | OpenClaw 更智能 |
| 摘要生成 | 无 | 有 | OpenClaw 保留更多上下文 |
| Hook 支持 | 无 | before/after | OpenClaw 可扩展 |
| 安全保障 | 无 | Safety Timeout | OpenClaw 更安全 |

**结论**：OpenClaw 在 Compaction 方面**全面领先** Claude Code。

---

## 下一步行动

### 短期（1-2 周）

- [ ] **不需要做任何事**：Compaction 已经完善
- [ ] 观察 Compaction 在实际使用中的表现
- [ ] 如果有问题，考虑调整阈值配置

### 中期（1 个月）

- [ ] 研究 before/after compaction Hook 的高级使用场景
- [ ] 如：compaction 后自动更新记忆系统
- [ ] 如：compaction 前自动清理临时文件

### 长期（季度）

- [ ] Compaction 不需要大的改动
- [ ] 重点是 Plugin 生态的完善（阶段 D）

---

## 与已学模块的连接

### 阶段一（QueryEngine）
- Compaction 发生在 Agent 循环中
- 当 token 达到阈值时，触发 compaction

### 阶段二（Tool 系统）
- Compaction 影响工具调用的历史上下文
- 工具结果的 token 计入 compaction metrics

### 阶段 B（Hook 系统）
- `before_compaction` / `after_compaction` 是 Hook 系统的一部分
- Hook 让 Compaction 过程可干预、可扩展

---

_Last updated: 2026-03-31_
