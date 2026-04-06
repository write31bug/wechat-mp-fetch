# Mem0 集成 OpenClaw 调研报告

**调研时间：** 2026-04-06  
**调研人：** dev subagent  
**背景：** 金哥希望给 OpenClaw 加上 Mem0 记忆系统，解决"记忆依赖 LLM 主动"的问题

---

## 一、方案概览

| 方案 | 安装方式 | API Key | 数据隐私 | 成本 |
|------|---------|---------|---------|------|
| **官方插件（Platform 模式）** | `openclaw plugins install @mem0/openclaw-mem0` | 需要 `${MEM0_API_KEY}` | 数据发往 Mem0 Cloud | Hobby 免费（10K add/月），Starter $19/月起 |
| **官方插件（Open-Source 模式）** | 同上 | 需要 `${OPENAI_API_KEY}`（嵌入/LLM用） | 完全本地 | 仅 LLM API 成本 |
| **社区插件（serenichron）** | 替换 `plugins.slots.memory` | 取决于自部署配置 | 完全本地 | 仅基础设施成本 |

---

## 二、官方插件 `@mem0/openclaw-mem0`

### 2.1 安装

```bash
openclaw plugins install @mem0/openclaw-mem0
```

安装后插件被放入 `~/.openclaw/extensions/openclaw-mem0/`，并自动注册到 `openclaw.json`。

### 2.2 两种运行模式

#### Platform 模式（Mem0 云服务）

