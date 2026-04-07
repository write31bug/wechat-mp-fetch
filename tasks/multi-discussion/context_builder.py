# context_builder.py
"""
多 Agent 讨论系统 · 上下文构建器
负责：给每个 agent 组装它该看到的上下文
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class AgentConfig:
    """单个 agent 的配置"""
    id: str
    name: str
    role: str
    personality: str = ""
    model: str = ""
    temperature: float = 0.7


@dataclass
class Message:
    """一条发言"""
    agent_id: str
    agent_name: str
    round_num: int
    content: str
    timestamp: str = ""


class ContextBuilder:
    """上下文构建器"""

    def __init__(self, topic: str):
        self.topic = topic

    def build(self, round_num: int, total_rounds: int,
              agent: AgentConfig,
              history: List[Message],
              this_round_previous: Optional[List[Message]] = None) -> str:
        """
        构建发送给单个 agent 的完整上下文。

        参数：
            round_num        当前轮次（从 1 开始）
            total_rounds     总轮次
            agent            当前 agent 的配置
            history          之前所有轮次的发言（所有 agent 的）
            this_round_previous  本轮前面已经发言的 agent 内容（串行模式）
        """
        parts = []

        # 1. 头部：主题 + 轮次
        parts.append(self._header(round_num, total_rounds))

        # 2. 角色说明
        parts.append(self._role_card(agent))

        # 3. 历史发言（之前所有轮次）
        parts.append(self._history_section(history))

        # 4. 本轮其他人已发言的内容（串行模式）
        if this_round_previous:
            parts.append(self._this_round_section(this_round_previous))

        # 5. 输出格式要求
        parts.append(self._instructions())

        return "\n\n".join(parts)

    # ────────────────────────────────────────────────
    # 私有方法
    # ────────────────────────────────────────────────

    def _header(self, round_num: int, total_rounds: int) -> str:
        return f"""# 讨论主题

{self.topic}

# 当前轮次

第 {round_num} 轮（共 {total_rounds} 轮）"""

    def _role_card(self, agent: AgentConfig) -> str:
        lines = [
            f"# 你的身份",
            f"**角色名称**：{agent.name}",
            f"**角色定位**：{agent.role}",
        ]
        if agent.personality:
            lines.append(f"**性格特点**：{agent.personality}")
        return "\n".join(lines)

    def _history_section(self, history: List[Message]) -> str:
        """展示之前所有轮次的发言。按轮次分组。"""
        if not history:
            return "# 历史发言\n\n（暂无历史发言）"

        # 按轮次分组
        rounds: Dict[int, List[Message]] = {}
        for msg in history:
            rounds.setdefault(msg.round_num, []).append(msg)

        lines = ["# 历史发言\n"]
        for rnum in sorted(rounds.keys()):
            lines.append(f"\n## 第 {rnum} 轮\n")
            for msg in rounds[rnum]:
                lines.append(f"### {msg.agent_name} 的发言\n")
                lines.append(f"{msg.content}\n")

        return "\n".join(lines)

    def _this_round_section(self, this_round_previous: List[Message]) -> str:
        """本轮前面已发言的内容（串行模式）。"""
        lines = ["\n# 本轮其他人的发言\n"]
        for msg in this_round_previous:
            lines.append(f"### {msg.agent_name}（本轮先于你发言）\n")
            lines.append(f"{msg.content}\n")
        return "\n".join(lines)

    def _instructions(self) -> str:
        return """# 你的发言

请基于你的角色立场，针对上述讨论发表你的观点。

要求：
1. 回应历史发言中的关键论点
2. 保持角色一致性
3. 提出新的论据或视角
4. 控制在 200-500 字

现在请开始你的发言："""
