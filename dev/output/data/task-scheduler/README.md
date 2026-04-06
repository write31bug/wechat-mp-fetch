# 批量任务调度脚手架

**路径：** `E:\openclaw\dev\output\data\task-scheduler\`

## 核心模块

```
task-scheduler/
├── scheduler.js    ← 核心调度器（TaskScheduler 类）
├── demo.js        ← 演示脚本（6个模拟任务，并发控制+重试）
└── README.md      ← 本文档
```

## 使用方法

```javascript
const { TaskScheduler } = require('./scheduler');

// 创建调度器
const scheduler = new TaskScheduler({
  maxConcurrency: 3,   // 最大并发数
  retries: 2,          // 失败重试次数
  retryDelay: 2000,    // 重试间隔（ms）
});

// 添加任务
scheduler.add('任务名称', async () => {
  const result = await someAsyncWork();
  return result;
});

// 批量添加
scheduler.addBatch([
  { name: '任务A', fn: async () => {} },
  { name: '任务B', fn: async () => {} },
]);

// 事件回调
scheduler.onProgress(({ completed, total, running, current }) => {
  console.log(`进度: ${completed}/${total}`);
});

scheduler.onError((err) => {
  console.log(`失败: ${err.name} - ${err.error.message}`);
});

// 执行并等待全部完成
const summary = await scheduler.runAll();
console.log(`成功: ${summary.successCount}/${summary.total}`);
```

## 验证结果

demo.js 演示结果：
- 6 个模拟任务（每个 1-2s）
- 并发数 2（每次最多同时跑 2 个）
- 实际耗时 **6.4s**（3 批 × ~2s，符合预期）
- 6/6 全部成功 ✅

## 与 Skill 的结合

所有 baoyu-* skill 的批量执行场景均可使用，例如：

```javascript
const scheduler = new TaskScheduler({ maxConcurrency: 2 });

for (const prompt of prompts) {
  scheduler.add(`生成图-${prompt}`, async () => {
    return await imagine(prompt);
  });
}

const results = await scheduler.runAll();
```

## 限制

- 当前为单进程调度，不支持跨机器分布式
- 重试机制为指数退避（未来可加）
- 无持久化（进程挂了任务丢失），生产环境建议加 DB 持久化
