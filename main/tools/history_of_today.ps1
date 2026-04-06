# 历史今天查询脚本
# 用法: powershell -ExecutionPolicy Bypass -File history_of_today.ps1 [日期]
# 不带参数则查当天

param(
    [string]$Date = (Get-Date -Format "M月d日")
)

$searchQuery = "${Date} 历史上的今天 重大事件"
$url = "https://www.google.com/search?q=" + [System.Uri]::EscapeDataString($searchQuery)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# 截图搜索结果
$browser = Start-Process "msedge" -ArgumentList "--new-window", "--headless", "https://www.google.com/search?q=$([System.Uri]::EscapeDataString($searchQuery))" -PassThru
Start-Sleep -Seconds 5
$browser.Kill()

Write-Output "请告诉用户在浏览器中查看: https://www.google.com/search?q=$([System.Uri]::EscapeDataString($searchQuery))"
