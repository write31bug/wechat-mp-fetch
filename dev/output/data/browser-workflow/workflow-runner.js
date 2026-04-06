/**
 * browser-workflow-runner.js
 * 浏览器自动化工作流调度器
 * 
 * 使用方法:
 *   node workflow-runner.js [--session <name>] [--steps <step1,step2>] [--verbose]
 * 
 * 示例:
 *   node workflow-runner.js --session moltbook-post --steps step-1-login,step-2-compose,step-3-submit
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const BASE_DIR = __dirname;
const STATE_DIR = path.join(BASE_DIR, 'state');
const RESULTS_DIR = path.join(BASE_DIR, 'results');

// --- 工具函数 ---

function log(step, msg) {
  console.log(`[${step}] ${msg}`);
}

function ensureDir(dir) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

function readState() {
  const f = path.join(STATE_DIR, 'workflow-state.json');
  return fs.existsSync(f) ? JSON.parse(fs.readFileSync(f, 'utf8')) : {};
}

function writeState(state) {
  ensureDir(STATE_DIR);
  fs.writeFileSync(
    path.join(STATE_DIR, 'workflow-state.json'),
    JSON.stringify(state, null, 2),
    'utf8'
  );
}

function saveSnapshot(stepName, snapshotJson) {
  const runDir = path.join(RESULTS_DIR, `run-${timestamp()}`);
  ensureDir(runDir);
  fs.writeFileSync(
    path.join(runDir, `${stepName}-snapshot.json`),
    snapshotJson,
    'utf8'
  );
  return runDir;
}

function timestamp() {
  return new Date().toISOString().slice(0, 10);
}

/**
 * 执行 agent-browser 命令，返回 JSON 结果
 * 使用 execSync + 长超时，避免启动 Chromium 时被 SIGKILL
 */
function browserCmd(args, session = 'default', verbose = false) {
  const sessionArg = session !== 'default' ? `--session ${session}` : '';
  const cmd = `agent-browser ${args} ${sessionArg}`.trim();
  if (verbose) log('CMD', cmd);
  
  try {
    const out = execSync(cmd, { 
      encoding: 'utf8', 
      timeout: 60000,   // Chromium 启动较慢，给足时间
      maxBuffer: 10 * 1024 * 1024,
      shell: true 
    });
    // 尝试解析最后一行 JSON（agent-browser 输出最后一行为 JSON）
    const lines = out.trim().split('\n');
    for (let i = lines.length - 1; i >= 0; i--) {
      try {
        return JSON.parse(lines[i]);
      } catch {}
    }
    return { raw: out };
  } catch (err) {
    return { error: err.message };
  }
}

/**
 * 通用步骤执行函数
 * @param {string} stepName - 步骤名（如 'step-1-login'）
 * @param {string} session - 浏览器 session 名
 * @param {object} options - { url?, actions?, waitFor?, extract?, saveSnapshot? }
 */
