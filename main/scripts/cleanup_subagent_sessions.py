"""
cleanup_subagent_sessions.py
清理超过2小时的 subagent session

关键：abortedLastRun 字段不可靠，无法区分活跃/结束
只用 ageMs > 2小时 + key含subagent 判断
"""

import json
import subprocess
import re
from datetime import datetime, timezone

# ==================== 配置 ====================
DRY_RUN = False          # True = 只输出，False = 真正删除
AGE_HOURS = 2            # 超过多少小时算过期
CONFIRM_REQUIRED = False  # 直接删除，不确认
# ==================== 配置 ====================

NOW_MS = int(datetime.now(timezone.utc).timestamp() * 1000)
AGE_MS = AGE_HOURS * 60 * 60 * 1000
CUTOFF = NOW_MS - AGE_MS

OPENCLAW_BIN = r"D:\work\software\nvm4w\nodejs\openclaw.cmd"

def get_sessions():
    result = subprocess.run(
        [OPENCLAW_BIN, "sessions", "--all-agents", "--json"],
        capture_output=True, text=True
    )
    data = json.loads(result.stdout)
    return data["sessions"]

def is_subagent_session(key):
    return bool(re.search(r":subagent:", key))

def format_age_ms(ms):
    total_sec = ms // 1000
    h = total_sec // 3600
    m = (total_sec % 3600) // 60
    s = total_sec % 60
    if h > 0:
        return f"{h}h {m}m"
    elif m > 0:
        return f"{m}m {s}s"
    else:
        return f"{s}s"

def main():
    sessions = get_sessions()

    expired = []
    for s in sessions:
        key = s.get("key", "")
        age_ms = s.get("ageMs", 0)

        # 只看 subagent
        if not is_subagent_session(key):
            continue

        # 超过阈值
        if age_ms < AGE_MS:
            continue

        expired.append({
            "key": key,
            "agentId": s.get("agentId", "unknown"),
            "ageMs": age_ms,
            "ageStr": format_age_ms(age_ms),
        })

    # 按 ageMs 降序（最老的排前面）
    expired.sort(key=lambda x: x["ageMs"], reverse=True)

    print(f"\n{'='*60}")
    print(f"Subagent Session 清理")
    print(f"{'='*60}")
    print(f"阈值：{AGE_HOURS} 小时")
    print(f"当前：{datetime.fromtimestamp(NOW_MS/1000, tz=timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"扫描：{len(sessions)} 个 session")
    print(f"条件：key 含 ':subagent:' + age>{AGE_HOURS}h")
    print(f"\n找到 {len(expired)} 个待删：\n")

    if not expired:
        print("没有需要清理的 session。")
        return

    from collections import defaultdict
    by_agent = defaultdict(list)
    for s in expired:
        by_agent[s["agentId"]].append(s)

    for agent_id, items in by_agent.items():
        print(f"【{agent_id}】{len(items)} 个：")
        for s in items:
            print(f"  - {s['key'][:70]}")
            print(f"    age={s['ageStr']}")

    print(f"\n{'='*60}")
    if DRY_RUN:
        print(f"[DRY-RUN] 共 {len(expired)} 个，未实际删除")
    else:
        print(f"[删除中...] 共 {len(expired)} 个")

    if not DRY_RUN:
        if CONFIRM_REQUIRED:
            confirm = input(f"\n确认删除 {len(expired)} 个？(y/N): ")
            if confirm.lower() != "y":
                print("取消。")
                return

        deleted = 0
        failed = 0
        for s in expired:
            result = subprocess.run(
                [OPENCLAW_BIN, "sessions", "delete", s["key"]],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                deleted += 1
            else:
                failed += 1
                print(f"  [FAIL] {s['key'][:60]}")

        print(f"\n完成：删 {deleted} 个，失败 {failed} 个")

if __name__ == "__main__":
    main()
