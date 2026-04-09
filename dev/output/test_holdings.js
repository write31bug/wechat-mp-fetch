/**
 * 测试 Holdings 页面能否正常获取数据
 */
const { chromium } = require('playwright')

async function test() {
  const browser = await chromium.launch({ headless: true })
  const page = await browser.newPage()

  const errors = []
  const failed = []
  page.on('console', msg => {
    if (msg.type() === 'error') errors.push(msg.text())
  })
  page.on('response', resp => {
    if (resp.status() >= 400) {
      failed.push({ url: resp.url(), status: resp.status() })
    }
  })

  console.log('Testing Holdings page...')
  await page.goto('http://localhost:6310/#/holdings', { waitUntil: 'networkidle', timeout: 15000 })
  await page.waitForTimeout(5000)

  const rows = await page.locator('.el-table__body-wrapper tr').count()
  console.log('Holdings table rows:', rows)

  const failedFiltered = failed.filter(f => f.url.includes('/api/qt') || f.url.includes('/fundgz'))
  if (failedFiltered.length > 0) {
    console.log('\nFailed API calls:')
    failedFiltered.forEach(f => console.log(`  [${f.status}] ${f.url.substring(0, 100)}`))
  } else {
    console.log('\n✅ No failed API calls in Holdings page')
  }

  if (errors.length > 0) {
    console.log('Console errors:', errors.slice(0, 3))
  }

  await browser.close()
}

test().catch(e => console.error(e.message))
