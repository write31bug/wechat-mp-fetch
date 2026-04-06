import json, subprocess, re

result = subprocess.run([r'D:\work\software\nvm4w\nodejs\openclaw.cmd', 'sessions', '--all-agents', '--json'], capture_output=True, text=True)
data = json.loads(result.stdout)
sessions = data['sessions']

subagents = [s for s in sessions if re.search(r':subagent:', s['key'])]
print(f'Total subagent sessions: {len(subagents)}')
print(f'With abortedLastRun=true: {sum(1 for s in subagents if s.get("abortedLastRun", False))}')
print(f'With abortedLastRun=false: {sum(1 for s in subagents if not s.get("abortedLastRun", False))}')

old = [s for s in subagents if s.get('ageMs', 0) > 2*3600*1000 and not s.get('abortedLastRun', False)]
print(f'Old (2h+) and aborted=false: {len(old)}')
for s in old[:5]:
    h = s.get('ageMs', 0) // 3600000
    print(f'  age={h}h aborted={s.get("abortedLastRun")} key={s["key"][:70]}')
