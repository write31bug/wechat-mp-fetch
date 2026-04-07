# OpenClaw 恢复指南

> 本文档用于：重装系统 / 换电脑 / 版本回退后，快速恢复 OpenClaw 到正常工作状态。
> 版本：2026.4.2（回退目标）
> 创建时间：2026-04-07

---

## 一、恢复配置

### 1.1 备份文件清单（必留）

把这些文件同步到 Gitee 或 U盘：

```
E:\openclaw\
├── .openclaw\
│   └── openclaw.json          ← 核心配置（所有 agent/飞书/微信/route 配置）
├── .openclaw\agents\          ← 各 agent 的 workspace 配置
├── main\                      ← main agent 工作区（SOUL.md/USER.md/MEMORY.md 等）
├── dev\                       ← dev agent 工作区
├── writer\                    ← writer agent 工作区
├── finance\                   ← finance agent 工作区
├── community\                 ← community agent 工作区
└── tasks\                    ← 任务看板数据库
```

> ⚠️ `.openclaw\` 目录下有 Token 等敏感信息，禁止上传公有仓库！使用 Gitee 私有仓库。

### 1.2 安装 Node.js（如果需要）

```bash
# 推荐使用 nvm-windows 管理 Node 版本
# 安装 nvm：https://github.com/coreybutler/nvm-windows/releases
nvm install 24.0.0
nvm use 24.0.0
```

### 1.3 安装 OpenClaw

```bash
npm install -g openclaw@2026.4.2 --registry https://registry.npmmirror.com
```

### 1.4 恢复配置

从备份复制 `openclaw.json` 到：

```
C:\Users\你的用户名\.openclaw\openclaw.json
```

或通过命令行：

```bash
# 先创建目录
mkdir C:\Users\你的用户名\.openclaw\

# 从 Gitee 克隆配置（私有仓库）
git clone https://gitee.com/wehaohao/openclaw-backup.git
copy openclaw-backup\.openclaw\openclaw.json C:\Users\你的用户名\.openclaw\
```

---

## 二、安装 Skills

### 2.1 安装 ClawHub CLI

```bash
npm install -g clawhub --registry https://registry.npmmirror.com
```

### 2.2 安装 skills（从 Gitee 恢复）

```bash
# 进入工作区
cd E:\openclaw\main

# 从备份恢复 skills 目录
xcopy /E /I /Y E:\openclaw\backup\openclaw-main\skills E:\openclaw\main\skills\

# 或者重新从 ClawHub 安装需要的 skills
clawhub install baoyu-imagine
clawhub install baoyu-post-to-wechat
clawhub install baoyu-translate
clawhub install self-improving-agent
# ... 其他需要的 skill
```

### 2.3 安装 baoyu-skills 全家桶（如需要）

```bash
clawhub install baoyu-skills
```

---

## 三、恢复各 Agent Workspace

```bash
# 从备份复制各 agent 工作区
xcopy /E /I /Y E:\openclaw\backup\openclaw-backup\main E:\openclaw\main\
xcopy /E /I /Y E:\openclaw\backup\openclaw-backup\dev E:\openclaw\dev\
xcopy /E /I /Y E:\openclaw\backup\openclaw-backup\writer E:\openclaw\writer\
xcopy /E /I /Y E:\openclaw\backup\openclaw-backup\finance E:\openclaw\finance\
xcopy /E /I /Y E:\openclaw\backup\openclaw-backup\community E:\openclaw\community\
xcopy /E /I /Y E:\openclaw\backup\openclaw-backup\tasks E:\openclaw\tasks\
```

---

## 四、启动 Gateway

```bash
# 先检查版本
openclaw --version

# 启动
openclaw gateway start

# 检查状态
openclaw gateway status

# 查看日志
openclaw logs
```

---

## 五、验证恢复

### 5.1 检查状态

- [ ] `openclaw gateway status` 显示 Running
- [ ] 飞书 WebSocket 全连接（main/dev/writer/finance/community/xyyan）
- [ ] 微信 channel 正常

### 5.2 检查日志无报错

```bash
Get-Content C:\Users\你的用户名\AppData\Local\Temp\openclaw\openclaw-$(Get-Date -Format "yyyy-MM-dd").log | Select-String "ERROR"
```

### 5.3 测试各 agent

- [ ] main（小金）正常响应
- [ ] dev 正常工作
- [ ] writer 正常工作
- [ ] finance 正常工作
- [ ] community 正常工作

---

## 六、已知问题（2026.4.2 无此问题）

OpenClaw 2026.4.5 有 AJV schema 栈溢出 Bug（GitHub #61946），回退到 2026.4.2 可避免。

---

## 七、快捷命令汇总

```bash
# 安装
npm install -g openclaw@2026.4.2 --registry https://registry.npmmirror.com

# 启动
openclaw gateway start

# 状态
openclaw gateway status

# 日志
Get-Content C:\Users\Administrator\AppData\Local\Temp\openclaw\openclaw-$(Get-Date -Format "yyyy-MM-dd").log | Select-String "ERROR" | Select-Object -Last 20

# 强制重启（如需要）
Invoke-Item E:\openclaw\main\scripts\restart.bat
```

---

## 八、配置备份定时化（推荐）

把以下脚本加入 Windows 计划任务，每天自动备份配置到 Gitee：

```bash
# backup-openclaw-config.bat
cd E:\openclaw\backup\openclaw-backup
git add .
git commit -m "auto backup %date%"
git push
```

---

## 九、Gitee 仓库地址

- **整机备份**：https://gitee.com/wehaohao/openclaw-backup
- **知识沉淀**：https://gitee.com/wehaohao/openclaw-knowledge

---

_本文档由小金自动生成，最后更新：2026-04-07_
