"""
向 DesktopCal 每日条目追加内容，并重启 dkdockhost 组件刷新显示

用法：python append_and_restart_dock.py <任务内容>
"""
import sqlite3, sys, datetime, json, time, subprocess, os

task_content = sys.argv[1] if len(sys.argv) > 1 else input("请输入任务内容: ")

db_path = r'C:\Users\Administrator\AppData\Roaming\CalendarTask\Db\calendar.db'
today = datetime.date.today().strftime('%Y%m%d')
daily_uid = f'dkcal_mdays_{today}'

# === 1. 写数据库 ===
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("SELECT it_id, it_content, it_history FROM item_table WHERE it_unique_id=?", (daily_uid,))
row = cur.fetchone()

if not row:
    print(f'未找到每日条目 UID={daily_uid}，请先在 DesktopCal 中创建今日条目')
    conn.close()
    sys.exit(1)

existing_content = row[1] or ''
history = []
if row[2]:
    try:
        history = json.loads(row[2])
    except:
        pass

if task_content in existing_content:
    print(f'任务已存在: {task_content}')
    new_content = existing_content
else:
    new_content = existing_content + ('\r\n' if existing_content else '') + task_content
    print(f'追加任务: {task_content}')

now = datetime.datetime.now()
history.append({'content': new_content, 'time': int(now.timestamp())})

cur.execute("""
    UPDATE item_table 
    SET it_content=?, it_history=?, it_mdate=?
    WHERE it_unique_id=?
""", (new_content, json.dumps(history, ensure_ascii=False), now.strftime('%Y-%m-%d %H:%M:%S'), daily_uid))
conn.commit()
conn.close()
print(f'数据库已更新，mdate={now.strftime("%Y-%m-%d %H:%M:%S")}')

# === 2. 重启 dkdockhost ===
print('正在重启 dkdockhost...')
try:
    # 查找 dkdockhost 进程
    result = subprocess.run(
        ['powershell', '-NoProfile', '-Command', 
         "Get-CimInstance Win32_Process -Filter \"name='dkdockhost.exe'\" | Select-Object ProcessId | ConvertTo-Json -Compress"],
        capture_output=True, text=True
    )
    import json as json2
    pids = json2.loads(result.stdout)
    if isinstance(pids, dict):
        pids = [pids]
    
    killed = []
    for p in pids:
        pid = p['ProcessId']
        print(f'  终止 PID={pid}')
        subprocess.run(['taskkill', '/PID', str(pid), '/F'], capture_output=True)
        killed.append(pid)
    
    if killed:
        print(f'已终止 dkdockhost: {killed}')
        # 等待重启
        print('等待 dkdockhost 重启...')
        time.sleep(2)
        
        # 检查是否重启成功
        result2 = subprocess.run(
            ['powershell', '-NoProfile', '-Command',
             "(Get-CimInstance Win32_Process -Filter \"name='dkdockhost.exe'\").Count"],
            capture_output=True, text=True
        )
        try:
            count = int(result2.stdout.strip() or 0)
        except:
            count = 0
        if count > 0:
            print(f'[OK] dkdockhost restarted, running ({count} processes)')
        else:
            print('[WARN] dkdockhost not detected, trying manual start...')
            subprocess.run(
                ['powershell', '-NoProfile', '-Command',
                 "Start-Process 'C:\\Users\\Administrator\\AppData\\Roaming\\CalendarTask\\dkdockhost.exe' -WindowStyle Hidden"],
                capture_output=True
            )
            time.sleep(2)
    else:
        print('未找到运行中的 dkdockhost，尝试直接启动...')
        subprocess.run(
            ['powershell', '-NoProfile', '-Command',
             "Start-Process 'C:\\Users\\Administrator\\AppData\\Roaming\\CalendarTask\\dkdockhost.exe' -WindowStyle Hidden"],
            capture_output=True
        )

except Exception as e:
    print(f'[ERROR] restart failed: {e}')
    print('[HINT] Try restarting DesktopCal manually')

print('\n[OK] Done! Check the desktop widget.')
