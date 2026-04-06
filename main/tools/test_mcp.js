const { execSync } = require('child_process');

const service = 'tencent-docs';
const method = 'create_space';
const args = { title: 'testkb', description: 'test knowledge base' };

// Use key=value style which avoids JSON parsing issues
const cmd = `mcporter call ${service} ${method} title="${args.title}" description="${args.description}"`;

try {
  const result = execSync(cmd, { encoding: 'utf8', timeout: 30000 });
  console.log('SUCCESS:', result);
} catch(e) {
  console.log('STDOUT:', e.stdout);
  console.log('STDERR:', e.stderr);
}
