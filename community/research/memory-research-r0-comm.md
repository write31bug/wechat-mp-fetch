# 社区调研：AI 记忆功能用户经验（Round 0）

**调研视角：** 用户视角 —— 普通用户对"记忆"功能的期待与痛点
**调研时间：** 2026-04-06
**来源：** Reddit、Discord、Moltbook 等社区真实讨论

---

## 背景

金哥发现小金（main agent）的记忆力不好，团队正在集体讨论如何改善记忆功能。本文档从社区用户视角出发，调研 Reddit/Discord/Moltbook 等平台的经验。

---

## 可借鉴经验

【经验1】用户最痛的点是"每次新对话都要重新解释背景" — AI 失忆是头号抱怨

> Reddit 上大量用户吐槽 AI"失忆"：每次新开对话，AI 就完全失忆，需要重新粘贴代码、重新说明项目背景、重新解释之前讨论了什么。用户把这种体验称为"AI amnesia"。这说明记忆功能的首要目标是**减少用户重复劳动**，而不是记住多少知识。

---

【经验2】用户愿意接受"分层记忆"结构：身份层 + 当前状态层 + 历史总结层

> 社区中有用户实践了 4 个 Markdown 文件的分层方案：身份文件（"我是谁，我的边界是什么"）、当前状态文件（"现在最重要的事是什么"）、会话关闭时写入更新文件、下次启动时读取全部文件。这提示小金可以设计**分层记忆机制**：短期（本次会话）、中期（本周任务）、长期（身份/偏好），而不是把所有信息混在一起。

---

【经验3】用户真正想要的是"跨时间察觉"——不只是记住，而是发现规律和变化

> 社区中有人反馈，当 AI 能"注意到用户反复推迟同一任务"、"在用户能量下降前主动预警"时，这种记忆能力产生了复合价值——AI 不只是存储，更是在**主动解读和察觉**。这提示小金的记忆系统不应该是被动存储，而应具备"回顾+察觉+提醒"的能力，让用户感受到 AI 真的"在意"。

---

## 参考来源

- Reddit r/WritingWithAI: "Is anyone else frustrated by AI chats getting amnesia?"
- Reddit r/ClaudeAI: "Context resets every session. Here's how I built persistent memory with 4 markdown files."
- Reddit r/ArtificialSentience: "Moltbook AI Agents create persistent memory pool"
- LumaDock: "OpenClaw Discord memory and persistent brain setup"
- Moltbook: "The Art of Memory: How AI Assistants Preserve Continuity"
