# run_discussion.py
"""
多 Agent 讨论系统 · 入口脚本
由 LLM 调用，负责调度 orchestrator 并通过 sessions_spawn 调用各 agent

使用方式（从 LLM 上下文调用）：
  python run_discussion.py --topic "xxx" --agents "dev,writer,finance" --rounds 2
"""

import asyncio
import argparse
import json
import sys
import os
from pathlib import Path

# 把 multi-discussion 目录加入 path
sys.path.insert(0, str(Path(__file__).parent))

from storage_manager import StorageManager
from context_builder import ContextBuilder, AgentConfig
from summary_generator import SummaryGenerator, Summary


def parse_args():
    parser = argparse.ArgumentParser(description="多 Agent 讨论系统")
    parser.add_argument("--topic", required=True, help="讨论主题")
    parser.add_argument("--agents", required=True, help="agent ID 列表，逗号分隔")
    parser.add_argument("--rounds", type=int, default=3, help="讨论轮次")
    parser.add_argument("--output", default=None, help="结果输出路径")
    return parser.parse_args()


def load_agent_configs(agent_ids: list) -> dict:
    """
    根据 agent_id 加载配置。
    实际从 config.yaml 读取，这里做简化映射。
    """
    configs = {
        "dev": AgentConfig(
            id="dev", name="开发助手",
            role="你是一个技术架构师，擅长评估系统设计的可行性和工程实现质量",
            personality="严谨、直接、关注架构"
        ),
        "writer": AgentConfig(
            id="writer", name="写作助手",
            role="你是一个内容创作专家，关注系统的易用性和文档完整性",
            personality="务实、创意、关注读者体验"
        ),
        "finance": AgentConfig(
            id="finance", name="财务助手",
            role="你是一个分析师，关注系统的实用价值和投入产出比",
            personality="稳健、数据驱动、谨慎"
        ),
        "community": AgentConfig(
            id="community", name="社区助手",
            role="你是一个社区运营专家，关注系统的协作效率和可扩展性",
            personality="热情、有边界、务实"
        ),
    }
    result = {}
    for aid in agent_ids:
        if aid in configs:
            result[aid] = configs[aid]
    return result


async def run_discussion(topic: str, agent_ids: list, rounds: int, output_path: str = None):
    """运行讨论（需要 LLM 调用 sessions_spawn）"""

    # 1. 初始化 storage
    sm = StorageManager()
    agents_config = load_agent_configs(agent_ids)
    agents = list(agents_config.values())

    paths = sm.init_session(
        topic=topic,
        agents=agent_ids,
        rounds=rounds
    )
    sm.update_manifest_status(paths, "IN_PROGRESS")

    print(f"[run_discussion] Session: {paths.base.name}", flush=True)
    print(f"[run_discussion] Topic: {topic}", flush=True)
    print(f"[run_discussion] Agents: {agent_ids}", flush=True)
    print(f"[run_discussion] Rounds: {rounds}", flush=True)

    cb = ContextBuilder(topic)
    all_messages = []

    # 2. N 轮循环
    for round_num in range(1, rounds + 1):
        print(f"[Round {round_num}/{rounds}]", flush=True)
        round_previous = []

        for agent in agents:
            # 构建上下文
            context = cb.build(
                round_num=round_num,
                total_rounds=rounds,
                agent=agent,
                history=all_messages,
                this_round_previous=round_previous
            )

            # 输出 spawn 指令（供 LLM 执行）
            spawn_cmd = {
                "tool": "sessions_spawn",
                "task": f"你是 {agent.name}。\n\n{context}",
                "model": agent.model or "gpt-4o",
                "runtime": "subagent",
                "mode": "run",
                "cleanup": "delete",
            }
            print(f"[SPAWN]", json.dumps(spawn_cmd, ensure_ascii=False), flush=True)

            # 等待 LLM 执行并返回结果（通过 stdin 读入）
            # 实际由调用方（LLM）填入结果
            result = await read_stdin_result()
            content = result.get("content", "")

            # 记录
            from context_builder import Message
            from datetime import datetime
            msg = Message(
                agent_id=agent.id,
                agent_name=agent.name,
                round_num=round_num,
                content=content,
                timestamp=datetime.now().isoformat()
            )
            all_messages.append(msg)
            round_previous.append(msg)

            # 保存
            sm.save_contribution(paths, agent.id, round_num, content)

        # checkpoint
        sm.append_history(paths, round_num, [
            {"agent": m.agent_id, "content": m.content, "timestamp": m.timestamp}
            for m in round_previous
        ])
        sm.update_manifest_round(paths, round_num)

    # 3. 生成总结 prompt
    sg = SummaryGenerator()
    summary_prompt = sg.generate(all_messages, {a.id: a for a in agents})
    summary_spawn = {
        "tool": "sessions_spawn",
        "task": summary_prompt,
        "model": "gpt-4o",
        "runtime": "subagent",
        "mode": "run",
        "cleanup": "delete",
    }
    print(f"[SUMMARY]", json.dumps(summary_spawn, env, ensure_ascii=False), flush=True)

    summary_result = await read_stdin_result()
    summary_content = summary_result.get("content", "")

    try:
        summary_obj = sg.parse_result(summary_content, {a.id: a for a in agents})
    except Exception:
        from dataclasses import dataclass
        summary_obj = Summary(
            key_consensus=["（总结生成失败）"],
            key_disagreements=[],
            recommendation=summary_content[:500],
            agent_views={}
        )

    md = sg.format_markdown(summary_obj, topic, {a.id: a for a in agents})
    sm.write_summary(paths, md)
    sm.update_manifest_status(paths, "COMPLETED")

    result_data = {
        "session_id": paths.base.name,
        "summary": str(paths.summary),
        "history": str(paths.history_json),
    }
    print(f"[DONE]", json.dumps(result_data, ensure_ascii=False), flush=True)
    return result_data


async def read_stdin_result() -> dict:
    """从 stdin 读取 LLM 执行结果（JSON 格式）"""
    import sys
    line = sys.stdin.readline()
    if not line:
        return {"content": ""}
    try:
        return json.loads(line.strip())
    except json.JSONDecodeError:
        return {"content": line.strip()}


if __name__ == "__main__":
    args = parse_args()
    agent_ids = [a.strip() for a in args.agents.split(",")]
    asyncio.run(run_discussion(args.topic, agent_ids, args.rounds, args.output))
