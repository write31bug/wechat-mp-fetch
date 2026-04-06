const { execSync } = require('child_process');
const { setTimeout } = require('timers/promises');

const taskId = '862bbf758763489b81a016a080978f43';

async function poll() {
  for (let i = 0; i < 30; i++) {
    await setTimeout(5000);
    const cmd = `mcporter call tencent-docs manage.export_progress task_id="${taskId}"`;
    let out;
    try {
      out = execSync(cmd, { encoding: 'utf8', timeout: 30000 });
    } catch(e) {
      out = e.stdout;
    }
    console.log(`Poll ${i+1}:`, out);
    try {
      const data = JSON.parse(out);
      if (data.status === 'ok' && data.progress === 100) {
        console.log('DONE! file_url:', data.file_url);
        return;
      }
      if (data.status === 'fail' || (data.code && data.code !== 0)) {
        console.log('FAILED:', out);
        return;
      }
    } catch(e) {}
  }
  console.log('TIMEOUT');
}

poll();
