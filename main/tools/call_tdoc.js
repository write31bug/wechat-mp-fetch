const { execSync } = require('child_process');
const { setTimeout } = require('timers/promises');

function callRaw(service, method, params) {
  const parts = [];
  for (const [k, v] of Object.entries(params)) {
    const sv = typeof v === 'string' ? v : JSON.stringify(v);
    parts.push(`${k}=${JSON.stringify(sv)}`);
  }
  const paramStr = parts.join(' ');
  const cmd = `mcporter call ${service} ${method} ${paramStr}`;
  try {
    const result = execSync(cmd, { encoding: 'utf8', timeout: 60000 });
    return result;
  } catch(e) {
    return e.stdout || e.message;
  }
}

async function pollExport(taskId, maxAttempts = 20) {
  for (let i = 0; i < maxAttempts; i++) {
    console.log(`第 ${i+1} 次轮询...`);
    const r = callRaw('tencent-docs', 'manage.export_progress', { task_id: taskId });
    console.log(r);
    const data = JSON.parse(r);
    if (data.status === 'ok' && data.progress === 100) {
      console.log('\n导出完成!');
      console.log('file_url:', data.file_url);
      return;
    }
    await setTimeout(5000);
  }
  console.log('轮询超时');
}

pollExport('144115263956337781_6ae04c67-bda6-2a1d-04e8-14ab9a90f0b2');
