const { chromium } = require('playwright');

(async () => {
  const url = process.argv[2] || 'https://mp.weixin.qq.com/s/Pn_b2O6xVWk29ZjpmdXHEw';
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto(url, { timeout: 30000 });
  await page.waitForFunction(() => !document.URL.includes('login') && document.readyState === 'complete');
  try {
    await page.waitForSelector('#js_content', { timeout: 15000 });
  } catch {
    console.error('无法加载文章内容');
    await browser.close();
    process.exit(1);
  }
  const title = await page.evaluate(() => {
    const el = document.querySelector('h2.rich_media_title') || document.querySelector('#activity_name') || document.querySelector('meta[property="og:title"]');
    return el ? (el.getAttribute('content') || el.textContent || '').trim() : '';
  });
  const text = await page.evaluate(() => {
    const el = document.querySelector('#js_content');
    return el ? el.innerText.trim() : '';
  });
  await browser.close();
  console.log('标题:', title);
  console.log('\n=== 正文 ===\n');
  console.log(text);
})();
