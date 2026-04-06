"""
向 DesktopCal 每日条目追加内容（正确方式）
DesktopCal widget 只读 dkcal_mdays_YYYYMMDD 格式的条目
"""
import sqlite3, sys, datetime, json
sys.stdout.reconfigure(encoding='utf-8')

db = r'C:\Users\Administrator\AppData\Roaming\CalendarTask\Db\calendar.db'
today = datetime.date.today().strftime('%Y%m%d')  # 20260404
daily_uid = f'dkcal_mdays_{today}'

conn = sqlite3.connect(db)
cur = conn.cursor()

# 读取现有每日条目
cur.execute("SELECT it_id, it_content, it_history FROM item_table WHERE it_unique_id=?", (daily_uid,))
row = cur.fetchone()

if row:
    existing_content = row[1] or ''
    print(f'现有内容: {repr(existing_content)}')
    
    # 解析历史
    history = []
    if row[2]:
        try:
            history = json.loads(row[2])
        except:
            history = []
    
    # 追加新任务（追加到现有内容）
    new_task = 'openclaw写入'
    if new_task not in existing_content:
        new_content = existing_content + ('\r\n' if existing_content else '') + new_task
    else:
        print('任务已存在，无需重复添加')
        new_content = existing_content

    print(f'新内容: {repr(new_content)}')
    
    # 更新历史
    now = datetime.datetime.now()
    history.append({'content': new_content, 'time': int(now.timestamp())})
    
    # 更新数据库
    cur.execute("""
        UPDATE item_table 
        SET it_content=?, it_history=?, it_mdate=?
        WHERE it_unique_id=?
    """, (new_content, json.dumps(history, ensure_ascii=False), now.strftime('%Y-%m-%d %H:%M:%S'), daily_uid))
    
    conn.commit()
    print(f'\n✅ 追加成功！')
    print(f'每日条目 UID: {daily_uid}')
    print(f'最终内容: {new_content}')
else:
    print(f'未找到每日条目 UID={daily_uid}，需要先创建')

conn.close()
