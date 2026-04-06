"""
DesktopCal 日历清单管理
用法:
  python desktopcal_todo.py add <任务内容>          # 添加任务
  python desktopcal_todo.py list                    # 查看今日任务
  python desktopcal_todo.py done <行号>            # 标记完成（行号从1开始）
  python desktopcal_todo.py del <行号>             # 删除任务
  python desktopcal_todo.py modify <行号> <新内容>  # 修改任务
"""
import sqlite3, sys, datetime, json, time, subprocess, os

DB = r'C:\Users\Administrator\AppData\Roaming\CalendarTask\Db\calendar.db'
DESKTOPCAL_EXE = r'C:\Users\Administrator\AppData\Roaming\CalendarTask\desktopcal.exe'


def commit_and_close(conn):
    """确保改动真正落盘，然后关闭连接"""
    conn.commit()
    try:
        conn.execute('PRAGMA wal_checkpoint(FULL)')
    except:
        pass
    conn.close()


def get_daily_uid():
    today = datetime.date.today().strftime('%Y%m%d')
    return f'dkcal_mdays_{today}'


def get_daily_entry(conn):
    """获取今日条目，不存在则自动创建"""
    uid = get_daily_uid()
    cur = conn.cursor()
    cur.execute("SELECT it_id, it_content, it_history FROM item_table WHERE it_unique_id=?", (uid,))
    row = cur.fetchone()
    if row:
        return row
    # 不存在则创建
    now = datetime.datetime.now()
    cur.execute("""
        INSERT INTO item_table (u_id, pj_id, u_mid, it_unique_id, it_bgcolor, it_content, it_history, it_appinfo, it_cdate, it_mdate, it_stime, it_mtime, group_id)
        VALUES (0, 0, '', ?, '', '', '[]', '', ?, ?, 0, 1, '')
    """, (uid, now.strftime('%Y-%m-%d %H:%M:%S'), now.strftime('%Y-%m-%d %H:%M:%S')))
    commit_and_close(conn)
    # 重新读取
    cur.execute("SELECT it_id, it_content, it_history FROM item_table WHERE it_unique_id=?", (uid,))
    return cur.fetchone()


def parse_tasks(content):
    """把每日条目内容解析成任务列表"""
    if not content:
        return []
    lines = content.split('\r\n')
    tasks = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        done = line.startswith('[+]')
        text = line[4:].strip() if done else line
        tasks.append({'text': text, 'done': done, 'raw': line})
    return tasks


def build_content(tasks):
    """把任务列表合并回 it_content 字符串"""
    lines = []
    for t in tasks:
        prefix = '[+] ' if t['done'] else ''
        lines.append(prefix + t['text'])
    return '\r\n'.join(lines)


def restart_desktopcal():
    """强制停止 desktopcal + dkdockhost 全部进程，等待干净退出后重新启动"""
    try:
        # 强制停止所有相关进程
        subprocess.run(
            ['powershell', '-NoProfile', '-Command',
             "Get-Process desktopcal,dkdockhost -ErrorAction SilentlyContinue | Stop-Process -Force"],
            stdout=open(os.devnull,'w'), stderr=open(os.devnull,'w')
        )
        # 等待进程彻底退出
        time.sleep(2)

        # 启动 desktopcal
        subprocess.Popen([DESKTOPCAL_EXE],
                        stdout=open(os.devnull,'w'), stderr=open(os.devnull,'w'))
        time.sleep(3)
        return True
    except Exception as e:
        return False


def cmd_list():
    conn = sqlite3.connect(DB)
    row = get_daily_entry(conn)
    conn.close()
    tasks = parse_tasks(row[1]) if row else []
    if not tasks:
        print('[Empty] 今日清单为空')
        return
    print(f'今日清单 ({len(tasks)} 项):\n')
    for i, t in enumerate(tasks, 1):
        status = '[x]' if t['done'] else '[ ]'
        print(f'  {i}. {status} {t["text"]}')
    print()


def cmd_add(content):
    conn = sqlite3.connect(DB)
    row = get_daily_entry(conn)
    # get_daily_entry may have closed conn on INSERT, re-connect if needed
    try:
        conn.execute("SELECT 1")
    except:
        conn = sqlite3.connect(DB)
        row = get_daily_entry(conn)
    tasks = parse_tasks(row[1])
    
    # 避免重复
    for t in tasks:
        if t['text'] == content:
            print(f'[INFO] 任务已存在: {content}')
            conn.close()
            return

    tasks.append({'text': content, 'done': False, 'raw': content})
    new_content = build_content(tasks)
    
    # 更新历史
    history = []
    if row[2]:
        try:
            history = json.loads(row[2])
        except:
            pass
    now = datetime.datetime.now()
    history.append({'content': new_content, 'time': int(now.timestamp())})
    
    cur = conn.cursor()
    cur.execute("""
        UPDATE item_table SET it_content=?, it_history=?, it_mdate=? WHERE it_id=?
    """, (new_content, json.dumps(history, ensure_ascii=False), now.strftime('%Y-%m-%d %H:%M:%S'), row[0]))
    commit_and_close(conn)
    
    print(f'[ADD] "{content}"')
    if restart_desktopcal():
        print('[OK] DesktopCal 已刷新')
    else:
        print('[WARN] 请手动重启 DesktopCal')


