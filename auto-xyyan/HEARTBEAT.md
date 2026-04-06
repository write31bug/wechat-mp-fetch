# HEARTBEAT.md - auto-xyyan 心跳任务

## 逻辑
读取 `daily/last_run.txt`，若日期≠今天则执行一次完整文献搜索，否则静默结束。

## 去重规则
停机多久，每天最多补一次，不重复执行。
