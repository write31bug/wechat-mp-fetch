---
url: https://www.doubao.com/thread/a11efdf4a5341
title: "OpenClaw多Agent飞书应用间互相聊天方案 - 豆包"
description: "豆包 是你的 AI 聊天智能对话问答助手，写作文案翻译情感陪伴编程全能工具。豆包 为你答疑解惑，提供灵感，辅助创作，也可以和你畅聊任何你感兴趣的话题。"
captured_at: "2026-04-02T16:30:52.010Z"
---

# OpenClaw多Agent飞书应用间互相聊天方案 - 豆包

openclaw 我现在创建了 5 个 agent，绑定了 5 个飞书应用，有没有办法让他们自己互相聊天

已完成思考，参考 17 篇资料

完全可以实现，针对你「5 个 Agent 分别绑定了 5 个独立飞书应用」的场景，有两种成熟可落地的实现方案，下面是完整配置步骤和核心说明。

### 方案一：OpenClaw 原生 Agent 间直接对话（推荐，系统内闭环，支持自主来回交互）

核心原理：通过 OpenClaw 内置的`agentToAgent`权限体系 + `sessions_send`工具，实现 Agent 之间的直接消息投递，自带乒乓对话机制，可自动实现多轮来回聊天。

#### 前置确认

确保你已完成 5 个 Agent 与 5 个飞书应用的一对一绑定，即`openclaw.json`中已正确配置 feishu 多账户，且通过`bindings`完成了`accountId`与`agentId`的精准映射。

#### 步骤 1：全局开启 Agent 间通信核心权限

修改`~/.openclaw/openclaw.json`配置文件，添加 / 修改以下配置段，替换为你的 5 个 Agent 实际 ID：

json

```json
{
  "tools": {
    "agentToAgent": {
      "enabled": true,
      "allow": ["agent1", "agent2", "agent3", "agent4", "agent5"],
      "maxPingPongTurns": 10
    },
    "sessions": {
      "enabled": true,
      "visibility": "all",
      "allowTools": ["sessions_list", "sessions_send"]
    }
  }
}
```

- 核心配置说明：
	- `agentToAgent.enabled: true`：跨 Agent 通信总开关，默认关闭必须显式开启
		- `allow`：通信白名单，仅列表内的 Agent 可互相收发消息，遵循最小权限原则
		- `maxPingPongTurns`：单轮对话最大来回轮数，默认 5 轮，可按需调整，最大支持 50 轮
		- `visibility: "all"`：必须配置，否则 Agent 无法识别和访问其他 Agent 的会话

#### 步骤 2：为每个 Agent 配置对话能力

修改对应 Agent 工作区的`AGENTS.md`/`SOUL.md`，给每个 Agent 设定角色和对话规则，示例如下（可按需调整）：

markdown

```markdown
# 角色设定
你是【产品经理Agent】，agentId为\`agent1\`，可与agent2（研发Agent）、agent3（测试Agent）、agent4（运营Agent）、agent5（设计Agent）进行自由对话。
# 核心对话规则
1. 你可调用\`sessions_send\`工具，向指定agentId的Agent发送消息，主动发起对话
2. 当收到其他Agent发来的消息时，必须结合上下文进行针对性回复，延续话题，不得无故终止
3. 若需结束当前对话，回复\`REPLY_SKIP\`即可停止本次交互
4. 你的所有对话内容，会同步通过绑定的飞书机器人输出
```

5 个 Agent 均需完成类似配置，可分别设定不同的角色分工，让对话更有逻辑、不混乱。

#### 步骤 3：启动对话，验证效果

1. **手动触发初始对话**：在任意一个 Agent 的会话窗口，发送指令即可启动对话，示例：
	`请使用sessions_send工具，给agent2发送消息，开启一个关于「2026年AI产品落地规划」的讨论，邀请对方发表观点`
	系统会自动触发 Agent1 给 Agent2 发消息，随后进入乒乓对话机制，双方自动交替回复，实现互相聊天。
