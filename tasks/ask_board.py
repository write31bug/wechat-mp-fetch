import sqlite3
import uuid
from datetime import datetime

DB_PATH = r'E:\openclaw\tasks\board.db'

def _conn():
    """所有数据库连接的统一入口：WAL + busy_timeout"""
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA busy_timeout=10000')
    return conn

def _migrate_add_summary_path(conn):
    """安全地给 discussions 表加 summary_path 列（幂等迁移）"""
    cur = conn.execute("PRAGMA table_info(discussions)")
    columns = [row[1] for row in cur.fetchall()]
    if 'summary_path' not in columns:
        conn.execute('ALTER TABLE discussions ADD COLUMN summary_path TEXT')
        print('[migrate] discussions.summary_path 列已添加')


def init_db():
    """初始化所有表（tasks + discussions/contributions/discussion_log）"""
    conn = _conn()
    # 任务看板表（原有）
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
    # 讨论任务表
    conn.execute('''
        CREATE TABLE IF NOT EXISTS discussions (
            id              TEXT PRIMARY KEY,
            topic           TEXT NOT NULL,
            background      TEXT,
            goal            TEXT,
            agents          TEXT,
            status          TEXT DEFAULT 'PENDING',
            base_path       TEXT,
            created         TEXT,
            updated         TEXT
        )
    ''')
    # 各方观点状态表
    conn.execute('''
        CREATE TABLE IF NOT EXISTS contributions (
            id              TEXT PRIMARY KEY,
            discussion_id   TEXT NOT NULL,
            agent           TEXT NOT NULL,
            file_path       TEXT,
            status          TEXT DEFAULT 'PENDING',
            confidence      TEXT,
            error_message   TEXT,
            created         TEXT,
            updated         TEXT,
            completed_at    TEXT
        )
    ''')
    # 操作审计日志表（默认关闭，按需写入）
    conn.execute('''
        CREATE TABLE IF NOT EXISTS discussion_log (
            id              TEXT PRIMARY KEY,
            discussion_id   TEXT NOT NULL,
            agent           TEXT,
            action          TEXT,
            detail          TEXT,
            timestamp       TEXT
        )
    ''')
    # 索引（外键关联查询加速）
    conn.execute('CREATE INDEX IF NOT EXISTS idx_contributions_discussion ON contributions(discussion_id)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_discussion_log_discussion ON discussion_log(discussion_id)')

    # 迁移：discussions 表加 summary_path 字段（已存在的数据库平滑升级）
    _migrate_add_summary_path(conn)

    conn.commit()
    conn.close()
    print('[init_db] 所有表初始化完成（WAL 模式已开启）')

# ============ 任务看板（原有函数，保持不变） ============

def create_task(task_id, name, assigner, context):
    conn = _conn()
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    conn.execute('''
        INSERT OR IGNORE INTO tasks (task_id, name, assigner, assignee, status, context, created_at, updated_at)
        VALUES (?, ?, ?, ?, 'PENDING', ?, ?, ?)
    ''', (task_id, name, assigner, context, context, now, now))
    conn.commit()
    conn.close()

def claim_task(task_id, assignee):
    conn = _conn()
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    conn.execute('''
        UPDATE tasks SET assignee = ?, status = 'IN_PROGRESS', updated_at = ?
        WHERE task_id = ?
    ''', (assignee, now, task_id))
    conn.commit()
    conn.close()

def block_task(task_id, assignee, next_step):
    conn = _conn()
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    conn.execute('''
        UPDATE tasks SET assignee = ?, status = 'BLOCKED', next_step = ?, updated_at = ?
        WHERE task_id = ?
    ''', (assignee, next_step, now, task_id))
    conn.commit()
    conn.close()

def complete_task(task_id, assignee, result):
    conn = _conn()
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

def get_task(task_id):
    conn = _conn()
    cur = conn.execute('SELECT * FROM tasks WHERE task_id = ?', (task_id,))
    row = cur.fetchone()
    cols = ['task_id','name','assigner','assignee','status','context','next_step','result','created_at','updated_at']
    conn.close()
    return dict(zip(cols, row)) if row else None

