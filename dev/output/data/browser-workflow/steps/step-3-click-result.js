/**
 * step-3-click-result.js
 * 第三步：点击第一条搜索结果，截图确认
 */

async function run(session, { runStep, readState, writeState, browserCmd, log }) {
  const state = readState();
  const results = state.variables?.searchResults || [];
  
  if (results.length === 0) {
    log('step-3-click-result', '⚠ 没有搜索结果可点击，尝试直接获取当前页面 title');
    const titleResult = browserCmd('get title --json', session);
    log('step-3-click-result', `当前页面标题: ${titleResult.data?.title || 'unknown'}`);
    return;
  }

  const firstRef = results[0].ref;
  log('step-3-click-result', `点击 @${firstRef}: ${results[0].title}`);

  await runStep('step-3-click-result', session, {
    waitFor: 'networkidle',
    saveSnapshot: true,
    actions: [
      { type: 'click', ref: `@${firstRef}` },
      { type: 'wait', value: 3000 },
    ],
    extract: [
      { ref: '@e1', name: 'new-page-title', type: 'text' },
    ]
  });

  const urlResult = browserCmd('get url --json', session);
  const currentUrl = urlResult.data?.url || 'unknown';
  const titleResult = browserCmd('get title --json', session);
  const currentTitle = titleResult.data?.title || 'unknown';

  // 截图
  const screenshotDir = require('path').join(__dirname, '..', 'results');
  const ts = Date.now();
  browserCmd(`screenshot screenshot-${ts}.png`, session);

  state.variables.visitedUrl = currentUrl;
  state.variables.visitedTitle = currentTitle;
  writeState(state);

  log('step-3-click-result', `当前 URL: ${currentUrl}`);
  log('step-3-click-result', `当前标题: ${currentTitle}`);
  log('step-3-click-result', `✓ 第三步完成`);
}

module.exports = { run };
