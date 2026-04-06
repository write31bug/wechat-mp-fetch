import sqlite3
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
    """任务交接/卡住：必须调用此方法才能交接给下一个人"""
    conn = sqlite3.connect(DB_PATH)
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    conn.execute('''
        UPDATE tasks SET assignee = ?, status = 'BLOCKED', next_step = ?, updated_at = ?
        WHERE task_id = ?
    ''', (assignee, next_step, now, task_id))
    conn.commit()
    conn.close()

def complete_task(task_id, assignee, result):
    """
    任务完成：【强制前置检查】
    必须先调用 block_task 写入 next_step，才能调用 complete_task
    否则抛出异常
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute('SELECT next_step FROM tasks WHERE task_id = ?', (task_id,))
    row = cur.fetchone()
    if row is None:
        conn.close()
        raise ValueError(f"任务 {task_id} 不存在")
    if row[0] is None or row[0] == '':
        conn.close()
        raise ValueError(
            f"任务 {task_id} 未填写 next_step！"
            "必须先调用 block_task(task_id, assignee, '交接信息') 写入下一步，才能调用 complete_task"
        )
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    conn.execute('''
        UPDATE tasks SET assignee = ?, status = 'DONE', result = ?, updated_at = ?
        WHERE task_id = ?
    ''', (assignee, result, now, task_id))
    conn.commit()
    conn.close()

def dispatch_handoff(task_id, from_role, to_role, task_body):
    """
    【派活话术模板】
    小金派活时必须填写以下字段，格式化为交接标准：
    
    参数：
    - task_id: 任务ID
    - from_role: 小金（派活人）
    - to_role: 接手小弟
    - task_body: dict，包含：
        - goal: 目标（做什么）
        - audience: 受众是谁
        - constraints: 禁止事项（不能做什么）
        - deliverable: 交付标准（产出什么样）
        - next_handoff: 完成后交给谁
    
    返回标准话术字符串，用于发给小弟。
    """
    body = task_body
    msg = f"""【任务 {task_id} 派活】

目标：{body.get('goal', '请自行确认')}
受众：{body.get('audience', '通用受众')}
禁止：{body.get('constraints', '无')}
交付标准：{body.get('deliverable', '请自行确认')}
完成后交给：{body.get('next_handoff', '小金')}

完成后必须：调用 block_task 写入 next_step，再调用 complete_task，才算闭环。"""
    return msg

def get_task(task_id):
    """读取单个任务"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute('SELECT * FROM tasks WHERE task_id = ?', (task_id,))
    row = cur.fetchone()
    cols = ['task_id','name','assigner','assignee','status','context','next_step','result','created_at','updated_at']
    conn.close()
    return dict(zip(cols, row)) if row else None

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
    tasks = get_all_tasks()
    for t in tasks:
        print(f"{t['task_id']} | {t['name']} | {t['assignee']} | {t['status']}")
