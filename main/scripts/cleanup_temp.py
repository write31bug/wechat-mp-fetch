# temp 目录自动清理脚本
temp_dir = r'E:\openclaw\main\temp'
flag_file = temp_dir + '\\last_cleanup.txt'
from datetime import datetime
today = datetime.now().strftime('%Y-%m-%d')
import os, shutil

removed = 0

# 检查今天是否已清理
if os.path.exists(flag_file):
    with open(flag_file, 'r', encoding='utf-8') as f:
        if f.read().strip() == today:
            print('今日已清理，跳过')
            exit(0)

# 清理 temp 根目录临时文件（保留 last_cleanup.txt）
for item in os.listdir(temp_dir):
    path = os.path.join(temp_dir, item)
    if item == 'last_cleanup.txt' or item == 'wip':
        continue
    if os.path.isfile(path):
        os.remove(path)
        print(f'Deleted: {item}')
        removed += 1
    elif os.path.isdir(path):
        shutil.rmtree(path)
        print(f'Deleted dir: {item}')
        removed += 1

# 清理 wip 里超过7天的文件
wip_dir = os.path.join(temp_dir, 'wip')
if os.path.exists(wip_dir):
    from datetime import timedelta
    cutoff = datetime.now() - timedelta(days=7)
    for item in os.listdir(wip_dir):
        path = os.path.join(wip_dir, item)
        if os.path.isfile(path):
            mtime = datetime.fromtimestamp(os.path.getmtime(path))
            if mtime < cutoff:
                os.remove(path)
                print(f'Deleted wip: {item}')
                removed += 1

# 更新时间戳
with open(flag_file, 'w', encoding='utf-8') as f:
    f.write(today)

print(f'Done. Removed: {removed} items')
