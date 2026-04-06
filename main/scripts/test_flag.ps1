$dir = "E:\openclaw\main"
$flagFile = "$dir\temp\last_cleanup.txt"
Write-Host "Flag path: $flagFile"
Write-Host "Dir exists: $(Test-Path $dir)"
Write-Host "Temp exists: $(Test-Path $dir\temp)"
$today = (Get-Date).ToString("yyyy-MM-dd")
Write-Host "Today: $today"
$today | Out-File -FilePath $flagFile -Encoding UTF8
Write-Host "Written: $(Test-Path $flagFile)"
Get-Content $flagFile
