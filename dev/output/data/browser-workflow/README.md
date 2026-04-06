# 浏览器自动化工作流 demo

**产物路径：** `E:\openclaw\dev\output\data\browser-workflow\`

## 架构

```
workflow-runner.js       ← 调度器（读取 steps/ 目录，按顺序执行步骤）
steps/                   ← 步骤脚本（每个 .js 导出 run 函数）
state/workflow-state.json ← 全局状态（跨步骤共享变量、Session）
results/                 ← 每次运行的快照输出
```

## 工作原理

1. **workflow-runner.js** 读取 `steps/` 下所有 `.js` 文件
2. 每个步骤调用 `runStep()` — 打开页面、执行动作、快照、提取数据
3. 步骤之间通过 `workflow-state.json` 共享变量（如搜索词、结果列表）
4. 支持 `--session` 切换浏览器上下文（多账号并行）
5. 支持 `--steps` 指定运行哪些步骤

## 使用方法

```bash
# 跑全部步骤
node workflow-runner.js --session my-session

# 指定步骤
node workflow-runner.js --session my-session --steps step-1-login,step-2-compose

# 调试模式
node workflow-runner.js --verbose
```

## demo 场景：百度搜索 → 结果页 → 点击链接

- `step-1-open-search.js` — 打开百度，填写搜索词，回车提交
- `step-2-wait-results.js` — 快照结果页，提取标题列表
- `step-3-click-result.js` — 点击第一条结果，记录跳转 URL

> ⚠️ 百度有安全验证机制，demo 在部分网络环境会触发验证页面。这是真实网站对 headless 浏览器的常见限制，不影响框架本身的功能。

## 扩展方式

**新增步骤：** 在 `steps/` 下新建 `.js` 文件，导出 `run` 函数即可被自动加载：

```javascript
async function run(session, { runStep, readState, writeState, browserCmd, log }) {
  const state = readState();
  
  await runStep('my-new-step', session, {
    url: 'https://example.com',
    actions: [
      { type: 'fill', ref: '@e2', value: state.variables.username },
      { type: 'click', ref: '@e3' },
    ],
    extract: [
      { ref: '@e5', name: 'result', type: 'text' }
    ]
  });

  state.variables.myResult = result.extracted.result;
  writeState(state);
}

module.exports = { run };
```

## 与 clawflow 的关系

clawflow 尚未安装。当前使用 JSON 文件做状态管理，未来安装 clawflow 后可替换为 clawflow 的流程管理，获得：
- 持久化 flow 状态
- 支持等待外部输入（人工审批节点）
- flow 可视化

当前框架已预留接口，迁移成本低。
