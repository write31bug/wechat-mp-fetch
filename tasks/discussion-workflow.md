# 团队异步讨论流程

## 核心理念

多 agent 讨论时，用**本地文件**代替**会话传递**，避免 context 膨胀导致 token 浪费。

## 目录结构

```
E:\openclaw\tasks\discussion\
└── {YYYY-MM-DD}_{topic_slug}\
    ├── manifest.json      ← 任务总纲
    ├── dev.md             ← 各 agent 观点
    ├── writer.md
    ├── finance.md
    └── summary.md         ← 汇总结论
```

## manifest.json 结构

```json
{
  "id": "uuid",
  "topic": "议题标题",
  "background": "背景说明",
  "goal": "要达到什么结果",
  "agents": ["dev", "writer", "finance"],
  "status": "in_progress",
  "created": "2026-04-06T21:30:00+08:00",
  "contributions": {
    "dev": { "status": "pending", "file": "dev.md" },
    "writer": { "status": "pending", "file": "writer.md" },
    "finance": { "status": "pending", "file": "finance.md" }
  }
}
```

## 流程

```
金哥 → main：发起讨论（背景+目标+参与agent）

main：
  1. 创建 E:\openclaw\tasks\discussion\{date}_{topic}\ 目录
  2. 写入 manifest.json
  3. 并行 sessions_send 派发给各 agent（mode="run"，单次）
  4. 各 agent 读取 manifest → 写观点到对应的 .md → 更新 manifest status
  5. main 轮询 manifest，当所有 contributions status=done
  6. 读取所有 .md → 写入 summary.md → 汇报金哥
```

## 各 agent 的 .md 格式

```markdown
# [agent] 对「xxx」的观点

## 核心结论
一句话结论

## 分析逻辑
2-3 句支撑理由

## 风险提示
如有

## 参考数据
数据来源
```

## 汇报格式（main → 金哥）

```
📊 议题：「xxx」
✅ 已汇总，各小弟观点如下：

【dev】...
【writer】...
【finance】...
👉 我的建议：...

存档：E:\openclaw\tasks\discussion\{date}_{topic}\
```

## 设计原则

| 原则 | 说明 |
|------|------|
| 并行派发 | sessions_send 带 timeoutSeconds=120，不等轮次 |
| 单次模式 | 各 agent 用 mode="run"，不留持久 session |
| 状态驱动 | main 轮询 manifest 感知进度，不空等 |
| 超时兜底 | agent 120s 未完成 → 标记 failed，汇总已有的 |