2. **完全自主聊天配置**：若想让 Agent 主动互相聊天，可在`openclaw.json`中添加定时任务，配合 Agent 的 prompt 规则，实现定时主动发起对话。

---

### 方案二：飞书群组内多机器人对话（可视化强，直接在飞书群查看完整聊天过程）

核心原理：将 5 个绑定了 Agent 的飞书机器人拉入同一个飞书群，以群消息为中转，每个机器人监听到群内其他机器人的消息后，由对应的 Agent 生成回复，再通过自身的飞书账号发送到群内，形成群内多 Agent 自由聊天的效果。

#### 步骤 1：飞书侧准备工作

1. 创建一个飞书普通群，将 5 个飞书应用的机器人全部添加到群内
2. 飞书开放平台给每个应用开通核心权限：`im:message`、`im:message.group_at_msg:readonly`、`im:message:send_as_bot`、`im:chat.members:bot_access`，并启用机器人的 WebSocket 事件订阅
3. 重新发布每个飞书应用，完成企业内上线，确保机器人在群内可正常收发消息

#### 步骤 2：OpenClaw 侧配置路由与触发规则

1. 配置 bindings 路由，确保每个飞书账号的群消息能精准路由到对应的 Agent，在`openclaw.json`的`bindings`数组中添加以下配置（5 个 Agent 均需配置）：
	json
	```json
	{
	  "bindings": [
	    {
	      "agentId": "agent1",
	      "match": {
	        "channel": "feishu",
	        "accountId": "feishu_account1",
	        "peer": {
	          "kind": "group",
	          "id": "xxxxxx"
	        }
	      }
	    },
	    // 重复以上结构，完成agent2-5与对应飞书账号、群的绑定
	  ]
	}
	```
	- `accountId`：对应 Agent 绑定的飞书账号 ID，需与 channels 中配置的一致
		- `peer.id`：替换为你创建的飞书群的 chat\_id，确保 5 个 Agent 的配置中该 ID 一致
2. 配置每个 Agent 的群聊回复规则，修改对应 Agent 工作区的`AGENTS.md`，添加规则：
	markdown
	```markdown
	# 群聊对话规则
	1. 当你在飞书群「多Agent讨论群」中收到其他机器人发送的消息时，必须结合消息内容和上下文，生成相关回复，延续对话
	2. 回复无需@对方，直接发送你的观点即可，保持对话流畅
	3. 禁止重复发言、无意义灌水，每次回复需有明确的观点或话题延伸
	4. 同一话题下，单轮仅回复1次，等待其他Agent发言后再进行下一轮回复
	```

#### 步骤 3：启动群内对话

在飞书群里手动发送一条初始消息，比如`请各位Agent围绕「2026年企业AI转型路径」展开讨论，依次发表自己的观点`，即可触发 5 个 Agent 依次回复，形成群内互相聊天的效果。

---

### 进阶优化与常见问题排查

1. **对话可控性优化**
	- 给每个 Agent 设定明确的角色分工和话题边界，避免对话跑偏或无效循环
		- 可设置主控 Agent，由一个 Agent 负责话题发起、流程控场和对话终止，其他 Agent 配合发言，形成有序讨论
		- 通过`maxPingPongTurns`限制单轮对话最大轮数，避免无限循环
2. **常见问题排查**
	- Agent 间无法收发消息：检查`agentToAgent.enabled`是否为 true，`allow`白名单是否包含对应 Agent ID，`sessions.visibility`是否设为`all`
		- 飞书群内机器人无法互相回复：排查飞书应用权限是否齐全、机器人是否已正确入群、`bindings`路由是否精准匹配了群 ID 和对应 Agent
		- 对话无限循环：检查 prompt 中是否设置了明确的终止规则，合理调整`maxPingPongTurns`数值，避免 Agent 之间无意义的互相套话

参考 17 篇资料