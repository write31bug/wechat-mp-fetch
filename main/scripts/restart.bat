@echo off
chcp 65001 > nul
title OpenClaw 重启管理器

echo 正在发起停止指令（独立窗口）...
:: 1. 新开一个窗口专门执行 stop，执行完那个窗口自动关闭
start /wait cmd /c "openclaw gateway stop"

echo 等待10秒...
timeout /t 10 /nobreak >nul

echo 正在发起启动指令（独立窗口）...
:: 2. 再新开一个窗口专门执行 start，保持运行
start "OpenClaw Gateway" cmd /k "openclaw gateway"

echo 任务完成！
pause