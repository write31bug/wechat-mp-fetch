# -*- coding: utf-8 -*-
"""
Skill Usage Tracker - 精确版
通过解析工具调用日志来统计 skill 真实使用次数
"""
import os, glob, re, json
from datetime import datetime, timedelta
from collections import defaultdict

LOG_DIR = os.path.expanduser("C:/Users/Administrator/AppData/Local/Temp/openclaw")
LOG_GLOB = os.path.join(LOG_DIR, "openclaw-*.log")
OUT_FILE = os.path.join(os.path.dirname(__file__), "..", "memory", "skill-usage.json")

def get_recent_logs(days=7):
    cutoff = datetime.now() - timedelta(days=days)
    files = glob.glob(LOG_GLOB)
    recent = []
    for f in files:
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(f))
            if mtime >= cutoff:
                recent.append((f, mtime))
        except:
            pass
    return sorted(recent, key=lambda x: x[1], reverse=True)

def extract_skill_calls(content):
    """
    从日志内容中提取真正被调用的 skill/tool 名称
    匹配模式: tool="xxx" 或 tools:["xxx"] 或 调用 skill 相关函数
    """
    results = []
    
    # 模式1: [tools] call tool=xxx 或 tool_name=xxx
    pattern1 = re.compile(r'\[tools\]\s+(?:call|call_tool|invoke).*?tool["\']?\s*[:=]\s*["\']?([a-z0-9_-]+)["\']?', re.IGNORECASE)
    # 模式2: tool=xxx 出现在工具调用行
    pattern2 = re.compile(r'tool=([a-z0-9_-]+)', re.IGNORECASE)
    # 模式3: MCP tool 调用 wecom_mcp call xxx.method
    pattern3 = re.compile(r'wecom_mcp\s+(?:call|list)\s+(\w+)', re.IGNORECASE)
    # 模式4: skill 调用
    pattern4 = re.compile(r'(?:skill|tool)[:\s]+([a-z][a-z0-9_-]+\.[a-z_]+)', re.IGNORECASE)
    # 模式5: function call 相关
    pattern5 = re.compile(r'"(name|tool)"\s*:\s*"?([a-z0-9_-]+)"?', re.IGNORECASE)
    
    for line in content.split('\n'):
        # 跳过列表输出行（skills list 的输出每个 skill 都会有类似条目）
        if 'skills list' in line.lower() or 'available skills' in line.lower():
            continue
        if '| ' in line and any(s in line for s in ['wecom-', 'baoyu-', 'skill-', 'agent-']):
            # 表格形式输出的 skills list，跳过
            continue
            
        for pat in [pattern1, pattern2, pattern3, pattern4, pattern5]:
            for m in pat.finditer(line):
                name = m.group(1) or m.group(2)
                if name and len(name) > 2:
                    results.append(name.lower())
    
    return results

def main(days=7):
    print(f"Scanning last {days} days logs...")
    log_files = get_recent_logs(days)
    print(f"Found {len(log_files)} log files")
    
    # 也扫描更长时间（30天）找从没用过的
    all_log_files = get_recent_logs(30)
    
    skill_counts = defaultdict(lambda: {'count': 0, 'dates': defaultdict(int)})
    all_skill_counts = defaultdict(lambda: {'count': 0})
    
    date_re = re.compile(r'20\d{2}-\d{2}-\d{2}')
    total_lines = 0
    
    for fpath, mtime in all_log_files:
        date_str = mtime.strftime('%Y-%m-%d')
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                total_lines += len(lines)
                
                # 提取 skill 调用
                calls = extract_skill_calls(content)
                for call in calls:
                    all_skill_counts[call]['count'] += 1
                    if fpath in [x[0] for x in log_files]:
                        skill_counts[call]['count'] += 1
                        skill_counts[call]['dates'][date_str] += 1
        except Exception as e:
            print(f"Error: {fpath}: {e}")
    
    print(f"Total lines scanned: {total_lines}")
    print(f"Unique tool/skill names found: {len(all_skill_counts)}")
    
    # 生成报告
    report = {
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'period_days': days,
        'log_files_scanned': len(all_log_files),
        'total_lines': total_lines,
        'total_unique_tools': len(all_skill_counts),
    }
    
    # 排序
    sorted_usage = dict(sorted(all_skill_counts.items(), key=lambda x: -x[1]['count']))
    
    # 分类
    wecom = {k:v for k,v in sorted_usage.items() if k.startswith('wecom')}
    baoyu = {k:v for k,v in sorted_usage.items() if k.startswith('baoyu')}
    other = {k:v for k,v in sorted_usage.items() if not k.startswith('wecom') and not k.startswith('baoyu')}
    
    report['usage'] = sorted_usage
    report['wecom_tools'] = dict(sorted(wecom.items(), key=lambda x: -x[1]['count']))
    report['baoyu_tools'] = dict(sorted(baoyu.items(), key=lambda x: -x[1]['count']))
    report['other_tools'] = dict(sorted(other.items(), key=lambda x: -x[1]['count']))
    
    # 保存 JSON
    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 打印摘要
    print(f"\n{'='*55}")
    print(f"Skill Usage Report ({days} days / 30 days total)")
    print(f"Generated: {report['generated_at']}")
    print(f"{'='*55}")
    
    def print_section(title, data, top_n=20):
        if not data:
            print(f"\n{title}: None")
            return
        items = list(data.items())[:top_n]
        print(f"\n{title} ({len(data)} total):")
        for name, info in items:
            c = info['count'] if isinstance(info, dict) else info
            bar = '#' * min(int(c), 50)
            print(f"  {name:<40} {c:>5}  {bar}")
    
    print_section("Wecom Tools", wecom)
    print_section("Baoyu Tools", baoyu)
    print_section("Other Tools", other)
    
    # 未使用的 skill（从 known skills 列表）
    known_but_unused = [
        'summarize', 'obsidian', 'apple-notes', 'apple-reminders',
        'bear-notes', 'blogwatcher', 'blucli', 'bluebubbles',
        'camsnap', 'clawhub', 'coding-agent', 'discord',
        'eightctl', 'gemini', 'gh-issues', 'gifgrep',
        'github', 'gog', 'goplaces', 'himalaya', 'imsg',
        'model-usage', 'notion', 'openai-whisper', 'openai-whisper-api',
        'openhue', 'oracle', 'ordercli', 'peekaboo',
        'sag', 'session-logs', 'sherpa-onnx-tts', 'slack',
        'songsee', 'sonoscli', 'spotify-player', 'summarize',
        'things-mac', 'tmux', 'trello', 'video-frames',
        'voice-call', 'wacli', 'xurl', '1password'
    ]
    
    unused = [s for s in known_but_unused if s not in all_skill_counts or all_skill_counts[s]['count'] == 0]
    print(f"\n[Never Used] ({len(unused)} skills):")
    for s in unused:
        print(f"  - {s}")
    
    print(f"\n[Saved] {OUT_FILE}")
    
    return report

if __name__ == '__main__':
    import sys
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    main(days)
