import json, subprocess, re
from collections import defaultdict

result = subprocess.run([r'D:\work\software\nvm4w\nodejs\openclaw.cmd', 'sessions', '--all-agents', '--json'], capture_output=True, text=True)
data = json.loads(result.stdout)
sessions = data['sessions']

subagents = [s for s in sessions if re.search(r':subagent:', s['key'])]
old = [s for s in subagents if s.get('ageMs', 0) > 2*3600*1000]
old.sort(key=lambda x: x.get('ageMs', 0), reverse=True)

by_agent = defaultdict(list)
for s in old:
    by_agent[s['agentId']].append(s)

total = 0
for agent_id, items in by_agent.items():
    print(f'[{agent_id}] {len(items)} 个:')
    for s in items:
        h = s['ageMs'] // 3600000
        m = (s['ageMs'] % 3600000) // 60000
        key_short = s['key'][:70]
        print(f'  {h}h{m}m  {key_short}')
    total += len(items)

print()
print(f'总计: {total} 个 subagent session (age > 2h)')
