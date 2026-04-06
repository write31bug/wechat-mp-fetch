# AI Agent Memory System — Round0 调研报告（dev 视角）

**调研时间：** 2026-04-06
**视角：** 技术实现层面
**调研问题：** 如何改善 AI agent 的长期记忆能力

---

## 核心发现

### 1. 记忆需要分层架构，而非塞进 context window

行业共识：把全部记忆塞进 context window 不是真正的长期记忆。生产级方案是**分层记忆架构**（类比 OS 层级）：

| 层级 | 存储位置 | 用途 |
|------|---------|------|
| Working Memory | LLM context | 当前会话的少量关键信息 |
| Short-Term | 外部结构化存储 | 会话级别的上下文摘要 |
| Long-Term | Vector DB / Graph DB | 持久化的用户事实、偏好、流程 |

参考：Medium《Memory Engineering for AI Agents》提出的「registers → cache → RAM → disk」类比，以及 AWS AgentCore 的实践。

---

### 2. 长期记忆分三类，对应不同存储和检索策略

Mem0 论文（arXiv:2504.19413）和官方文档明确提出三类记忆：

- **语义记忆（Semantic）**：用户事实、偏好——用向量数据库存储，语义检索
- **情景记忆（Episodic）**：历史事件、过往交互——带时间戳的事件序列存储
- **程序记忆（Procedural）**：工作流、操作步骤——结构化知识库存储

实践要点：向量检索解决「快速找到相关内容」，图数据库解决「多跳关系推理」，二者互补。

---

### 3. 持久化记忆的写入需要显式策略，不能全量灌入

调研中发现的关键教训：写入记忆要有**过滤和压缩策略**，而不是原始对话全部落盘。具体手段包括：

- 会话结束时调用 LLM 做摘要，只提炼值得长期保留的信息
- Mem0 的 self-improving memory 会从历史交互中持续学习，优化检索相关性
- 与 RAG 不同，agent memory 的核心是「从过去学会改进」，而非「检索文档」

参考：Mem0 Platform + LangGraph 的集成模式——LangGraph 管短期会话状态，Mem0 管跨会话持久记忆。

---

## 可借鉴经验（技术实现层面）

【经验1】分层记忆架构 — 用分层设计替代单一 context：工作集/短时/长期分层，按需注入上下文，避免 context 溢出。

【经验2】三类记忆分类存储 — 将记忆分为语义/情景/程序三类，语义用向量库检索，情景带时序，程序用知识库管理。

【经验3】会话末摘要写入 — 会话结束时 LLM 提炼关键信息落长期存储，而非全量原始对话存入，减少噪声和 token 浪费。

---

## 参考来源

- Mem0 GitHub (mem0ai/mem0) — 52k stars，开源方案
- arXiv:2504.19413 — Mem0 论文
- Medium《Memory Engineering for AI Agents》(2026)
- AWS AgentCore Long-Term Memory Deep Dive
- 47Billion《AI Agent Memory Explained》
