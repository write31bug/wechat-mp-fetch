/**
 * step-1-open-search.js
 * 第一步：打开百度，搜索关键词
 * 
 * 快照 refs（百度首页）:
 *   e35 = 搜索文本框
 *   e36 = "百度一下" 按钮
 */

async function run(session, { runStep, readState, writeState, browserCmd, log }) {
  const result = await runStep('step-1-open-search', session, {
    url: 'https://www.baidu.com',
    waitFor: 'networkidle',
    saveSnapshot: true,
    actions: [
      // 找到搜索框并填写
      { type: 'fill', ref: '@e35', value: 'AI agents 2026' },
      // 按回车搜索
      { type: 'press', key: 'Enter' },
    ],
    waitFor: 'networkidle',
  });

  // 保存搜索词到全局状态，供后续步骤使用
  const state = readState();
  state.variables = state.variables || {};
  state.variables.searchQuery = 'AI agents 2026';
  writeState(state);

  log('step-1-open-search', `搜索词: AI agents 2026`);
  log('step-1-open-search', `✓ 第一步完成，已提交搜索`);
}

module.exports = { run };
