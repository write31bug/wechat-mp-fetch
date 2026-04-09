/**
 * 基本面分析页面测试
 * 访问 http://localhost:6310/#/fundamental-analysis
 */
const { chromium } = require('playwright')

async function test() {
  const browser = await chromium.launch({ headless: true })
  const page = await browser.newPage()

  // 收集 console errors
  const errors = []
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text())
    }
  })
  page.on('pageerror', err => errors.push('PAGE ERROR: ' + err.message))

  console.log('1. 访问页面...')
  await page.goto('http://localhost:6310/#/fundamental-analysis', { waitUntil: 'networkidle', timeout: 15000 })
  await page.waitForTimeout(2000)

  console.log('2. 检查页面元素...')
  // 检查主要按钮
  const importBtn = await page.locator('button:has-text("导入xlsx")').count()
  console.log(`   - 导入xlsx按钮: ${importBtn > 0 ? '✅' : '❌ 未找到'}`)

  const analyzeBtn = await page.locator('button:has-text("分析")').count()
  console.log(`   - 分析按钮: ${analyzeBtn > 0 ? '✅' : '❌ 未找到'}`)

  const refreshBtn = await page.locator('button:has-text("刷新价格")').count()
  console.log(`   - 刷新价格按钮: ${refreshBtn > 0 ? '✅' : '❌ 未找到'}`)

  const downloadBtn = await page.locator('button:has-text("下载结果")').count()
  console.log(`   - 下载结果按钮: ${downloadBtn > 0 ? '✅' : '❌ 未找到'}`)

  // 检查表格
  const table = await page.locator('.el-table').count()
  console.log(`   - 表格: ${table > 0 ? '✅' : '❌ 未找到'}`)

  // 检查汇总卡片
  const summaryCards = await page.locator('.summary-cards').count()
  console.log(`   - 汇总卡片: ${summaryCards > 0 ? '✅' : '❌ 未找到'}`)

  // 检查刷新间隔选择器
  const intervalSelect = await page.locator('.refresh-interval').count()
  console.log(`   - 刷新间隔选择器: ${intervalSelect > 0 ? '✅' : '❌ 未找到'}`)

  console.log('\n3. 尝试导入 xlsx 文件...')
  // 找到文件输入框
  const fileInput = page.locator('input[type="file"]')
  const fileInputCount = await fileInput.count()
  console.log(`   - 文件输入框: ${fileInputCount > 0 ? '✅' : '❌ 未找到'}`)

  if (fileInputCount > 0) {
    try {
      await fileInput.setInputFiles('E:/openclaw/finance/output/data/汇总持仓.xlsx')
      await page.waitForTimeout(3000)

      // 检查是否导入了数据
      const rows = await page.locator('.el-table__body-wrapper tr').count()
      console.log(`   - 导入后表格行数: ${rows > 0 ? '✅ ' + rows + '行' : '❌ 0行（可能解析失败）'}`)

      // 检查错误提示
      const errorMsgs = await page.locator('.el-message--error').count()
      console.log(`   - 错误提示数量: ${errorMsgs}`)

    } catch (e) {
      console.log(`   - 导入失败: ${e.message}`)
    }
  }

  console.log('\n4. Console Errors:')
  if (errors.length === 0) {
    console.log('   ✅ 无 console error')
  } else {
    errors.forEach(e => console.log(`   ❌ ${e}`))
  }

  await browser.close()
  console.log('\n测试完成')
}

test().catch(e => {
  console.error('测试脚本异常:', e)
  process.exit(1)
})
