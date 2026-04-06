"""
向 DesktopCal 每日条目追加内容，并重启主程序刷新 Widget
"""
import sqlite3, sys, datetime, json, time, subprocess, os

task_content = sys.argv[1] if len(sys.argv) > 1 else input("Enter task: ")

db_path = r'C:\Users\Administrator\AppData\Roaming\CalendarTask\Db\calendar.db'
today = datetime.date.today().strftime('%Y%m%d')
daily_uid = f'dkcal_mdays_{today}'

# === 1. Write DB ===
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("SELECT it_id, it_content, it_history FROM item_table WHERE it_unique_id=?", (daily_uid,))
row = cur.fetchone()
conn.close()

if not row:
    print('[ERROR] Daily entry not found')
    sys.exit(1)

existing_content = row[1] or ''
history = []
if row[2]:
    try:
        history = json.loads(row[2])
    except:
        pass

if task_content in existing_content:
    print(f'[INFO] Already exists: {task_content}')
    new_content = existing_content
else:
    new_content = existing_content + ('\r\n' if existing_content else '') + task_content
    print(f'[INFO] Adding: {task_content}')

now = datetime.datetime.now()
history.append({'content': new_content, 'time': int(now.timestamp())})

conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("""
    UPDATE item_table 
    SET it_content=?, it_history=?, it_mdate=?
    WHERE it_unique_id=?
""", (new_content, json.dumps(history, ensure_ascii=False), now.strftime('%Y-%m-%d %H:%M:%S'), daily_uid))
conn.commit()
conn.close()
print(f'[DB] Done at {now.strftime("%Y-%m-%d %H:%M:%S")}')

# === 2. Restart desktopcal + dkdockhost ===
print('[KILL] Stopping processes...')
try:
    # Get PIDs
    r = subprocess.run(
        ['powershell', '-NoProfile', '-Command',
         "Get-CimInstance Win32_Process -Filter \"name='desktopcal.exe' -or name='dkdockhost.exe'\" | ConvertTo-Json -Compress"],
        capture_output=True
    )
    text = r.stdout.decode('utf-8', errors='replace').strip()
    if not text:
        print('[WARN] No processes found')
        pids = []
    else:
        pids_data = json.loads(text)
        if isinstance(pids_data, dict):
            pids_data = [pids_data]
        pids = [p['ProcessId'] for p in pids_data]

    for pid in pids:
        subprocess.run(['taskkill', '/PID', str(pid), '/F'],
                       stdout=open(os.devnull,'w'), stderr=open(os.devnull,'w'))
    print(f'[KILL] Stopped: {pids}')
    time.sleep(1)

    # Launch desktopcal (it will auto-restart dkdockhost)
    print('[START] Launching desktopcal...')
    subprocess.Popen(
        [r'C:\Users\Administrator\AppData\Roaming\CalendarTask\desktopcal.exe'],
        stdout=open(os.devnull,'w'), stderr=open(os.devnull,'w')
    )
    time.sleep(3)

    # Verify
    r2 = subprocess.run(
        ['powershell', '-NoProfile', '-Command',
         "Get-CimInstance Win32_Process -Filter \"name='desktopcal.exe' -or name='dkdockhost.exe'\" | ConvertTo-Json -Compress"],
        capture_output=True
    )
    text2 = r2.stdout.decode('utf-8', errors='replace').strip()
    if text2:
        running = json.loads(text2)
        if isinstance(running, dict):
            running = [running]
        print(f'[OK] Running: {[(p["Id"],p["ProcessName"]) for p in running]}')
    print('[OK] All done! Check the desktop widget.')

except Exception as e:
    print(f'[ERROR] {e}')
    print('[HINT] Please restart DesktopCal manually')
