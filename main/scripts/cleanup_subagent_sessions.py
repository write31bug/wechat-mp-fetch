"""
清理超过 N 小时的 subagent session
直读 sessions.json，修正了数据结构匹配

用法:
  python cleanup_subagent_sessions.py          # 扫描（不删除）
  python cleanup_subagent_sessions.py --delete # 真正删除
  python cleanup_subagent_sessions.py --dry    # 同 --delete（默认）
"""

import json
import os
import glob
import sys
import time as time_module
from datetime import datetime, timezone, timedelta

# ==================== 配置 ====================
AGE_HOURS = 2            # 超过多少小时算过期
DRY_RUN = "--delete" not in sys.argv  # 默认扫描，加 --delete 才真正删
# ==================== 配置 ====================

NOW_MS = int(datetime.now(timezone.utc).timestamp() * 1000)
AGE_MS = AGE_HOURS * 60 * 60 * 1000

OPENCLAW_STATE = r'E:\openclaw\.openclaw'
AGENTS_DIR = os.path.join(OPENCLAW_STATE, 'agents')

LOG_PATH = os.path.join(os.path.dirname(__file__), 'cleanup_subagent.log')


def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def get_all_sessions():
    """遍历所有 agent 的 sessions.json，提取顶层的 sessionKey -> metadata"""
    all_sessions = []
    if not os.path.exists(AGENTS_DIR):
        return all_sessions
    for agent_id in os.listdir(AGENTS_DIR):
        sessions_file = os.path.join(AGENTS_DIR, agent_id, 'sessions', 'sessions.json')
        if not os.path.exists(sessions_file):
            continue
        try:
            with open(sessions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # data 是 dict: {sessionKey: metadata}
            for session_key, meta in data.items():
                if not isinstance(meta, dict):
                    continue
                meta_copy = dict(meta)
                meta_copy['key'] = session_key
                meta_copy['_agentDir'] = agent_id
                meta_copy['_sessionsFile'] = sessions_file
                all_sessions.append(meta_copy)
        except (json.JSONDecodeError, IOError) as e:
            log(f"  [WARN] 读取 {sessions_file} 失败: {e}")
    return all_sessions


def is_subagent_session(key):
    """判断是否为 subagent session"""
    if not key:
        return False
    # sessions_spawn 产生的 session key 包含 :subagent:
    return ':subagent:' in key


def format_age_ms(ms):
    total_sec = ms // 1000
    h = total_sec // 3600
    m = (total_sec % 3600) // 60
    if h > 0:
        return f"{h}h {m}m"
    elif m > 0:
        return f"{m}m"
    else:
        return f"{total_sec}s"


def delete_session_from_index(session):
    """从 sessions.json 中删除 session 条目"""
    sessions_file = session['_sessionsFile']
    session_key = session['key']

    with open(sessions_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if session_key not in data:
        log(f"  [WARN] {session_key} 已不在 sessions.json 中")
        return False

    session_id = data[session_key].get('sessionId', '')
    del data[session_key]

    # 清理 activeKey
    if data.get('activeKey') == session_key:
        data['activeKey'] = None

    with open(sessions_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    log(f"  从 sessions.json 移除: {session_key}")
    return True, session_id


def delete_transcript_files(agent_id, session_id):
    """删除 transcript .jsonl 文件"""
    if not session_id:
        return
    sessions_dir = os.path.join(AGENTS_DIR, agent_id, 'sessions')
    transcript_dir = os.path.join(sessions_dir, 'transcripts')

    # 直接删 sessionId.jsonl
    direct = os.path.join(sessions_dir, f"{session_id}.jsonl")
    if os.path.exists(direct):
        size = os.path.getsize(direct)
        os.remove(direct)
        log(f"  删除了 transcript: {direct} ({size} bytes)")

    # 删 transcripts/ 下的
    if os.path.exists(transcript_dir):
        for fn in os.listdir(transcript_dir):
            if fn == f"{session_id}.jsonl" or fn.startswith(f"{session_id}-"):
                try:
                    os.remove(os.path.join(transcript_dir, fn))
                    log(f"  删除了: {fn}")
                except OSError as e:
                    log(f"  [WARN] 删除失败 {fn}: {e}")


def main():
    mode = "删除模式" if not DRY_RUN else "扫描模式"
    log(f"\n{'='*60}")
    log(f"Subagent Session 清理 - {mode}")
    log(f"{'='*60}")
    log(f"阈值：{AGE_HOURS} 小时")
    log(f"当前：{datetime.fromtimestamp(NOW_MS/1000, tz=timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S')}")

    all_sessions = get_all_sessions()
    log(f"扫描范围：{len(all_sessions)} 个 session（所有 agent）")

    expired = []
    for s in all_sessions:
        key = s.get('key', '')
        if not is_subagent_session(key):
            continue

        # 计算 age
        updated_at = s.get('updatedAt', 0)
        age_ms = NOW_MS - updated_at if updated_at else 0
        if age_ms < AGE_MS:
            continue

        expired.append({
            'key': key,
            'agentId': s.get('agentId', 'unknown'),
            '_agentDir': s.get('_agentDir', 'unknown'),
            '_sessionsFile': s.get('_sessionsFile', ''),
            'sessionId': s.get('sessionId', ''),
            'ageMs': age_ms,
            'ageStr': format_age_ms(age_ms),
        })

    expired.sort(key=lambda x: x['ageMs'], reverse=True)

    if not expired:
        log(f"\n没有需要清理的 subagent session。")
        return

    log(f"\n找到 {len(expired)} 个过期 subagent session：\n")

    from collections import defaultdict
    by_agent = defaultdict(list)
    for s in expired:
        by_agent[s['agentId']].append(s)

    for agent_id, items in by_agent.items():
        log(f"【{agent_id}】{len(items)} 个：")
        for s in items:
            log(f"  - {s['key']}")
            log(f"    age={s['ageStr']}, sessionId={s['sessionId']}")

    log(f"\n{'='*60}")

    if DRY_RUN:
        log(f"[扫描完成] 共 {len(expired)} 个未删除（dry-run）")
        return

    # 真正删除
    deleted = 0
    failed = 0
    for s in expired:
        try:
            result = delete_session_from_index(s)
            if result:
                _, session_id = result
                delete_transcript_files(s['_agentDir'], session_id)
                deleted += 1
            else:
                failed += 1
        except Exception as e:
            failed += 1
            log(f"  [FAIL] {s['key']} -> {e}")

    log(f"\n完成：删 {deleted} 个，失败 {failed} 个")


if __name__ == '__main__':
    main()
