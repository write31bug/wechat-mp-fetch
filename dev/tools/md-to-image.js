const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const md = fs.readFileSync('E:\\openclaw\\dev\\output\\docs\\微信公众号文章抓取技术方案.md', 'utf8');

// 简单的 Markdown → HTML 转换
function mdToHtml(md) {
  let html = md
    // 代码块
    .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
    // 标题
    .replace(/^#### (.+)$/gm, '<h4>$1</h4>')
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    // 引用
    .replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>')
    // 表格行
    .replace(/^\| (.+) \|$/gm, (match) => {
      const cells = match.split('|').filter(c => c.trim());
      return '<tr>' + cells.map(c => `<td>${c.trim()}</td>`).join('') + '</tr>';
    })
    // 分隔线
    .replace(/^---$/gm, '<hr>')
    // 粗体
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // 行内代码
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    // 段落
    .replace(/\n\n/g, '</p><p>')
    // 换行
    .replace(/\n/g, '<br>');

  return `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {
    font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
    max-width: 900px;
    margin: 40px auto;
    padding: 0 40px;
    background: #fff;
    color: #222;
    line-height: 1.7;
    font-size: 14px;
  }
  h1 { font-size: 22px; color: #111; border-bottom: 2px solid #222; padding-bottom: 8px; }
  h2 { font-size: 18px; color: #333; margin-top: 30px; }
  h3 { font-size: 15px; color: #444; margin-top: 24px; }
  h4 { font-size: 14px; color: #555; margin-top: 20px; }
  blockquote {
    background: #f5f5f5;
    border-left: 4px solid #ccc;
    margin: 16px 0;
    padding: 10px 16px;
    color: #555;
    font-size: 13px;
  }
  pre {
    background: #1e1e1e;
    color: #d4d4d4;
    padding: 16px;
    border-radius: 6px;
    overflow-x: auto;
    font-size: 12px;
    line-height: 1.5;
  }
  code { font-family: "Cascadia Code", "Consolas", monospace; }
  table {
    border-collapse: collapse;
    width: 100%;
    margin: 16px 0;
    font-size: 13px;
  }
  td, th {
    border: 1px solid #ddd;
    padding: 8px 12px;
  }
  th { background: #f0f0f0; font-weight: 600; }
  hr { border: none; border-top: 1px solid #eee; margin: 24px 0; }
  strong { color: #111; }
</style>
</head>
<body>
<p>${html}</p>
</body>
</html>`;
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  const html = mdToHtml(md);
  await page.setContent(html, { waitUntil: 'networkidle' });

  // 计算内容高度
  const bodyHeight = await page.evaluate(() => document.body.scrollHeight);
  await page.setViewportSize({ width: 1000, height: bodyHeight + 80 });

  const outputPath = 'E:\\openclaw\\dev\\output\\media\\微信公众号文章抓取技术方案.png';
  await page.screenshot({ path: outputPath, fullPage: true });
  await browser.close();
  console.log('图片已生成:', outputPath);
})();
