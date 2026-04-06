import json

path = r'E:\openclaw\.openclaw\agents\main\sessions\sessions.json'
with open(path, 'r', encoding='utf-8') as f:
    d = json.load(f)

keys = list(d.keys())
print(f'Total entries: {len(keys)}')
print('Sample keys:')
for k in keys[:5]:
    print(f'  {k}')
