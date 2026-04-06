# -*- coding: utf-8 -*-
import sys, os
sys.stdout.reconfigure(encoding='utf-8')

main = r'E:\openclaw\main'
for entry in os.scandir(main):
    if not entry.is_dir():
        continue
    name = entry.name
    # Check if has CJK characters (common in Chinese)
    has_cjk = any(ord(c) > 0x2e80 for c in name)
    if has_cjk:
        print("Dir name:", repr(name))
        print("Dir name decode attempt:", name.encode('utf-8', errors='replace'))
        for f in os.listdir(entry.path):
            fp = os.path.join(entry.path, f)
            size = os.path.getsize(fp)
            print("  File:", repr(f), f"({size}B)")
            try:
                with open(fp, 'r', encoding='gb18030') as fh:
                    content = fh.read(300)
                print("  Preview:", content[:200])
            except Exception as e:
                print("  Error:", e)
