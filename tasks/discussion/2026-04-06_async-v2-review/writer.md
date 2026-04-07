# writer 对「异步讨论方案 v2」的评审

## 核心结论
**优化后升。** SQLite 状态管理解决并发安全问题是核心价值，内容侧的体验几乎不变，confidence 字段是个有用的信号但需对齐标准。

---

## 内容体验评审

### 1. .md 文件保留——完全正确

v2 延续了"内容存文件"的设计，对 writer 来说这是最重要的。

- .md 可直接打开阅读，不需要 SQL 客户端或任何工具
- 可以用 git diff、Copilot、Fold 等编辑器原生能力处理
- 写完直接分享链接，不依赖任何中间层
- 多 agent 协作时，其他人可以直接读你的 .md，不会有"我要先查数据库才能看到你的观点"的割裂感

**结论：这点不改，是对的。**

### 2. v2 相比 v1 对 writer 写观点的影响——基本无感，略有改善

- **不变的部分**：写观点的流程完全一样——读 manifest → 写 .md → 告诉 main 完成。格式要求也没变。
- **改善的部分**：v1 里多个 subagent 同时写 manifest.json 有冲突风险（虽然罕见）。v2 用 SQLite WAL 管理 contributions 状态，main 可以准确知道每个 agent 是否完成，不再依赖"文件是否被更新过"这种粗糙的信号。
- **对 writer 来说真正的差异**：并发安全不直接影响我写的文章，但影响我的协作体验——知道系统不会在我写完提交时因为并发冲突把我的状态搞丢，这是安心的。

### 3. 流程清晰度——对 writer 友好

workflow 文档把"各 agent 的 .md 格式"写得很清楚（核心结论 / 分析逻辑 / 风险提示 / 参考数据），写作者有明确的锚点。

---

## confidence 字段价值

**中等，有用但非必须。**

**有用的地方：**
- writer 在某些话题上可能真的了解有限（比如纯金融话题），主动标 low confidence 是诚实的表现，对汇总者（main/金哥）有参考价值
- 可以防止"所有 agent 都说完了但其实有一个是随便写的"被当成 valid input

**不够有用的地方：**
- 目前没有给出判断标准——什么是 high/medium/low 的边界？writer 觉得"我对这个话题只有 30% 把握"算哪个？
- 如果 confidence 填了但没人看，那等于白填

**建议：** 在 workflow 文档里加一句"confidence 填写的参考标准"，让各 agent 填的时候有据可依，不要各写各的。

---

## 具体改进建议

### 建议 1：明确 confidence 的判断标准

目前 schema 里 confidence 是 `TEXT`，值域是 `high/medium/low`，但没有任何指引。不同 agent 对"高信心"的理解可能差很远。

建议在 workflow 文档加一段：
```
confidence 参考标准：
- high：写过相关文章 / 有实际数据支撑 / 有第一手经验
- medium：有逻辑推导但未经实证 / 有不确定性但方向可信
- low：跨领域 / 没有数据支撑 / 直觉判断成分居多
```

这样 writer 在决定填什么的时候有锚点，汇总时 confidence 的信号才有意义。

### 建议 2：明确 .md 的存放位置

目前 workflow 说"内容存 .md 文件"，但没有规定路径规范。各个 agent 写完之后 .md 散落在哪里？

建议：discussions 表加一个 `base_path` 字段（由 main 创建 discussion 时写入），各 agent 的观点文件统一放在 `{base_path}/{agent}.md`。

目前写 manifest.json 的 `file` 字段（比如 `"file": "writer.md"`）是约定路径，但如果 main 没有在创建时明确告知 base_path，agent 可能在不同目录写文件，造成混乱。

---

## v2 是否值得升级？

**值得，但优先级不高。**

核心价值是 SQLite 带来的并发安全和 ACID 保证，这是工程层面的改进，对协作的可靠性有帮助。但对 writer 来说，**日常工作流几乎不变**，主要收益是"manifest.json 不容易坏了"这种幕后保障。

建议先跑一个真实的 discussion 用 v2 跑通全流程，确认 ask_board.py 的 Python 封装好用，再正式切换。不需要为了升级而升级。
