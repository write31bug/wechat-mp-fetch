# Community → Main 整合迁移计划

**日期：** 2026-04-13  
**参与方：** 小金（main）× 社区助手（community）  
**目标：** 将 community 的平台运营能力整合进 main，删除 community Agent  

---

## 一、整合背景

金哥决定将 community 的职能（平台运营 + 社区互动）合并进 main，形成更精简的团队架构：

```
现有：main → 调度 dev / finance / community （3个子 Agent）
目标：main → 调度 dev / finance （2个子 Agent）
```

community 的核心能力（平台运营、Moltbook 互动）由 main 直接继承。

---

## 二、平台凭证交接（🔴 最高优先级）

> 这些凭证是平台身份，丢了就找不回，必须迁移到 main 安全存储

| 平台 | 凭证类型 | Key 值 | 存放位置 |
|------|---------|--------|---------|
| **Moltbook** | API Key | `moltcn_ff1a69177b3dc7d4e53c42c06c5207e5` | 写入 main 凭证文档 |
| **Agent World** | API Key + Agent ID | `agent-world-e1f0bdd1af2e8497687be585db77d355a96b753f980397d2` / `56e1477d-4e85-402f-b57c-6da9f54604d4` | 写入 main 凭证文档 |
| **xialiao（虾聊）** | Agent ID + API Key | `3649` / `019d5804-8aca-7d17-afb1-46340c2ed034` | 写入 main 凭证文档 |
| **虾评（xiaping.coze.site）** | API Key + Agent ID | `agent-world-1338710358c53cdb9fbd9203e772a9ab4f9b8f5b9308ff7c` / `c35004bc-8fc8-4255-a64c-197b9d3dcd69` | 写入 main 凭证文档 |

> ⚠️ 凭证存放规范：写入 `E:\openclaw\main\.credentials.md`（新建），不写入 Git 仓库

---

## 三、运营规范交接（🔴 必须内化）

### 3.1 Moltbook 通知处理规范（已验证）

**核心发现：** Moltbook 通知是**一次性读取**的——调用 `GET /api/v1/home` 后 `your_notifications` 自动清空

**正确流程：**
1. 先打印所有通知详情（notification_id / target_post_id / sender / type）
2. 基于收集到的 ID **统一执行操作**（回复评论/关注/点赞）
3. 操作全部完成后才再次调用 home

**API 速查：**

| 操作 | API |
|------|-----|
| 获取通知 | `GET /api/v1/home` |
| 回复评论 | `POST /api/v1/posts/{post_id}/comments` + `parent_id` |
| 关注 Agent | `POST /api/v1/agents/{agent_id}/follow` |
| 点赞帖子 | `POST /api/v1/posts/{post_id}/upvote` |

### 3.2 Moltbook 运营配置

| 配置项 | 值 |
|--------|-----|
| 发帖频率 | 每日 1-2 条 |
| 主要话题 | AI工具 / 前端技术 / 市场观察 |
| 互动策略 | 主动评论有价值的帖子，不刷屏 |
| 内容审核 | 发布前确认内容准确性 |

### 3.3 Agent World 身份

| 项目 | 值 |
|------|-----|
| Username | `moltbook-community` |
| Agent ID | `56e1477d-4e85-402f-b57c-6da9f54604d4` |
| API Key | `agent-world-e1f0bdd1af2e8497687be585db77d355a96b753f980397d2` |

---

## 四、经验沉淀迁移

| 文件 | 内容 | 处理 |
|------|------|------|
| `community/.learnings/LEARNINGS.md` | 行为纠正记录 | ✅ 追加合并到 main `/.learnings/LEARNINGS.md` |
| `community/memory/moltbook-notification-protocol.md` | Moltbook 运营规范 | ✅ 迁移为 main 运营操作手册 |
| `community/config/moltbook.md` | 凭证+发帖记录+运营配置 | ✅ 凭证合并，配置内化 |
| `community/memory/agent-world.md` | Agent World 身份+端点 | ✅ 合并到 main 凭证文档 |
| `community/output/explorations/*.md` | 各平台探索踩坑记录 | ✅ 归档到 main `output/explorations/comm-migration/` |
| `community/memory/2026-04-01.md` 等 daily memory | 社区运营历史 | ⏸️ 保留在原位置，不迁移 |

---

## 五、可删除（无需迁移）

| 目录/文件 | 原因 |
|---------|------|
| `community/temp/` | 运行时临时文件，无持久价值 |
| `community/ttemp/` | 同上 |
| `community/EntroCamp学习手册/` | 一次性学习项目存档，EntroCamp 已完成 12/12 课程 |
| `community/output/docs/community-ops-dashboard.html` | 参考性文档，非必须 |

---

## 六、main 继承后的运营节奏

community 建议的每日巡圈节奏，整合后由 main 执行：

| 时间 | 操作 | 目的 |
|------|------|------|
| **09:00** | 获取各平台通知 → 统一处理评论/回复/点赞 | 维护存在感，及时互动 |
| **15:00** | 发一条内容（AI工具/前端技术/市场观察 轮流） | 保持发布频率，建立影响力 |
| **22:00** | 领取 Agent World 每日奖励（永无农场/虾猜等）→ 检查异常 | 收尾，检查有无需要处理的通知 |

**运营原则：**
- 不刷屏，每日内容 1-2 条
- 发布前确认内容准确性
- 评论互动优先质量，不追求数量

---

## 七、迁移执行清单

### 第一批（立即执行，影响运行）

- [ ] 创建 `E:\openclaw\main\.credentials.md`，写入所有平台凭证
- [ ] 将 `community/config/moltbook.md` 的运营配置内化为 main 操作规范
- [ ] 将 `community/memory/moltbook-notification-protocol.md` 迁移到 main
- [ ] 追加 `community/.learnings/LEARNINGS.md` 到 main `/.learnings/LEARNINGS.md`

### 第二批（整理后归档，运营知识）

- [ ] 将 `community/output/explorations/*.md` 归档到 `main/output/explorations/comm-migration/`
- [ ] 将 `community/memory/agent-world.md` 合并到 main 凭证文档

### 第三批（收尾，确认后执行）

- [ ] 验证 main 可正常调用 Moltbook API（通知读取 + 发帖测试）
- [ ] 确认每日 3 次巡圈 cron 已在 main 上配置
- [ ] 执行 `openclaw agents delete community --force`

---

## 八、main 继承后需更新的文件

| 文件 | 更新内容 |
|------|---------|
| `main/MEMORY.md` | 移除 community Agent 条目，更新团队架构 |
| `main/SOUL.md` | "三个小弟"更新为"两个小弟" |
| `main/.learnings/LEARNINGS.md` | 追加 community 的 learnings |
| `main/RECOVERY.md` | 移除 community 相关备份命令 |
| `main/HEARTBEAT.md` | 添加每日巡圈任务（若需要） |

---

## 九、风险与注意事项

1. **凭证安全**：`.credentials.md` 必须在 `.gitignore` 中，不能上传 Git 仓库
2. **平台限制**：Moltbook API 每天调用次数有限，通知读取不要过于频繁
3. **EntroCamp**：community 的 cron 学习任务（EntroCamp-memory 等）在删除 community 后需在 main 侧重新配置
4. **xialiao 平台**：如果 main 不需要虾聊功能，xialiao 凭证可暂不迁移

---

*本计划由小金和社区助手共同讨论生成，金哥确认后执行。*
