/**
 * 基本面分析页面深度测试
 */
const { chromium } = require('playwright')

async function test() {
  const browser = await chromium.launch({ headless: true })
  const page = await browser.newPage()

  const errors = []
  const warnings = []
  page.on('console', msg => {
    if (msg.type() === 'error') errors.push(msg.text())
  })
  page.on('pageerror', err => errors.push('PAGE ERROR: ' + err.message))

  console.log('=== 阶段1: 页面加载和导入 ===')
  await page.goto('http://localhost:6310/#/fundamental-analysis', { waitUntil: 'networkidle', timeout: 15000 })
  await page.waitForTimeout(1500)

  await page.locator('input[type="file"]').setInputFiles('E:/openclaw/finance/output/data/汇总持仓.xlsx')
  await page.waitForTimeout(3000)

  const rowsAfterImport = await page.locator('.el-table__body-wrapper tr').count()
  console.log(`导入后行数: ${rowsAfterImport}`)

  console.log('\n=== 阶段2: 测试勾选功能 ===')
  // 勾选第一行
  const firstCheckbox = page.locator('.el-table__body-wrapper .el-checkbox__input').first()
  if (await firstCheckbox.count() > 0) {
    await firstCheckbox.click()
    await page.waitForTimeout(500)
    const checked = await page.locator('.el-table__body-wrapper .el-checkbox__input.is-checked').count()
    console.log(`已勾选行数: ${checked}`)
  }

  // 全选
  const selectAll = page.locator('.el-table__header-wrapper .el-checkbox__input').first()
  if (await selectAll.count() > 0) {
    await selectAll.click()
    await page.waitForTimeout(500)
    const allChecked = await page.locator('.el-table__body-wrapper .el-checkbox__input.is-checked').count()
    console.log(`全选后已勾选行数: ${allChecked}`)
  }

  console.log('\n=== 阶段3: 测试"分析"按钮 ===')
  const analyzeBtn = page.locator('button:has-text("分析")').first()
  const isDisabled = await analyzeBtn.getAttribute('disabled')
  console.log(`分析按钮状态: ${isDisabled !== null ? '❌ disabled（应该有勾选了）' : '✅ enabled'}`)

  if (isDisabled === null) {
    await analyzeBtn.click()
    await page.waitForTimeout(5000) // 等待价格获取和分析

    // 检查是否出现评分
    const scoreElements = await page.locator('.el-table__body-wrapper').locator('text=/\\d+\\.\\d/').count()
    console.log(`表格中出现数字评分的数量: ${scoreElements}`)

    // 检查错误消息
    const successMsg = await page.locator('.el-message--success').count()
    console.log(`成功消息数量: ${successMsg}`)
  }

  console.log('\n=== 阶段4: 测试刷新价格 ===')
  const refreshBtn = page.locator('button:has-text("刷新价格")').first()
  await refreshBtn.click()
  await page.waitForTimeout(5000)
  console.log('刷新价格完成')

  console.log('\n=== 阶段5: 测试详情抽屉 ===')
  const viewBtns = page.locator('button[aria-label="view"]')
  if (await viewBtns.count() > 0) {
    await viewBtns.first().click()
    await page.waitForTimeout(1000)
    const drawer = await page.locator('.el-drawer').count()
    console.log(`抽屉是否打开: ${drawer > 0 ? '✅' : '❌'}`)
    if (drawer > 0) {
      const drawerTitle = await page.locator('.el-drawer__header').textContent()
      console.log(`抽屉标题: ${drawerTitle}`)
      // 关闭抽屉
      const closeBtn = page.locator('.el-drawer__close-btn')
      if (await closeBtn.count() > 0) await closeBtn.click()
    }
  } else {
    console.log('❌ 未找到查看按钮')
  }

  console.log('\n=== 阶段6: 测试下载结果 ===')
  const downloadBtn = page.locator('button:has-text("下载结果")')
  const downloadDisabled = await downloadBtn.getAttribute('disabled')
  console.log(`下载结果按钮: ${downloadDisabled === null ? '✅ enabled' : '❌ disabled（需要先有评分数据）'}`)

  console.log('\n=== 汇总 ===')
  if (errors.length === 0) {
    console.log('✅ 无 JS Error')
  } else {
    console.log(`❌ ${errors.length} 个错误:`)
    errors.forEach(e => console.log(`   - ${e}`))
  }

  await browser.close()
}

test().catch(e => {
  console.error('测试异常:', e.message)
  process.exit(1)
})
