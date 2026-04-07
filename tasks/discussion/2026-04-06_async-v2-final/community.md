# community 对「v2 方案修复后」的复审

## 核心结论
✅ **升级** —— v2 的所有 P0/P1 问题均已修复，核心设计（文件存内容 + DB 存状态）完全对齐 community 的需求。

---

## community 建议采纳情况

### used_in_summary 字段：❌ 未采纳，但有合理替代

v2 schema 的 `contributions` 表没有 `used_in_summary` 字段。
**替代方案**：各 agent 的完整观点存入 `{agent}.md`，main 在汇总时自主决定哪些写入 `summary.md`。这个设计实际上**比 used_in_summary 更灵活**：
- used_in_summary = agent 猜 main 要不要 → 猜错反而误导
- 原文进 .md，main 自由裁剪 → 更可靠

community 接受这个替代方案。

### related_agent 字段：❌ 未采纳，必要性低

跨 agent 引用（如"参考 finance 的某观点"）的需求在当前 workflow 中不突出。各 agent 独立思考后汇总，main 负责综合，暂无强需求。

**如果未来需要**：可以在 `contributions` 表加一列 `referenced_agents TEXT`（JSON array），或在 .md 正文里引用，不改 schema 也能跑。

### discussion_log 可用性：✅ 仍可按需开启

文档明确写了"可选，默认关闭"，ask_board.py 里有 `log_discussion_action()`。社区运营的 audit 需求完全可以按需开启，无异议。

---

## 对社区运营的价值

1. **confidence 自评 → 汇总质量更高**：community 发帖/引用的内容如果 confidence=low，小金可以主动降权处理，避免在社区里散播不确定信息。
2. **文件存内容 → 可复用**：community 写的观点 `.md` 可以直接存档，不用从 DB 里再导出。定期汇总给金哥时也方便整理。
3. **WAL + busy_timeout → 不用担心并发炸库**：community 和 writer/finance/dev 并行交稿时，不会因为 database locked 延误。
4. **audit log 按需开 → 不污染**：社区运营不需要每条日志都记，需要的时候开就行。

---

## 遗留问题

1. **路径规范对临时讨论的适用性**：v2 路径格式 `E:\openclaw\tasks\discussion\{YYYY-MM-DD}_{topic_slug}` 适合正式任务，但 rapid fire 短讨论（如一句观点交换）是否也要走这套？建议明确"什么粒度走正式讨论流程，什么走快速口头交换"。

2. **confidence 自评无校验机制**：agent 可能会倾向于给自己打 high。建议 main 汇总时对全 high 的情况做一次抽检复核。

---

## 最终建议

**支持升级到 v2。**

所有 community 关注的 P0/P1 问题均已修复，核心设计合理。遗留问题属于"用一段时间再看"的优化项，不阻碍当前升级。

建议金哥在正式切换前：
1. 把 ask_board.py 的当前备份一下（以防回退）
2. 在一个真实讨论任务里走一遍 v2 全流程（从 create_discussion 到 summary.md）
3. 确认 confidence 填写习惯符合预期

---

*community 复审完成*
