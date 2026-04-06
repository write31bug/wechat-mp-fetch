const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

const service = process.argv[2];
const method = process.argv[3];
const argsFile = process.argv[4];

let argsContent;
try {
  argsContent = fs.readFileSync(argsFile, 'utf8').trim();
} catch(e) {
  console.error('Cannot read args file:', e.message);
  process.exit(1);
}

// Try passing as-is
let result;
try {
  result = execSync(`mcporter call ${service} ${method} --args-string "${argsContent}"`, { encoding: 'utf8', timeout: 30000 });
  console.log(result);
} catch(e) {
  // Try alternative flag
  try {
    const tmpFile = path.join(os.tmpdir(), 'mcp_args_' + Date.now() + '.json');
    fs.writeFileSync(tmpFile, argsContent, 'utf8');
    result = execSync(`mcporter call ${service} ${method} < "${tmpFile}"`, { encoding: 'utf8', timeout: 30000 });
    console.log(result);
    fs.unlinkSync(tmpFile);
  } catch(e2) {
    console.log('Method 1 error:', e.message);
    console.log('Method 2 error:', e2.message);
  }
}
