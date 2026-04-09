/**
 * 直接用 Playwright 测试腾讯财经接口是否可达
 */
const { chromium } = require('playwright')

async function test() {
  const browser = await chromium.launch({ headless: true })
  const page = await browser.newPage()

  const results = []
  page.on('response', resp => {
    results.push({ url: resp.url().substring(0, 80), status: resp.status() })
  })

  // 直接在页面内 fetch
  await page.goto('http://localhost:6310/', { waitUntil: 'networkidle', timeout: 15000 })
  await page.waitForTimeout(1000)

  const fetchResult = await page.evaluate(async () => {
    try {
      const res = await fetch('/api/qt/stock/get?secid=1.600519&fields=f43,f44,f170,f57,f58')
      const text = await res.text()
      return { status: res.status, body: text.substring(0, 200) }
    } catch (e) {
      return { error: e.message }
    }
  })

  console.log('Fetch result:', JSON.stringify(fetchResult))

  const qtRequests = results.filter(r => r.url.includes('/api/qt'))
  console.log('Proxy requests:', qtRequests)

  await browser.close()
}

test().catch(e => console.error(e.message))
