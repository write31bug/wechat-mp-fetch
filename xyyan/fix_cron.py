import json
with open(r'E:\openclaw\.openclaw\cron\jobs.json', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('"runningAtMs": 1775403720875', '"runningAtMs": null')
content = content.replace('"lastRunAtMs": 1775403623591', '"lastRunAtMs": 1')

with open(r'E:\openclaw\.openclaw\cron\jobs.json', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed: cleared runningAtMs and lastRunAtMs for auto-xyyan cron job')
