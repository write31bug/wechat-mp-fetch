# 浏览器自动化工作流 demo 设计文档

**任务：** T-D-001
**负责人：** dev
**状态：** ✅ 已完成

## 目标

把 `agent-browser` + 状态管理 串成**多步骤可交互的浏览器机器人**，
实现：打开页面 → 等内容 → 点击按钮 → 截取结果 → 继续下一步的完整闭环。

> clawflow 尚未安装，当前用轻量 JSON 状态文件替代，待 clawflow 就位后可无缝迁移。

---

## 核心架构

```
┌─────────────────────────────────────────────┐
│              Workflow Orchestrator           │
│         (browser-workflow-runner.js)         │
├─────────────────────────────────────────────┤
│  Step 1: open → snapshot → parse refs       │
│  Step 2: interact (click/fill) → wait       │
│  Step 3: snapshot → extract data            │
│  Step 4: save state / load to next step     │
└─────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────┐
│            agent-browser CLI                 │
│   (headless Chromium, ref-based selection)  │
└─────────────────────────────────────────────┘
```

## 工作流状态机

```
IDLE → STEP_1_RUNNING → STEP_1_DONE
   → STEP_2_RUNNING → STEP_2_DONE
   → ... → COMPLETE / ERROR
```

每个步骤的输出：
- `snapshot.json` — 页面快照（含 refs）
- `interaction.json` — 本步操作记录
- `workflow-state.json` — 全局状态（当前步骤、cookies、变量）

---

## Demo 场景：Moltbook 自动发帖流程

**场景：** 登录 Moltbook → 打开发帖页 → 填写标题和正文 → 提交

```
step-1-login.js    → 打开登录页，填写账号密码，提交，保存 auth state
step-2-compose.js  → 加载 auth state，打开发帖页，截图确认
step-3-submit.js   → 填写内容，提交，截图确认
```

---

## 文件结构

```
output/
└── docs/
    └── browser-automation-workflow-design.md   ← 本文档
└── data/
    └── browser-workflow/
        ├── workflow-runner.js          ← 主调度器
        ├── steps/
        │   ├── step-1-login.js
        │   ├── step-2-compose.js
        │   └── step-3-submit.js
        ├── state/
        │   └── workflow-state.json    ← 运行时状态
        └── results/
            └── run-2026-04-05/
                ├── step-1-snapshot.json
                ├── step-2-snapshot.json
                └── step-3-snapshot.json
```

---

## 下一步（可行动项）

- [ ] **clawflow 集成**：将 JSON 状态文件替换为 clawflow 流程管理，实现状态持久化 + 断点恢复
- [ ] **多 session 并行**：利用 `agent-browser` 的 `--context` 参数，同时跑多个浏览器上下文执行不同任务
- [ ] **错误重试机制**：在 `workflow-runner.js` 中加入重试逻辑，单步失败自动重试最多 3 次，3 次都失败则中断并报警
