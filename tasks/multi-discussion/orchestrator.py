# orchestrator.py
"""
多 Agent 讨论系统 · 主调度器

职责：
1. session 初始化
2. 每轮每 agent 的上下文构建
3. 通过 sessions_spawn 调用各 agent（由 LLM 执行）
4. 存储发言记录
5. 生成总结

sessions_spawn 集成方式：
  orchestrator 负责构建调用参数 → LLM 执行 sessions_spawn → 结果存入 storage
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict

from storage_manager import StorageManager, SessionPaths
from context_builder import ContextBuilder, AgentConfig, Message
from summary_generator import SummaryGenerator, Summary


@dataclass
class OrchestratorConfig:
    """调度配置"""
    rounds: int = 3
    max_tokens_per_turn: int = 800


class DiscussionOrchestrator:
    """
    讨论调度器。

    使用方式（LLM 调度）：
      orch = DiscussionOrchestrator(topic, agents, config)
      orch.init_session()

      for round_num in range(1, config.rounds + 1):
          for agent in orch.agents:
              # 1. 构建上下文
              context = orch.build_context(round_num, agent)

              # 2. LLM 执行 sessions_spawn
              #    sessions_spawn(
              #        agent_id=agent.id,
              #        task=f"你是 {agent.name}。\n\n{context}",
              #        runtime="subagent",
              #        mode="run",
              #        cleanup="delete"
              #    )

              # 3. LLM 返回结果后，调用：
              orch.save_contribution(agent.id, round_num, llm_result)

      # 生成总结
      summary_prompt = orch.build_summary_prompt()
      # LLM 执行总结 → orch.save_summary(result)
      orch.complete()
    """

    def __init__(self, topic: str, agents: List[AgentConfig],
                 config: OrchestratorConfig = None):
        self.topic = topic
        self.agents = agents
        self.agent_map: Dict[str, AgentConfig] = {a.id: a for a in agents}
        self.config = config or OrchestratorConfig()
        self.storage = StorageManager()
        self.ctx_builder = ContextBuilder(topic)
        self.paths: Optional[SessionPaths] = None
        self._all_messages: List[Message] = []

    # ──────────────────────────────────────────────
    # 生命周期
    # ──────────────────────────────────────────────

    def init_session(self) -> SessionPaths:
        """初始化 session（创建目录/manifest）"""
        self.paths = self.storage.init_session(
            topic=self.topic,
            agents=[a.id for a in self.agents],
            rounds=self.config.rounds
        )
        self.storage.update_manifest_status(self.paths, "IN_PROGRESS")
        return self.paths

    def complete(self):
        """标记讨论完成"""
        if self.paths:
            self.storage.update_manifest_status(self.paths, "COMPLETED")

    # ──────────────────────────────────────────────
    # 上下文构建（供 LLM 调用 sessions_spawn）
    # ──────────────────────────────────────────────

    def build_context(self, round_num: int, agent: AgentConfig,
                     this_round_previous: List[Message] = None) -> str:
        """
        构建 agent 的上下文 prompt。
        LLM 用这个 prompt 调用 sessions_spawn。
        """
        return self.ctx_builder.build(
            round_num=round_num,
            total_rounds=self.config.rounds,
            agent=agent,
            history=self._all_messages,
            this_round_previous=this_round_previous or []
        )

    def build_summary_prompt(self) -> str:
        """构建总结 prompt"""
        gen = SummaryGenerator()
        return gen.generate(self._all_messages, self.agent_map)

    # ──────────────────────────────────────────────
    # 结果存储（LLM 返回后调用）
    # ──────────────────────────────────────────────

    def save_contribution(self, agent_id: str, round_num: int, content: str):
        """保存单个 agent 的发言"""
        agent = self.agent_map.get(agent_id)
        if not agent:
            agent = AgentConfig(id=agent_id, name=agent_id, role="")

        msg = Message(
            agent_id=agent_id,
            agent_name=agent.name,
            round_num=round_num,
            content=content,
            timestamp=datetime.now().isoformat()
        )
        self._all_messages.append(msg)

        # 追加到 history.json
        self.storage.append_history(self.paths, round_num, [
            {"agent": m.agent_id, "content": m.content, "timestamp": m.timestamp}
            for m in self._all_messages if m.round_num == round_num
        ])
        # 更新 manifest 当前轮次
        self.storage.update_manifest_round(self.paths, round_num)

        # 保存发言文件
        self.storage.save_contribution(self.paths, agent_id, round_num, content)

    def save_summary(self, summary_content: str):
        """保存总结报告"""
        if self.paths:
            gen = SummaryGenerator()
            try:
                summary_obj = gen.parse_result(summary_content, self.agent_map)
            except Exception:
                summary_obj = Summary(
                    key_consensus=["（总结解析失败）"],
                    key_disagreements=[],
                    recommendation=summary_content[:500],
                    agent_views={}
                )
            md = gen.format_markdown(summary_obj, self.topic, self.agent_map)
            self.storage.write_summary(self.paths, md)

    # ──────────────────────────────────────────────
    # 便利属性
    # ──────────────────────────────────────────────

    @property
    def all_messages(self) -> List[Message]:
        return self._all_messages

    @property
    def session_path(self) -> Optional[str]:
        return str(self.paths.base) if self.paths else None
