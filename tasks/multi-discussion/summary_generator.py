# summary_generator.py
"""
多 Agent 讨论系统 · 总结生成器
负责：分析所有发言，生成结构化总结报告
"""

import json
from dataclasses import dataclass
from typing import List, Dict

from context_builder import Message, AgentConfig


@dataclass
class Summary:
    """总结报告结构"""
    key_consensus: List[str]
    key_disagreements: List[str]
    recommendation: str
    agent_views: Dict[str, str]


class SummaryGenerator:
    """总结生成器"""

    def __init__(self):
        pass

    def generate(self, messages: List[Message],
                 agents: Dict[str, AgentConfig]) -> str:
        """
        构建总结任务的 prompt。
        返回 prompt 字符串，由 orchestrator 调用 LLM。
        """
        return self._build_prompt(messages, agents)

    def parse_result(self, raw: str, agents: Dict[str, AgentConfig]) -> Summary:
        """解析 LLM 返回结果"""
        try:
            data = json.loads(raw)
            return Summary(
                key_consensus=data.get("key_consensus", []),
                key_disagreements=data.get("key_disagreements", []),
                recommendation=data.get("recommendation", ""),
                agent_views=data.get("agent_views", {})
            )
        except json.JSONDecodeError:
            return Summary(
                key_consensus=["（总结生成失败，请手动查看发言记录）"],
                key_disagreements=[],
                recommendation=raw[:500] if raw else "（无内容）",
                agent_views={}
            )

    # ────────────────────────────────────────────────
    # Prompt 构建
    # ────────────────────────────────────────────────

    def _build_prompt(self, messages: List[Message],
                     agents: Dict[str, AgentConfig]) -> str:
        """构建总结任务的 prompt"""

        history_text = self._format_messages(messages)

        agent_intro = "\n".join(
            f"- {cfg.name}（{cfg.id}）：{cfg.role}"
            for cfg in agents.values()
        )

        return f"""你是一个讨论总结分析师。请分析以下多 Agent 讨论，生成结构化总结。

## 讨论主题
（从历史发言中自行提取）

## 参与角色
{agent_intro}

## 完整讨论记录
{history_text}

---

请生成一份总结报告，要求：

1. **主要共识**：列出 2-5 条与会各方普遍认同的观点
2. **主要分歧**：列出 2-5 条各方存在争议的观点，说明各方立场差异
3. **综合建议**：基于讨论，给出一个平衡的建议或结论
4. **各方观点摘要**：每个角色单独一段（50-100字），概括该角色在讨论中的核心立场

请以 JSON 格式输出，结构如下（不要包含 markdown 代码块标记）：
{{
  "key_consensus": ["共识点1", "共识点2", ...],
  "key_disagreements": ["分歧点1", "分歧点2", ...],
  "recommendation": "综合建议内容",
  "agent_views": {{
    "agent_id1": "观点摘要1",
    "agent_id2": "观点摘要2"
  }}
}}

请确保输出的 JSON 是合法的，可直接用 json.loads() 解析。"""

    def _format_messages(self, messages: List[Message]) -> str:
        """把消息列表格式化成可读文本"""
        if not messages:
            return "（无发言记录）"

        rounds: Dict[int, List[Message]] = {}
        for msg in messages:
            rounds.setdefault(msg.round_num, []).append(msg)

        lines = []
        for rnum in sorted(rounds.keys()):
            lines.append(f"\n=== 第 {rnum} 轮 ===\n")
            for msg in rounds[rnum]:
                lines.append(f"【{msg.agent_name}】{msg.content}\n")

        return "\n".join(lines)

    # ────────────────────────────────────────────────
    # Markdown 格式化
    # ────────────────────────────────────────────────

    def format_markdown(self, summary: Summary, topic: str,
                       agents: Dict[str, AgentConfig]) -> str:
        """把 Summary 对象格式化成 Markdown 报告"""

        agent_lines = []
        for agent_id, view in summary.agent_views.items():
            name = agents.get(agent_id, AgentConfig(id=agent_id, name=agent_id, role=""))
            agent_lines.append(f"### {name.name}\n\n{view}\n")

        consensus_lines = "\n".join(
            f"{i+1}. {c}" for i, c in enumerate(summary.key_consensus)
        ) if summary.key_consensus else "（无共识）"

        disagreements_lines = "\n".join(
            f"{i+1}. {d}" for i, d in enumerate(summary.key_disagreements)
        ) if summary.key_disagreements else "（无明显分歧）"

        return f"""# 讨论总结：{topic}

**生成时间**：自动生成

---

## 📌 主要共识

{consensus_lines}

---

## ⚡ 主要分歧

{disagreements_lines}

---

## 💡 综合建议

{summary.recommendation}

---

## 👤 各方观点摘要

{"".join(agent_lines)}

---

*本报告由多 Agent 讨论系统自动生成*
"""
