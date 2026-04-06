"""
delete_subagent_sessions.py
直接操作 sessions.json + 重命名 .jsonl 文件来删除 session
"""

import json, re, os
from datetime import datetime, timezone

OPENCLAW_ROOT = r'E:\openclaw\.openclaw\agents'
AGE_HOURS = 2

def get_agent_session_from_key(key):
    parts = key.split(':')
    if len(parts) >= 4 and parts[2] == 'subagent':
        agent_id = parts[1]
        session_id = parts[3]
        if len(parts) > 4 and parts[4] == 'run':
            session_id = session_id + ':run:' + parts[5]
        return agent_id, session_id
    return None, None

def load_registry(agent_id):
    path = os.path.join(OPENCLAW_ROOT, agent_id, 'sessions', 'sessions.json')
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_registry(agent_id, data):
    path = os.path.join(OPENCLAW_ROOT, agent_id, 'sessions', 'sessions.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def rename_jsonl_to_deleted(agent_id, session_id):
    sessions_dir = os.path.join(OPENCLAW_ROOT, agent_id, 'sessions')
    possible_ids = [session_id]
    if ':' in session_id:
        possible_ids.append(session_id.split(':')[0])

    jsonl_path = None
    actual_sid = None
    for sid in possible_ids:
        p = os.path.join(sessions_dir, sid + '.jsonl')
        if os.path.exists(p):
            jsonl_path = p
            actual_sid = sid
            break

    if jsonl_path is None:
        return False, 'file_not_found'

    ts = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H-%M-%S.%f')[:-3] + 'Z'
    new_name = actual_sid + '.jsonl.deleted.' + ts
    new_path = os.path.join(sessions_dir, new_name)
    os.rename(jsonl_path, new_path)
    return True, new_name

def main():
    import subprocess

    result = subprocess.run(
        [r'D:\work\software\nvm4w\nodejs\openclaw.cmd', 'sessions', '--all-agents', '--json'],
        capture_output=True, text=True
    )
    data = json.loads(result.stdout)
    sessions = data['sessions']

    to_delete = []
    for s in sessions:
        key = s['key']
        if not re.search(r':subagent:', key):
            continue
        if s.get('ageMs', 0) <= AGE_HOURS * 3600 * 1000:
            continue
        to_delete.append((key, s))

    print('准备删除 %d 个 session...\n' % len(to_delete))

    ok_count = 0
    error_count = 0

    for key, s in to_delete:
        agent_id, session_id = get_agent_session_from_key(key)

        if not agent_id or not session_id:
            print('[SKIP] 解析失败: ' + key)
            error_count += 1
            continue

        registry = load_registry(agent_id)
        in_registry = key in registry
        if in_registry:
            del registry[key]
            save_registry(agent_id, registry)

        file_ok, file_info = rename_jsonl_to_deleted(agent_id, session_id)

        reg_str = '有' if in_registry else '无'
        if file_ok or in_registry:
            print('[OK] ' + agent_id + ' | ' + session_id[:30] + '... | registry=' + reg_str + ' | file->' + file_info)
            ok_count += 1
        else:
            print('[WARN] ' + agent_id + '/' + session_id + ' | registry=无 | file=不存在')
            ok_count += 1

    print('\n完成: 成功处理 %d 个，失败 %d 个' % (ok_count, error_count))

if __name__ == '__main__':
    main()