def cmd_done(index):
    conn = sqlite3.connect(DB)
    row = get_daily_entry(conn)
    tasks = parse_tasks(row[1])
    conn.close()
    
    if index < 1 or index > len(tasks):
        print(f'[ERROR] 无效行号 {index}，范围 1-{len(tasks)}')
        return
    
    t = tasks[index - 1]
    if t['done']:
        print(f'[INFO] 已是完成状态: {t["text"]}')
        return
    
    t['done'] = True
    t['text'] = t['text']  # 保留原内容
    new_content = build_content(tasks)
    
    history = []
    if row[2]:
        try:
            history = json.loads(row[2])
        except:
            pass
    now = datetime.datetime.now()
    history.append({'content': new_content, 'time': int(now.timestamp())})
    
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        UPDATE item_table SET it_content=?, it_history=?, it_mdate=? WHERE it_id=?
    """, (new_content, json.dumps(history, ensure_ascii=False), now.strftime('%Y-%m-%d %H:%M:%S'), row[0]))
    commit_and_close(conn)
    
    print(f'[DONE] {t["text"]}')
    if restart_desktopcal():
        print('[OK] DesktopCal 已刷新')
    else:
        print('[WARN] 请手动重启 DesktopCal')


def cmd_del(index):
    conn = sqlite3.connect(DB)
    row = get_daily_entry(conn)
    tasks = parse_tasks(row[1])
    
    if index < 1 or index > len(tasks):
        print(f'[ERROR] 无效行号 {index}，范围 1-{len(tasks)}')
        conn.close()
        return
    
    removed = tasks.pop(index - 1)
    new_content = build_content(tasks)
    
    history = []
    if row[2]:
        try:
            history = json.loads(row[2])
        except:
            pass
    now = datetime.datetime.now()
    history.append({'content': new_content, 'time': int(now.timestamp())})
    
    cur = conn.cursor()
    cur.execute("""
        UPDATE item_table SET it_content=?, it_history=?, it_mdate=? WHERE it_id=?
    """, (new_content, json.dumps(history, ensure_ascii=False), now.strftime('%Y-%m-%d %H:%M:%S'), row[0]))
    commit_and_close(conn)
    
    print(f'[DEL] "{removed["text"]}"')
    if restart_desktopcal():
        print('[OK] DesktopCal 已刷新')
    else:
        print('[WARN] 请手动重启 DesktopCal')


def cmd_modify(index, new_text):
    conn = sqlite3.connect(DB)
    row = get_daily_entry(conn)
    tasks = parse_tasks(row[1])
    
    if index < 1 or index > len(tasks):
        print(f'[ERROR] 无效行号 {index}，范围 1-{len(tasks)}')
        conn.close()
        return
    
    old_text = tasks[index - 1]['text']
    tasks[index - 1]['text'] = new_text
    new_content = build_content(tasks)
    
    history = []
    if row[2]:
        try:
            history = json.loads(row[2])
        except:
            pass
    now = datetime.datetime.now()
    history.append({'content': new_content, 'time': int(now.timestamp())})
    
    cur = conn.cursor()
    cur.execute("""
        UPDATE item_table SET it_content=?, it_history=?, it_mdate=? WHERE it_id=?
    """, (new_content, json.dumps(history, ensure_ascii=False), now.strftime('%Y-%m-%d %H:%M:%S'), row[0]))
    commit_and_close(conn)
    
    print(f'[MOD] "{old_text}" -> "{new_text}"')
    if restart_desktopcal():
        print('[OK] DesktopCal 已刷新')
    else:
        print('[WARN] 请手动重启 DesktopCal')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'list':
        cmd_list()
    elif cmd == 'add' and len(sys.argv) >= 3:
        cmd_add(' '.join(sys.argv[2:]))
    elif cmd == 'done' and len(sys.argv) >= 3:
        cmd_done(int(sys.argv[2]))
    elif cmd == 'del' and len(sys.argv) >= 3:
        cmd_del(int(sys.argv[2]))
    elif cmd == 'modify' and len(sys.argv) >= 4:
        cmd_modify(int(sys.argv[2]), ' '.join(sys.argv[3:]))
    else:
        print(__doc__)
