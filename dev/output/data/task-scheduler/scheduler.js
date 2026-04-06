/**
 * task-scheduler.js
 * 轻量级批量任务调度器
 * 
 * 特性：
 * - 并发控制（maxConcurrency）
 * - 任务队列（FIFO）
 * - 失败重试（可配置次数）
 * - 进度回调
 * - 支持 async/await
 * 
 * 使用示例：
 *   const { TaskScheduler } = require('./scheduler');
 *   
 *   const scheduler = new TaskScheduler({ maxConcurrency: 3, retries: 2 });
 *   
 *   scheduler.add('生成图片A', async () => {
 *     const result = await imagine('a beautiful sunset');
 *     return result;
 *   });
 *   
 *   scheduler.add('生成图片B', async () => {
 *     const result = await imagine('a mountain landscape');
 *     return result;
 *   });
 *   
 *   scheduler.onProgress(({ completed, total, current }) => {
 *     console.log(`[${completed}/${total}] ${current.name}`);
 *   });
 *   
 *   const results = await scheduler.runAll();
 *   console.log('完成:', results);
 */

const { EventEmitter } = require('events');

class TaskScheduler extends EventEmitter {
  /**
   * @param {object} options
   * @param {number} options.maxConcurrency - 最大并发数（默认3）
   * @param {number} options.retries - 失败重试次数（默认1）
   * @param {number} options.retryDelay - 重试间隔ms（默认2000）
   */
  constructor(options = {}) {
    super();
    this.maxConcurrency = options.maxConcurrency || 3;
    this.retries = options.retries ?? 1;
    this.retryDelay = options.retryDelay || 2000;
    
    this.queue = [];           // 待执行任务队列
    this.running = 0;          // 当前运行数
    this.completed = 0;         // 已完成数
    this.total = 0;            // 总任务数
    this.results = [];         // 结果列表
    this.errors = [];          // 错误列表
    this._paused = false;
  }

  /**
   * 添加任务到队列
   * @param {string} name - 任务名称
   * @param {Function} fn - async 执行函数
   * @param {object} meta - 附加元数据
   */
  add(name, fn, meta = {}) {
    this.queue.push({ name, fn, meta, status: 'pending' });
    this.total++;
    return this;  // 支持链式调用
  }

  /**
   * 批量添加任务
   * @param {Array<{name, fn, meta}>} tasks
   */
  addBatch(tasks) {
    for (const t of tasks) {
      this.add(t.name, t.fn, t.meta || {});
    }
    return this;
  }

  /**
   * 暂停调度
   */
  pause() {
    this._paused = true;
  }

  /**
   * 恢复调度
   */
  resume() {
    this._paused = false;
    this._dispatch();
  }

  /**
   * 进度回调注册
   */
  onProgress(callback) {
    this.on('progress', callback);
    return this;
  }

  /**
   * 完成回调
   */
  onComplete(callback) {
    this.on('complete', callback);
    return this;
  }

  /**
   * 单个任务错误回调
   */
  onError(callback) {
    this.on('error', callback);
    return this;
  }

  _emitProgress(currentTask) {
    this.emit('progress', {
      completed: this.completed,
      total: this.total,
      running: this.running,
      current: currentTask,
      errors: this.errors.length,
    });
  }

  _sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async _executeTask(task) {
    let lastError;
    
    for (let attempt = 0; attempt <= this.retries; attempt++) {
      try {
        const result = await task.fn();
        return { name: task.name, success: true, result, attempt };
      } catch (err) {
        lastError = err;
        if (attempt < this.retries) {
          await this._sleep(this.retryDelay);
        }
      }
    }
    
    return { name: task.name, success: false, error: lastError, attempt: this.retries + 1 };
  }

  async _dispatch() {
    while (this.running < this.maxConcurrency && this.queue.length > 0 && !this._paused) {
      const task = this.queue.shift();
      task.status = 'running';
      this.running++;
      
      // 并发执行，不 await
      this._executeTask(task).then(result => {
        this.running--;
        this.completed++;
        task.status = result.success ? 'done' : 'failed';
        this.results.push(result);
        
        if (!result.success) {
          this.errors.push(result);
          this.emit('error', result);
        }
        
        this._emitProgress(task);
        
        // 任务完成，继续分发
        this._dispatch();
        
        // 检查是否全部完成
        if (this.completed === this.total) {
          this.emit('complete', {
            results: this.results,
            errors: this.errors,
            total: this.total,
            successCount: this.results.filter(r => r.success).length,
            errorCount: this.errors.length,
          });
        }
      });
    }
  }

  /**
   * 执行全部任务（返回 Promise）
   */
  async runAll() {
    this._dispatch();
    
    // 等待完成
    return new Promise((resolve) => {
      this.on('complete', () => resolve({
        results: this.results,
        errors: this.errors,
        total: this.total,
        successCount: this.results.filter(r => r.success).length,
        errorCount: this.errors.length,
      }));
    });
  }

  /**
   * 返回当前状态快照
   */
  getStatus() {
    return {
      total: this.total,
      running: this.running,
      completed: this.completed,
      queued: this.queue.length,
      errors: this.errors.length,
      paused: this._paused,
    };
  }
}

module.exports = { TaskScheduler };
