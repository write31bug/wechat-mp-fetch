import sqlite3
import json
from datetime import datetime

DB_PATH = r'E:\openclaw\tasks\board.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY,
            name TEXT,
            assigner TEXT,
            assignee TEXT,
            status TEXT,
            context TEXT,
            next_step TEXT,
            result TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def create_task(task_id, name, assigner, context):
    """由小金调用，创建新任务"""
    conn = sqlite3.connect(DB_PATH)
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    conn.execute('''
        INSERT OR IGNORE INTO tasks (task_id, name, assigner, assignee, status, context, created_at, updated_at)
        VALUES (?, ?, ?, ?, 'PENDING', ?, ?, ?)
    ''', (task_id, name, assigner, context, context, now, now))
    conn.commit()
    conn.close()

def claim_task(task_id, assignee):
    """执行者认领任务"""
    conn = sqlite3.connect(DB_PATH)
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    conn.execute('''
        UPDATE tasks SET assignee = ?, status = 'IN_PROGRESS', updated_at = ?
        WHERE task_id = ?
    ''', (assignee, now, task_id))
    conn.commit()
    conn.close()

def block_task(task_id, assignee, next_step):
    """任务交接/卡住"""
    conn = sqlite3.connect(DB_PATH)
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    conn.execute('''
        UPDATE tasks SET assignee = ?, status = 'BLOCKED', next_step = ?, updated_at = ?
        WHERE task_id = ?
    ''', (assignee, next_step, now, task_id))
    conn.commit()
    conn.close()

def complete_task(task_id, assignee, result):
    """任务完成"""
    conn = sqlite3.connect(DB_PATH)
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    conn.execute('''
        UPDATE tasks SET assignee = ?, status = 'DONE', result = ?, updated_at = ?
        WHERE task_id = ?
    ''', (assignee, result, now, task_id))
    conn.commit()
    conn.close()

def get_task(task_id):
    """读取单个任务"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute('SELECT * FROM tasks WHERE task_id = ?', (task_id,))
    row = cur.fetchone()
    conn.close()
    return row

def get_all_tasks():
    """读取所有任务"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute('SELECT * FROM tasks ORDER BY created_at DESC')
    rows = cur.fetchall()
    conn.close()
    cols = ['task_id','name','assigner','assignee','status','context','next_step','result','created_at','updated_at']
    return [dict(zip(cols, r)) for r in rows]

def get_tasks_by_status(status):
    """按状态查询"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute('SELECT * FROM tasks WHERE status = ? ORDER BY created_at DESC', (status,))
    rows = cur.fetchall()
    conn.close()
    cols = ['task_id','name','assigner','assignee','status','context','next_step','result','created_at','updated_at']
    return [dict(zip(cols, r)) for r in rows]

if __name__ == '__main__':
    init_db()
    print('数据库初始化完成')
    print(get_all_tasks())
