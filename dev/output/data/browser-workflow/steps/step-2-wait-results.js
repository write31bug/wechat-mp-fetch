/**
 * step-2-wait-results.js
 * 第二步：在搜索结果页，提取前几条结果的标题
 */

async function run(session, { runStep, readState, writeState, browserCmd, log }) {
  await runStep('step-2-wait-results', session, {
    waitFor: 'networkidle',
    saveSnapshot: true,
  });

  // 从快照 refs 中提取搜索结果（百度结果通常是 h3.heading 或 link）
  const snapResult = browserCmd('snapshot -i --json', session);
  const refs = snapResult.data?.refs || {};
  
  // 找所有 heading 类型的元素（通常是搜索结果标题）
  const headings = Object.entries(refs)
    .filter(([k, v]) => v.role === 'heading')
    .slice(0, 5);

  // 也尝试找 class 包含 "result" 的 link
  const links = Object.entries(refs)
    .filter(([k, v]) => v.role === 'link' && v.name && v.name.length > 10 && !v.name.includes('百度'))
    .slice(0, 5);

  const allResults = [...headings, ...links].slice(0, 5);
  const uniqueResults = [];
  const seen = new Set();
  for (const [ref, info] of allResults) {
    if (!seen.has(info.name)) {
      seen.add(info.name);
      uniqueResults.push({ ref, title: info.name.slice(0, 80) });
      log('step-2-wait-results', `  发现: ${info.name.slice(0, 60)}`);
    }
  }

  const state = readState();
  state.variables = state.variables || {};
  state.variables.searchResults = uniqueResults;
  state.variables.resultCount = uniqueResults.length;
  writeState(state);

  log('step-2-wait-results', `✓ 共发现 ${uniqueResults.length} 条结果`);
}

module.exports = { run };
