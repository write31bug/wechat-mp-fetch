import json, subprocess, re
from collections import defaultdict

OPENCLAW_BIN = r'D:\work\software\nvm4w\nodejs\openclaw.cmd'
AGE_HOURS = 2

result = subprocess.run([OPENCLAW_BIN, 'sessions', '--all-agents', '--json'], capture_output=True, text=True)
data = json.loads(result.stdout)
sessions = data['sessions']

# 筛选: subagent + age > 2h
to_delete = []
for s in sessions:
    key = s['key']
    if not re.search(r':subagent:', key):
        continue
    if s.get('ageMs', 0) <= AGE_HOURS * 3600 * 1000:
        continue
    to_delete.append(key)

print(f'准备删除 {len(to_delete)} 个 session...\n')

ok = 0
fail = 0
for key in to_delete:
    r = subprocess.run([OPENCLAW_BIN, 'sessions', 'delete', key], capture_output=True, text=True)
    if r.returncode == 0:
        ok += 1
        print(f'[OK] {key[:70]}')
    else:
        fail += 1
        print(f'[FAIL] {key[:70]} - {r.stderr[:100]}')

print(f'\n完成: 成功 {ok} 个，失败 {fail} 个')
