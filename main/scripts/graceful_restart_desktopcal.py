"""
使用 WM_CLOSE 优雅关闭 DesktopCal 进程，等待其自行退出
然后重新启动 desktopcal.exe
"""
import subprocess, time, os, sys

DESKTOPCAL_EXE = r'C:\Users\Administrator\AppData\Roaming\CalendarTask\desktopcal.exe'

def get_pids():
    r = subprocess.run(
        ['powershell', '-NoProfile', '-Command',
         "Get-CimInstance Win32_Process -Filter \"name='desktopcal.exe' -or name='dkdockhost.exe'\" | ConvertTo-Json -Compress"],
        capture_output=True
    )
    text = r.stdout.decode('utf-8', errors='replace').strip()
    if not text:
        return []
    import json
    pids = json.loads(text)
    if isinstance(pids, dict):
        pids = [pids]
    return [(p['ProcessId'], p['ProcessName']) for p in pids]

def graceful_shutdown():
    """发送 WM_CLOSE (0x0010) 让进程正常关闭"""
    pids = get_pids()
    if not pids:
        print('[INFO] No processes to close')
        return

    print(f'[CLOSE] Sending WM_CLOSE to: {pids}')
    for pid, name in pids:
        # 使用 PowerShell 的 PostMessage 发送 WM_CLOSE
        r = subprocess.run([
            'powershell', '-NoProfile', '-Command',
            f'''
            Add-Type @"
            using System;
            using System.Runtime.InteropServices;
            public class WinAPI {{
                [DllImport("user32.dll", SetLastError=true)]
                public static extern IntPtr FindWindow(IntPtr hwndParent, IntPtr hwndParentAfter, string lpClassName, string lpWindowName);
                [DllImport("user32.dll", SetLastError=true)]
                public static extern IntPtr SendMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);
            }}
"@
            $hwnd = (Get-Process -Id {pid}).MainWindowHandle
            if ($hwnd -ne [IntPtr]::Zero) {{
                [WinAPI]::SendMessage($hwnd, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero)
                Write-Host "Sent WM_CLOSE to PID {pid}"
            }} else {{
                # 进程没有窗口，用 taskkill 作为后备
                Write-Host "No window handle for PID {pid}, using taskkill"
                Start-Process taskkill -ArgumentList "/PID {pid} /F" -NoNewWindow -Wait
            }}
            '''
        ], capture_output=True, text=True)
        print(f'  {r.stdout}')
        if r.stderr:
            print(f'  stderr: {r.stderr[:100]}')

    # 等待进程自行退出
    print('[WAIT] Waiting for processes to exit (max 5s)...')
    for _ in range(10):
        time.sleep(0.5)
        remaining = get_pids()
        if not remaining:
            print('[OK] All processes exited')
            return
        print(f'  Still running: {remaining}')

    # 如果还没退出，强制杀
    print('[WARN] Graceful exit timeout, force killing...')
    for pid, name in get_pids():
        subprocess.run(['taskkill', '/PID', str(pid), '/F'],
                      stdout=open(os.devnull,'w'), stderr=open(os.devnull,'w'))

if __name__ == '__main__':
    graceful_shutdown()
    print('[START] Launching DesktopCal...')
    subprocess.Popen([DESKTOPCAL_EXE],
                    stdout=open(os.devnull,'w'), stderr=open(os.devnull,'w'))
    print('[OK] DesktopCal started')
