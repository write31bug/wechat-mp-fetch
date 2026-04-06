/**
 * scheduler-demo.js
 * 批量任务调度器演示
 * 
 * 演示场景：批量生成 6 张图片（模拟），并发数 2，失败重试 1 次
 */

const { TaskScheduler } = require('./scheduler');

// 模拟一个耗时的 async 任务（随机失败 20%）
function mockAsyncTask(name, delay = 1000) {
  return async () => {
    await new Promise((resolve, reject) => {
      setTimeout(() => {
        if (Math.random() < 0.2) {
          reject(new Error(`❌ ${name} 随机失败`));
        } else {
          console.log(`[EXEC] ✓ ${name} 完成`);
          resolve(`结果: ${name} - ${Date.now()}`);
        }
      }, delay);
    });
    return `done: ${name}`;
  };
}

// 创建调度器：最大并发2，重试1次
const scheduler = new TaskScheduler({
  maxConcurrency: 2,
  retries: 1,
  retryDelay: 500,
});

// 进度回调
scheduler.onProgress(({ completed, total, running, current, errors }) => {
  process.stdout.write(`\r[进度] ${completed}/${total} 完成 | 运行中: ${running} | 失败: ${errors}   `);
});

// 错误回调
scheduler.onError((err) => {
  console.log(`\n[错误] ${err.name}: ${err.error.message} (第${err.attempt}次尝试)`);
});

// 添加 6 个模拟任务
const tasks = [
  { name: '生成封面图-科技风', fn: mockAsyncTask('生成封面图-科技风', 1500) },
  { name: '生成封面图-商务风', fn: mockAsyncTask('生成封面图-商务风', 1200) },
  { name: '生成信息图-图表', fn: mockAsyncTask('生成信息图-图表', 2000) },
  { name: '生成信息图-时间线', fn: mockAsyncTask('生成信息图-时间线', 1800) },
  { name: '生成小红书配图-教程', fn: mockAsyncTask('生成小红书配图-教程', 1000) },
  { name: '生成小红书配图-种草', fn: mockAsyncTask('生成小红书配图-种草', 1300) },
];

scheduler.addBatch(tasks);

console.log('=== 批量任务调度演示 ===');
console.log(`任务数: ${tasks.length}, 最大并发: 2, 重试次数: 1\n`);

const startTime = Date.now();

scheduler.runAll().then(summary => {
  const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
  console.log(`\n\n=== 全部完成 ===`);
  console.log(`耗时: ${elapsed}s`);
  console.log(`成功: ${summary.successCount}/${summary.total}`);
  console.log(`失败: ${summary.errorCount}`);
  
  if (summary.errors.length > 0) {
    console.log('\n失败任务:');
    for (const e of summary.errors) {
      console.log(`  - ${e.name}: ${e.error.message}`);
    }
  }
});
