/**
 * 测试价格接口是否可达
 */
const { chromium } = require('playwright')

async function test() {
  const browser = await chromium.launch({ headless: true })
  const page = await browser.newPage()

  // 捕获所有请求响应
  const failed = []
  page.on('response', async resp => {
    if (resp.status() >= 400) {
      failed.push({ url: resp.url(), status: resp.status() })
    }
  })

  await page.goto('http://localhost:6310/#/fundamental-analysis', { waitUntil: 'networkidle', timeout: 15000 })
  await page.waitForTimeout(500)

  await page.locator('input[type="file"]').setInputFiles('E:/openclaw/finance/output/data/汇总持仓.xlsx')
  await page.waitForTimeout(2000)

  // 全选
  await page.locator('.el-table__header-wrapper .el-checkbox__input').first().click()
  await page.waitForTimeout(500)

  // 点分析
  await page.locator('button:has-text("分析")').first().click()
  await page.waitForTimeout(8000)

  console.log('失败的请求:')
  failed.forEach(f => console.log(`  [${f.status}] ${f.url.substring(0, 100)}`))

  // 看看是否弹了成功消息
  const successText = await page.locator('.el-message--success').textContent().catch(() => null)
  console.log('\n成功消息:', successText)

  // 看看控制台有没有更多信息
  const errors = []
  page.on('console', msg => {
    if (msg.type() === 'error') errors.push(msg.text())
  })

  await browser.close()
}

test().catch(e => console.error(e.message))
