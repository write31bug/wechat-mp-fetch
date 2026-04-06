const { execSync } = require('child_process');

const cmd = `mcporter call tencent-docs scrape_url url="https://mp.weixin.qq.com/s/JFcHohMLurrCE8q92xEGnQ"`;

try {
  const result = execSync(cmd, { encoding: 'utf8', timeout: 60000 });
  console.log(result);
} catch(e) {
  console.log(e.stdout);
  console.log(e.stderr);
}