async function runStep(stepName, session, options = {}) {
  const { url, actions = [], waitFor, extract = [], saveSnapshot: shouldSave = true } = options;
  const state = readState();
  
  log(stepName, `开始执行，session=${session}`);
  
  // 1. 打开页面
  if (url) {
    const result = browserCmd(`open ${url}`, session);
    if (result.error) {
      log(stepName, `❌ 打开页面失败: ${result.error}`);
      throw new Error(`open failed: ${result.error}`);
    }
    log(stepName, `✓ 页面已打开: ${url}`);
  }

  // 2. 等待页面稳定
  const waitCmd = waitFor || 'networkidle';
  browserCmd(`wait --load ${waitCmd}`, session);
  log(stepName, `✓ 页面已稳定 (${waitCmd})`);

  // 3. 快照
  const snapResult = browserCmd('snapshot -i --json', session);
  if (snapResult.error) {
    log(stepName, `❌ 快照失败: ${snapResult.error}`);
    throw new Error(`snapshot failed`);
  }
  
  const refs = snapResult.data?.refs || {};
  const snapshotText = snapResult.data?.snapshot || '';
  
  if (shouldSave) {
    saveSnapshot(stepName, JSON.stringify(snapResult, null, 2));
    log(stepName, `✓ 快照已保存`);
  }

  // 4. 执行交互动作
  const vars = state.variables || {};
  
  for (const action of actions) {
    const { type, ref, value, key } = action;
    
    if (type === 'click') {
      const result = browserCmd(`click ${ref}`, session);
      if (result.error) log(stepName, `  ⚠ click ${ref} 失败: ${result.error}`);
      else log(stepName, `  ✓ 点击 @${ref}`);
    }
    else if (type === 'fill') {
      const val = typeof value === 'string' ? value : (vars[value] || '');
      const result = browserCmd(`fill ${ref} "${val}"`, session);
      if (result.error) log(stepName, `  ⚠ fill ${ref} 失败: ${result.error}`);
      else log(stepName, `  ✓ 填写 @${ref} ← "${val}"`);
    }
    else if (type === 'type') {
      const val = typeof value === 'string' ? value : (vars[value] || '');
      const result = browserCmd(`type ${ref} "${val}"`, session);
      if (result.error) log(stepName, `  ⚠ type ${ref} 失败: ${result.error}`);
      else log(stepName, `  ✓ 逐字输入 @${ref} ← "${val}"`);
    }
    else if (type === 'press') {
      const result = browserCmd(`press "${key}"`, session);
      if (result.error) log(stepName, `  ⚠ press "${key}" 失败: ${result.error}`);
      else log(stepName, `  ✓ 按键: ${key}`);
    }
    else if (type === 'wait') {
      const ms = typeof value === 'number' ? value : 1000;
      browserCmd(`wait ${ms}`, session);
      log(stepName, `  ✓ 等待 ${ms}ms`);
    }
    else if (type === 'waitForText') {
      browserCmd(`wait --text "${value}"`, session);
      log(stepName, `  ✓ 等待文本出现: "${value}"`);
    }
    
    // 动作后小等待，让页面响应
    browserCmd('wait 500', session);
  }

  // 5. 提取数据（如有）
  const extracted = {};
  if (extract.length > 0) {
    // 重新快照获取最新状态
    const snap2 = browserCmd('snapshot -i --json', session);
    const refs2 = snap2.data?.refs || {};
    
    for (const ex of extract) {
      const { ref, name, type = 'text' } = ex;
      const r = refs2[ref] || refs[ref];
      if (r) {
        if (type === 'text') {
          const res = browserCmd(`get text ${ref} --json`, session);
          extracted[name] = res.data?.text || r.name || '';
        } else if (type === 'attr') {
          const res = browserCmd(`get attr ${ref} "${ex.attr}" --json`, session);
          extracted[name] = res.data?.[ex.attr] || '';
        } else if (type === 'html') {
          const res = browserCmd(`get html ${ref} --json`, session);
          extracted[name] = res.data?.html || '';
        }
        log(stepName, `  ✓ 提取 @${ref}.${type} → ${name} = "${extracted[name]}"`);
      }
    }
  }

  // 6. 保存 auth state（如果步骤配置了）
  if (options.saveAuthState) {
    const authFile = path.join(STATE_DIR, `${session}-auth.json`);
    browserCmd(`state save ${authFile}`, session);
    log(stepName, `✓ Auth state 已保存: ${authFile}`);
    state.sessions = state.sessions || {};
    state.sessions[session] = { authFile, savedAt: new Date().toISOString() };
  }

  // 7. 更新全局状态
  state.lastStep = stepName;
  state.lastSnapshot = snapshotText.slice(0, 200);
  writeState(state);

  log(stepName, `✓ 步骤完成`);
  return { refs, extracted, snapshot: snapshotText };
}

// --- 主程序入口 ---
async function main() {
  const args = process.argv.slice(2);
  let session = 'default';
  let stepsToRun = null;
  let verbose = false;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--session' && args[i+1]) session = args[++i];
    if (args[i] === '--steps' && args[i+1]) stepsToRun = args[++i].split(',');
    if (args[i] === '--verbose') verbose = true;
  }

  log('WORKFLOW', `=== 浏览器自动化工作流启动 ===`);
  log('WORKFLOW', `session=${session}, steps=${stepsToRun || '全部'}`);

  // 初始化状态
  writeState({ 
    session, 
    startedAt: new Date().toISOString(),
    variables: {}
  });

  // 加载已保存的 auth state
  const authFile = path.join(STATE_DIR, `${session}-auth.json`);
  if (fs.existsSync(authFile)) {
    browserCmd(`state load ${authFile}`, session);
    log('WORKFLOW', '✓ Auth state 已加载（跳过登录）');
  }

  // 读取所有步骤文件
  const stepsDir = path.join(BASE_DIR, 'steps');
  const allSteps = fs.readdirSync(stepsDir)
    .filter(f => f.endsWith('.js') && !f.startsWith('_'))
    .sort();

  const stepsToExecute = stepsToRun || allSteps;

  for (const stepFile of stepsToExecute) {
    const stepName = stepFile.replace('.js', '');
    try {
      const stepModule = require(path.join(stepsDir, stepFile));
      await stepModule.run(session, { runStep, readState, writeState, browserCmd, log, verbose });
    } catch (err) {
      log('WORKFLOW', `❌ 步骤 ${stepName} 执行失败: ${err.message}`);
      process.exit(1);
    }
  }

  log('WORKFLOW', '=== 工作流完成 ===');
}

main().catch(err => {
  console.error('Fatal:', err);
  process.exit(1);
});

module.exports = { runStep, readState, writeState, browserCmd };
