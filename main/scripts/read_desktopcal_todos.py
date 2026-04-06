"""
读取 DesktopCal 今日待办 - 详细版
"""
import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = r'C:\Users\Administrator\AppData\Roaming\CalendarTask\Db\calendar.db'
import datetime
today = datetime.date.today().strftime('%Y-%m-%d')

conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("""
    SELECT it_id, it_content, it_history, it_cdate, it_mdate, it_unique_id
    FROM item_table
    WHERE it_cdate LIKE ? OR it_mdate LIKE ?
    ORDER BY it_id DESC
""", (f'{today}%', f'{today}%'))

rows = cur.fetchall()
conn.close()

print(f'今日待办共 {len(rows)} 条:\n')
for r in rows:
    print(f'ID: {r[0]}')
    print(f'内容: {repr(r[1])}')
    print(f'  -> 显示: {r[1]}')
    print(f'历史: {r[2]}')
    print(f'创建: {r[3]}')
    print(f'修改: {r[4]}')
    print(f'UID: {r[5]}')
    print()
