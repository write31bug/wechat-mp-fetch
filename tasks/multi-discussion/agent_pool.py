# agent_pool.py
"""
多 Agent 讨论系统 · Agent 池

sessions_spawn 是 OpenClaw LLM 工具，不能直接 import。
本模块的作用：
1. 构建完整的 sessions_spawn 调用参数（供 LLM 执行）
2. 提供上下文构建辅助

实际执行：由 LLM 看到 ToolCall 描述后，以 tool_call 方式调用 sessions_spawn。
"""

from dataclasses import dataclass
from typing import Optional

from context_builder import AgentConfig


@dataclass
class ToolCall:
    """
    sessions_spawn 调用描述符。
    orchestrator 生成后，LLM 以 tool_call 方式执行 sessions_spawn。

    参数说明：
    - tool_name: 固定 "sessions_spawn"
    - agent_id: subagent 标识，对应 workspace 名称
    - task: 完整 prompt
    - runtime: 固定 "subagent"
    - mode: 固定 "run"
    - model: 模型名称（可选，默认空字符串）
    - cleanup: 固定 "delete"
    """
    tool_name: str
    agent_id: str
    task: str
    runtime: str = "subagent"
    mode: str = "run"
    model: str = ""
    cleanup: str = "delete"


class AgentPool:
    """
    Agent 池 — 准备 sessions_spawn 调用参数。

    使用方式（LLM 调度）：
      pool = AgentPool()
      tc = pool.prepare_call(agent, context)
      # LLM 执行: sessions_spawn(
      #     agent_id=tc.agent_id,
      #     task=tc.task,
      #     runtime=tc.runtime,
      #     mode=tc.mode,
      #     model=tc.model,
      #     cleanup=tc.cleanup
      # )
    """

    def __init__(self, default_model: str = "gpt-4o"):
        self.default_model = default_model

    def prepare_call(self, agent: AgentConfig, context: str) -> ToolCall:
        """
        准备一个 sessions_spawn 调用。
        """
        system_prompt = self._build_system_prompt(agent)
        full_prompt = f"{system_prompt}\n\n{context}"

        return ToolCall(
            tool_name="sessions_spawn",
            agent_id=agent.id,
            task=full_prompt,
            runtime="subagent",
            mode="run",
            model=agent.model or self.default_model,
            cleanup="delete"
        )

    def prepare_summary_call(self, prompt: str) -> ToolCall:
        """准备总结 LLM 调用"""
        return ToolCall(
            tool_name="sessions_spawn",
            agent_id="summary",
            task=prompt,
            runtime="subagent",
            mode="run",
            model=self.default_model,
            cleanup="delete"
        )

    def _build_system_prompt(self, agent: AgentConfig) -> str:
        """构建 agent 的 system prompt"""
        parts = [f"你是 {agent.name}。"]
        if agent.role:
            parts.append(f"\n角色定位：{agent.role}")
        if agent.personality:
            parts.append(f"\n性格特点：{agent.personality}")
        parts.append("\n请严格按照你的角色立场发言，保持一致性。")
        return "".join(parts)
