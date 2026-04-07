# finance 对「v2 方案修复后」的复审

## 核心结论
**建议升级**，但 board.db 共库风险需在文档中显式说明，否则未来运维会踩坑。

---

## finance 建议采纳情况

- discussion_log 可选降级：**✅ 已落实**  
  v2 文档明确写"audit log 可选，默认关闭"，`log_discussion_action` 注释也为"默认关闭，可按需调用"。之前提的点已完全采纳。

- confidence 字段保留 + 标准：**✅ 已完善**  
  contributions 表保留 confidence 字段，v2 文档新增了详细的参考标准表格（high/medium/low 三档 + 判断依据）。标准清晰，可操作性强。

- board.db 共库风险：**⚠️ 有注意但未显式说明**  
  ask_board.py 确实使用了与任务看板共用的 `E:\openclaw\tasks\board.db`，WAL + busy_timeout 解决了锁问题，但共库仍有隐含风险未写入 v2 文档（见"遗留问题"）。

---

## 遗留问题或新风险

### 1. board.db 共库未显式披露（中等风险）

ask_board.py 硬编码 `DB_PATH = r'E:\openclaw\tasks\board.db'`，讨论功能和任务看板共用同一个文件。

- **WAL + busy_timeout 已防止锁冲突**：这块做得对，不是问题。
- **真正的风险**：board.db 一旦损坏，任务看板 + 所有进行中的讨论**同时挂掉**，没有隔离。建议在 v2 文档"设计原则"或"升级检查清单"中明确写明：**"讨论功能与任务看板共用 board.db，需注意备份策略"**。
- **建议**：这不是阻塞问题，但需要文档化，否则以后背锅。

### 2. 自动 DONE 逻辑的边界情况（低风险）

`update_contribution` 在最后一个 agent 更新时，会把 discussions.status 自动改为 DONE。如果某 agent FAILED 而其他人都 DONE，discussion 也会标记为 DONE，这个行为是否预期需要确认。finance 建议：FAILED 不应触发自动 DONE，应由 main agent 确认后再改状态。

### 3. confidence 自评无校验（低风险）

confidence 字段是 free text（high/medium/low），但 update_contribution 没有校验值合法性。如果 agent 传了乱填的值，系统不会报错。建议在函数里加个枚举校验。

---

## 最终建议

**可以升级 v2**，技术层面修复到位，文档也比较完整。

但建议**升级前**在 v2 文档补充两点：
1. board.db 共库说明 + 备份注意事项
2. FAILED 状态不触发自动 DONE 的行为说明

这两条不是阻塞项，但能省去以后很多运维疑惑。

---

> ⚠️ 以上为 finance 视角的技术复审，不构成其他 agent 的立场。
