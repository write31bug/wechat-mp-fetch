# dev 对「异步讨论方案」的评审

## 核心结论
**优化后升** —— 设计思路清晰，切中 token 膨胀痛点，但状态驱动模型在工程完整性上还有缺口，修复后可作为团队标配流程。

---

## 真实优点（技术层面）

### 1. Context 边界清晰，token 消耗可量化
各 agent 只读 manifest + 自己历史观点，不存在多轮会话叠加的 context 膨胀。120s 超时兜底让 token 预算可控。比起在同一个 session 里多 agent 交叉对话，这种模式的成本是可预测的。

### 2. 状态机设计降低了协调复杂度
manifest.json 作为单一数据源（Single Source of Truth），main 通过轮询感知进度，不依赖复杂的回调或消息队列。状态流转 `PENDING → IN_PROGRESS → DONE / FAILED` 简单明确，排查问题时日志路径清晰。

### 3. 并行派发真正实现了并行
`sessions_send` 并行触达各 agent，不存在轮次等待。120s 超时 vs 各 agent 独立执行，总耗时由最慢的那个决定，而不是串行总和。这是工程上正确的性能取舍。

### 4. 文件天然支持审计和回溯
所有观点以 .md 形式落盘，`{date}_{topic}` 目录结构便于归档。后续复盘可以直接拿历史文件比对，不用重建上下文。这是会话式讨论做不到的。

---

## 真实缺点（技术层面）

### 1. 轮询机制对 manifest 文件有 IO 竞争风险
main 轮询 `contributions.*.status`，如果并发写入（极端情况下 manifest.json 被多进程同时读写），存在状态损坏风险。当前方案假设单 main → 多 subagent 的星型拓扑，但凡有一个 subagent 的写入逻辑出问题（比如没加 file lock），就会污染状态。**没有 file locking 是工程上的隐患。**

### 2. 120s 超时兜底无法区分「真慢」和「已卡死」
subagent 120s 未响应，main 只能标记 `failed` 并继续汇总已有结果。但如果 agent 实际上在 119s 时还在跑，只是网络抖动导致没来得及写文件，这个 false positive 会丢失一条贡献。没有 progressive status（如 `IN_PROGRESS` 中间态上报），main 对执行进度一无所知。

### 3. subagent 的文件写入没有原子性保障
subagent 写 `dev.md` 是单次 `write` 操作，但如果写入过程中进程被 kill（超时/崩溃），文件会是空文件或截断状态。main 在下一轮轮询中看到 `done` 状态，但文件内容是损坏的。**没有 write-ahead log 或临时文件 + rename 的原子写入模式。**

### 4. manifest 的 `contributions.{agent}.status` 只能从 subagent 侧更新
subagent 拿到任务后是独立的 120s 窗口，main 不知道 agent 是否真的读到了 manifest。如果 subagent session 在派发阶段就失败了（金哥网络问题、main sessions_send 失败），manifest 里没有这个 agent 的任何状态，main 不会知道这次派发失败了。**缺乏「派发成功」的明确回执机制。**

---

## 具体改进建议

### 改进 1：引入文件锁或原子写入
subagent 更新 manifest status 时，使用「写临时文件 → rename 覆盖」的原子模式，避免并发写入冲突。Windows 下可用 `os.replace()` 做原子 rename。这是最小改动、最大收益的修复。

### 改进 2：增加中间状态上报（progress heartbeat）
在 120s 超时窗口内，agent 每 30s 向 manifest 写入一个 `progress: { timestamp, checkpoint: "reading_manifest" | "writing_opinion" | "updating_manifest" }` 字段。main 轮询时不仅看 `done/failed`，还看 progress 是否有心跳。这样可以区分「真卡死」（progress 停很久）和「只是慢」。

### 改进 3：manifest 增加 `dispatch_log` 字段记录派发结果
main sessions_send 后，把每个 agent 的派发结果（成功/失败/超时）写入 `dispatch_log`，让 manifest 自包含完整的生命周期记录。后续审计可以直接从这个字段追溯哪个环节出了问题，不用查 main 的进程日志。

---

## 适用场景边界

**适用：**
- 团队 2~5 个 agent，需要从不同视角（dev/writer/finance/community）独立输出观点
- 议题相对独立，不要求实时交叉讨论和观点碰撞
- 需要存档、回溯、审计的正式讨论场景
- 参与者时区差异大，根本无法同步开会

**不适用：**
- 需要实时辩论、观点碰撞的快速迭代场景（比如方案评审的多轮拉锯）
- 参与者超过 5 个，manifest contributions 字段会变得臃肿，轮询效率下降
- 高度依赖即时反馈的创意类讨论（brainstorm、头脑风暴），异步会扼杀灵感的即时性
- 决策链路短的紧急事务，manifest 创建本身就成了 overhead
