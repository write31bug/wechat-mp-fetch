import json, subprocess, re

result = subprocess.run([r'D:\work\software\nvm4w\nodejs\openclaw.cmd', 'sessions', '--all-agents', '--json'], capture_output=True, text=True)
data = json.loads(result.stdout)
sessions = data['sessions']

subagents = [s for s in sessions if re.search(r':subagent:', s['key'])]
print(f'Subagent sessions: {len(subagents)}')
print()

# 按 systemSent 分组
with_system = [s for s in subagents if s.get('systemSent', False)]
without_system = [s for s in subagents if not s.get('systemSent', False)]
print(f'systemSent=true: {len(with_system)} (说明: gateway曾尝试往这个session发消息但失败了)')
print(f'systemSent=false: {len(without_system)} (说明: 可能是活跃session或未触发过消息投递)')
print()

# 2h+ old
old = [s for s in subagents if s.get('ageMs', 0) > 2*3600*1000]
print(f'2h+ old: {len(old)}')
old_system = [s for s in old if s.get('systemSent', False)]
old_no_system = [s for s in old if not s.get('systemSent', False)]
print(f'  systemSent=true (已尝试投递失败): {len(old_system)}')
print(f'  systemSent=false: {len(old_no_system)}')
print()

# 金哥要删的是 "跑完了但没清理" 的
# systemSent=true 说明gateway知道这个session已经无效了（发过消息失败了）
# 所以这些是最安全的待删除目标
to_delete = [s for s in old if s.get('systemSent', False)]
print(f'建议删除目标 (systemSent=true + 2h+): {len(to_delete)} 个')
print()

if to_delete:
    from collections import defaultdict
    by_agent = defaultdict(list)
    for s in to_delete:
        by_agent[s['agentId']].append(s)

    for agent_id, items in by_agent.items():
        print(f'【{agent_id}】 {len(items)} 个:')
        for s in items:
            h = s['ageMs'] // 3600000
            m = (s['ageMs'] % 3600000) // 60000
            print(f'  age={h}h{m}m key={s["key"][:65]}')