def get_all_tasks():
    conn = _conn()
    cur = conn.execute('SELECT * FROM tasks ORDER BY created_at DESC')
    rows = cur.fetchall()
    conn.close()
    cols = ['task_id','name','assigner','assignee','status','context','next_step','result','created_at','updated_at']
    return [dict(zip(cols, r)) for r in rows]

def get_tasks_by_status(status):
    conn = _conn()
    cur = conn.execute('SELECT * FROM tasks WHERE status = ? ORDER BY created_at DESC', (status,))
    rows = cur.fetchall()
    conn.close()
    cols = ['task_id','name','assigner','assignee','status','context','next_step','result','created_at','updated_at']
    return [dict(zip(cols, r)) for r in rows]

def dispatch_handoff(task_id, from_role, to_role, task_body):
    body = task_body
    msg = f"""【任务 {task_id} 派活】

目标：{body.get('goal', '请自行确认')}
受众：{body.get('audience', '通用受众')}
禁止：{body.get('constraints', '无')}
交付标准：{body.get('deliverable', '请自行确认')}
完成后交给：{body.get('next_handoff', '小金')}

完成后必须：调用 block_task 写入 next_step，再调用 complete_task，才算闭环。"""
    return msg

# ============ 异步讨论（新增函数） ============

def create_discussion(topic, agents, background='', goal='', base_path=''):
    """创建讨论任务（原子事务）"""
    discussion_id = datetime.now().strftime('%Y%m%d%H%M%S') + '_' + topic.replace(' ', '_')[:20]
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    import json
    conn = _conn()
    try:
        conn.execute('''
            INSERT INTO discussions (id, topic, background, goal, agents, status, base_path, created, updated)
            VALUES (?, ?, ?, ?, ?, 'IN_PROGRESS', ?, ?, ?)
        ''', (discussion_id, topic, background, goal, json.dumps(agents), base_path, now, now))
        for agent in agents:
            conn.execute('''
                INSERT INTO contributions (id, discussion_id, agent, status, created, updated)
                VALUES (?, ?, ?, 'PENDING', ?, ?)
            ''', (str(uuid.uuid4()), discussion_id, agent, now, now))
        conn.commit()
    finally:
        conn.close()
    return discussion_id

def get_discussion(discussion_id):
    """读取讨论任务"""
    conn = _conn()
    cur = conn.execute('SELECT * FROM discussions WHERE id = ?', (discussion_id,))
    row = cur.fetchone()
    cols = ['id','topic','background','goal','agents','status','base_path','created','updated','summary_path']
    # 兼容旧数据：字段不足时补空值
    if row and len(row) < len(cols):
        row = row + ('',) * (len(cols) - len(row))
    conn.close()
    return dict(zip(cols, row)) if row else None

def get_contributions(discussion_id):
    """读取某讨论的所有 contributions"""
    conn = _conn()
    cur = conn.execute('''
        SELECT id, agent, status, confidence, file_path, error_message, completed_at
        FROM contributions WHERE discussion_id = ?
    ''', (discussion_id,))
    rows = cur.fetchall()
    conn.close()
    cols = ['id','agent','status','confidence','file_path','error_message','completed_at']
    return [dict(zip(cols, r)) for r in rows]