需要从 [app.mem0.ai](https://app.mem0.ai) 获取 API Key。

```json5
// openclaw.json → plugins.entries
"openclaw-mem0": {
  "enabled": true,
  "config": {
    "mode": "platform",
    "apiKey": "${MEM0_API_KEY}",
    "userId": "alice"  // 自定义唯一标识符
  }
}
```

#### Open-Source 模式（完全自托管）

不需要 Mem0 API Key，但默认需要 `OPENAI_API_KEY`（用于 embedding 和 LLM 提取）。

```json5
"openclaw-mem0": {
  "enabled": true,
  "config": {
    "mode": "open-source",
    "userId": "alice"
  }
}
```

可自定义 embedding、向量库、LLM 提供者：

```json5
"config": {
  "mode": "open-source",
  "userId": "alice",
  "oss": {
    "embedder": { "provider": "openai", "config": { "model": "text-embedding-3-small" } },
    "vectorStore": { "provider": "qdrant", "config": { "host": "localhost", "port": 6333 } },
    "llm": { "provider": "openai", "config": { "model": "gpt-4o" } }
  }
}
```

可选向量库：`memory`（内存，默认）、`qdrant`、`chroma` 等。  
可选 Embedding/LLM：`openai`、`ollama`（本地）、`anthropic` 等。

### 2.3 核心功能

- **Auto-Recall**：每轮对话前自动注入相关记忆到上下文
- **Auto-Capture**：对话后自动提取值得存储的信息
- **5 个 Agent Tools**：`memory_search`、`memory_list`、`memory_store`、`memory_get`、`memory_forget`
- **双记忆范围**：Session（短期，按 `run_id` 隔离）和 User（长期，跨会话持久化）

### 2.4 Mem0 定价（Platform 模式）

| 套餐 | 价格 | Add 请求/月 | Retrieval/月 |
|------|------|------------|--------------|
| Hobby | 免费 | 10,000 | 1,000 |
| Starter | $19/月 | 50,000 | 5,000 |
| Pro | $249/月 | 500,000 | 50,000 |
| Enterprise | 定制 | 无限制 | 无限制 |

Hobby 套餐足够个人轻量使用。另有 Startup 计划，面向 <$5M 融资团队，赠送 3 个月 Pro。

---

## 三、自托管替代方案

### 3.1 官方 Open-Source 模式

本质上就是自托管方案。需额外运行：
- **Qdrant**（向量数据库）：`docker run -p 6333:6333 qdrant/qdrant`
- **Ollama**（可选，本地 LLM）：`ollama serve`
- **Mem0 REST API**（可选）：自建或用 Mem0 开源包起服务

### 3.2 社区插件 `serenichron/openclaw-memory-mem0`

- GitHub：[github.com/serenichron/openclaw-memory-mem0](https://github.com/serenichron/openclaw-memory-mem0)
- 思路：用 Mem0 REST API 替换默认 LanceDB backend
- 暴露 3 个工具：`memory_recall`、`memory_store`、`memory_forget`
- 配置方式：在 `plugins.slots.memory` 将 `"memory-lancedb"` 替换为 `"memory-mem0"`
- 优点：接入任何支持 Mem0 REST API 的后端，灵活度高

### 3.3 FalkorDB 方案

- GitHub：[FalkorDB/openclaw-mem0-demo](https://github.com/FalkorDB/openclaw-mem0-demo)
- 用 FalkorDB（图形数据库）作为 Mem0 的持久化层，适合需要关系图谱的场景

### 3.4 Jinstronda 方案

- 原计划调研 `Jinstronda/openclaw-mem0-memory`，但该仓库当前 404（可能已下线或改名）
- 搜索显示定位为"Supermemory 的免费替代"，实际可行性存疑

---

## 四、安装步骤（Platform 模式，最简路径）

1. **注册 Mem0 账号**：前往 [app.mem0.ai](https://app.mem0.ai) 获取 API Key
2. **安装插件**：
   ```bash
   openclaw plugins install @mem0/openclaw-mem0
   ```
3. **配置 openclaw.json**（或设置环境变量）：
   ```json
   "plugins": {
     "entries": {
       "openclaw-mem0": {
         "enabled": true,
         "config": {
           "mode": "platform",
           "apiKey": "${MEM0_API_KEY}",
           "userId": "jin-ge"  // 换成你自己的标识
         }
       }
     }
   }
   ```
4. **设置环境变量**：
   ```bash
   export MEM0_API_KEY="your-key-here"
   ```
5. **重启 Gateway**：
   ```bash
   openclaw gateway restart
   ```
6. **验证**：
   ```bash
   grep "openclaw-mem0: initialized" ~/.openclaw/logs/gateway.log | tail -1
   # 期望输出含：openclaw-mem0: initialized (mode: platform, user: ..., autoRecall: true, autoCapture: true)
   ```

---

## 五、潜在坑

### 5.1 稳定性 & 可用性
- **Platform 模式**：依赖 Mem0 云服务可用性，若 Mem0 宕机则记忆功能全停
- **Open-Source 模式**：需自行维护 Ollama/Qdrant 等服务，有额外运维成本

### 5.2 隐私
- **Platform 模式**：对话内容会发送到 Mem0 服务器（虽然只提取事实，不传原始日志）
- **Open-Source 模式**：所有数据本地处理，隐私最优

### 5.3 成本
- Platform Hobby 免费版：10K add + 1K retrieval/月，超量计费
- OpenAI API 费用：embedding + LLM 提取会产生 token 消耗

### 5.4 已知 Bug
- **historyDbPath 必须为绝对路径**：LaunchAgent 模式下 `process.cwd()` 是 `/`，相对路径会解析到 `/memory.db` 导致 SQLite 无法打开，陷入 crash loop。**必须手动设置绝对路径**：
  ```json
  "oss": {
    "historyDbPath": "/absolute/path/to/.openclaw/memory/history.db"
  }
  ```
- **多 Agent 场景下全局占用 memory slot**：`@mem0/openclaw-mem0` 插件安装后会占用全局 `memory` slot，无法按 Agent 独立配置记忆系统（见 [mem0#4126](https://github.com/mem0ai/mem0/issues/4126)）

### 5.5 API Key 安全性
- ClawHub 的安全扫描指出：registry 元数据未声明 `MEM0_API_KEY` 依赖，但 SKILL.md 文档中确实使用了 `${MEM0_API_KEY}`。这是文档不一致，不影响安全，但需要注意插件安装时已声明了该环境变量。

---

## 六、方案推荐

| 场景 | 推荐方案 |
|------|---------|
| **快速尝鲜 / 个人使用** | Platform Hobby 模式，零运维 |
| **在意隐私 / 生产环境** | Open-Source 模式 + Ollama + Qdrant |
| **需要图形记忆 / 关系推理** | FalkorDB 方案 |
| **多 Agent 精细化控制** | serenichron 社区插件（按 slot 配置） |

---

## 七、参考链接

- Mem0 官方文档：https://docs.mem0.ai/integrations/openclaw
- Mem0 官网定价：https://mem0.ai/pricing
- ClawHub Mem0 Config Skill：https://clawhub.ai/nyrosveil/mem0-config
- 社区插件（serenichron）：https://github.com/serenichron/openclaw-memory-mem0
- FalkorDB Demo：https://github.com/FalkorDB/openclaw-mem0-demo
- Open Issue（多 Agent 支持）：https://github.com/mem0ai/mem0/issues/4126