def update_contribution(discussion_id, agent, status, file_path='', confidence='', error_message=''):
    """更新某 agent 的 contribution（原子）
    
    status 取值规则（v3 两轮制）：
    - ROUND1_DONE：第一轮完成，等待其他 agent
    - ROUND2_DONE：第二轮完成（最终完成）
    - DONE/FAILED：保留，向后兼容
    
    触发 discussions 自动 DONE 的条件：所有 agent 都不是 PENDING
    （即 ROUND1_DONE / ROUND2_DONE / DONE / FAILED 都算完成）
    """
    VALID_STATUSES = ('PENDING', 'ROUND1_DONE', 'ROUND2_DONE', 'DONE', 'FAILED')
    if status not in VALID_STATUSES:
        raise ValueError(f'status 必须是 {VALID_STATUSES} 之一，当前：{status}')
    
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = _conn()
    completed_at = now if status in ('DONE', 'ROUND2_DONE', 'FAILED') else ''
    conn.execute('''
        UPDATE contributions
        SET status=?, file_path=?, confidence=?, error_message=?, updated=?, completed_at=?
        WHERE discussion_id=? AND agent=?
    ''', (status, file_path, confidence, error_message, now, completed_at, discussion_id, agent))
    # 检查是否所有 agent 都完成（非 PENDING 状态）
    cur = conn.execute('''
        SELECT COUNT(*) FROM contributions
        WHERE discussion_id=? AND status='PENDING'
    ''', (discussion_id,))
    remaining = cur.fetchone()[0]
    # 只有当所有 agent 都不再是 PENDING 时才自动 DONE
    if remaining == 0:
        final_done = conn.execute('''
            SELECT COUNT(*) FROM contributions
            WHERE discussion_id=? AND status IN ('DONE','ROUND2_DONE')
        ''', (discussion_id,)).fetchone()[0]
        if final_done > 0:
            conn.execute('UPDATE discussions SET status=?, updated=? WHERE id=?', ('DONE', now, discussion_id))
    conn.commit()
    conn.close()

def log_discussion_action(discussion_id, agent, action, detail=''):
    """写审计日志（默认关闭，可按需调用）"""
    conn = _conn()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn.execute('''
        INSERT INTO discussion_log (id, discussion_id, agent, action, detail, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (str(uuid.uuid4()), discussion_id, agent, action, detail, now))
    conn.commit()
    conn.close()

# ============ 讨论总结写入（multi-discussion v4 新增） ============

def write_discussion_summary(discussion_id: str, summary_path: str):
    """
    将总结报告路径写入 discussions 表，同时更新状态为 COMPLETED。
    在 orchestrator 生成总结后调用。
    """
    conn = _conn()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn.execute('''
        UPDATE discussions
        SET summary_path = ?, status = 'COMPLETED', updated = ?
        WHERE id = ?
    ''', (summary_path, now, discussion_id))
    conn.commit()
    conn.close()


def get_discussion_detail(discussion_id: str) -> dict:
    """
    获取讨论详情（包括 summary_path）。
    用于查看已完成讨论的总结文件路径。
    """
    conn = _conn()
    cur = conn.execute('SELECT * FROM discussions WHERE id = ?', (discussion_id,))
    row = cur.fetchone()
    cols = ['id','topic','background','goal','agents','status',
            'base_path','created','updated','summary_path']
    if row and len(row) < len(cols):
        row = row + ('',) * (len(cols) - len(row))
    conn.close()
    return dict(zip(cols, row)) if row else None


def list_discussions(status: str = None) -> list:
    """
    列出所有讨论，可按 status 过滤。
    用法：
        list_discussions()                   # 所有讨论
        list_discussions(status='COMPLETED')  # 只看已完成的
        list_discussions(status='IN_PROGRESS')  # 进行中的
    """
    conn = _conn()
    if status:
        cur = conn.execute(
            'SELECT * FROM discussions WHERE status = ? ORDER BY created DESC',
            (status,)
        )
    else:
        cur = conn.execute('SELECT * FROM discussions ORDER BY created DESC')
    rows = cur.fetchall()
    cols = ['id','topic','background','goal','agents','status',
            'base_path','created','updated','summary_path']
    rows = [
        (r + ('',) * (len(cols) - len(r))) if len(r) < len(cols) else r
        for r in rows
    ]
    conn.close()
    return [dict(zip(cols, r)) for r in rows]

if __name__ == '__main__':
    init_db()
    print('[ask_board] 演示：创建讨论')
    did = create_discussion('测试讨论', ['dev', 'writer'], goal='测试', base_path='E:\\openclaw\\tasks\\discussion\\test')
    print(f'讨论ID: {did}')
    print(get_discussion(did))
    print(get_contributions(did))
    update_contribution(did, 'dev', 'DONE', confidence='high')
    print(get_contributions(did))
