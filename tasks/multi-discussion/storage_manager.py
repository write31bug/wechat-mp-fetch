# storage_manager.py
"""
多 Agent 讨论系统 · 存储管理器
负责：session 目录创建、文件读写、manifest 管理
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


BASE_PATH = Path("~/.openclaw/discussions").expanduser()


def generate_session_id(topic: str) -> str:
    """生成唯一 session ID：{日期}_{topic前20字符}"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    slug = slugify(topic)[:20]
    return f"{date_str}_{slug}"


def slugify(text: str) -> str:
    """把任意字符串转成安全的文件名（过滤半角和全角特殊字符）"""
    text = re.sub(r'[\\/:*?"<>|？「」【】『』]', '', text)
    return text.replace(" ", "_")[:30]


class SessionPaths:
    """一个讨论 session 的所有路径"""
    def __init__(self, base: Path, manifest: Path, history_json: Path,
                 summary, contributions_dir: Path):
        self.base = base
        self.manifest = manifest
        self.history_json = history_json
        self.summary = summary
        self.contributions_dir = contributions_dir


class StorageManager:
    """存储管理器"""

    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or BASE_PATH
        self.base_path.mkdir(parents=True, exist_ok=True)

    # ────────────────────────────────────────────────
    # Session 生命周期
    # ────────────────────────────────────────────────

    def init_session(self, topic: str, agents: List[str],
                    rounds: int = 3, config: Dict[str, Any] = None) -> SessionPaths:
        """
        创建讨论 session 目录结构。
        agents=N，不固定。
        """
        session_id = generate_session_id(topic)
        base = self.base_path / session_id
        base.mkdir(parents=True, exist_ok=True)

        # contributions/{agent_id}/ 每个 agent 一个子目录
        contributions_dir = base / "contributions"
        contributions_dir.mkdir(exist_ok=True)
        for agent in agents:
            agent_dir = contributions_dir / agent
            agent_dir.mkdir(exist_ok=True)

        # manifest.json
        manifest_path = base / "manifest.json"
        manifest_data = {
            "session_id": session_id,
            "topic": topic,
            "agents": agents,
            "rounds": rounds,
            "current_round": 0,
            "status": "PENDING",
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            "config": config or {}
        }
        self._write_json(manifest_path, manifest_data)

        # history.json（空的，等待填充）
        history_path = base / "history.json"
        self._write_json(history_path, {"rounds": []})

        # summary.md（空的，等待生成）
        summary_path = base / "summary.md"
        summary_path.write_text("", encoding="utf-8")

        return SessionPaths(
            base=base,
            manifest=manifest_path,
            history_json=history_path,
            summary=summary_path,
            contributions_dir=contributions_dir
        )

    def load_session(self, session_id: str) -> SessionPaths:
        """根据 session_id 加载已有 session"""
        base = self.base_path / session_id
        if not base.exists():
            raise FileNotFoundError(f"Session 不存在: {session_id}")
        return SessionPaths(
            base=base,
            manifest=base / "manifest.json",
            history_json=base / "history.json",
            summary=base / "summary.md",
            contributions_dir=base / "contributions"
        )

    # ────────────────────────────────────────────────
    # Manifest 操作
    # ────────────────────────────────────────────────

    def read_manifest(self, paths: SessionPaths) -> Dict[str, Any]:
        return self._read_json(paths.manifest)

    def update_manifest(self, paths: SessionPaths, updates: Dict[str, Any]):
        """部分更新 manifest"""
        data = self.read_manifest(paths)
        data.update(updates)
        data["updated"] = datetime.now().isoformat()
        self._write_json(paths.manifest, data)

    def update_manifest_round(self, paths: SessionPaths, round_num: int):
        """更新当前轮次（每轮结束后调用）"""
        self.update_manifest(paths, {"current_round": round_num})

    def update_manifest_status(self, paths: SessionPaths, status: str):
        """更新讨论状态：PENDING → IN_PROGRESS → COMPLETED / FAILED"""
        self.update_manifest(paths, {"status": status})

    # ────────────────────────────────────────────────
    # 发言文件读写
    # ────────────────────────────────────────────────

    def save_contribution(self, paths: SessionPaths, agent_id: str,
                         round_num: int, content: str):
        """
        保存单个 agent 的单轮发言。
        文件路径：contributions/{agent_id}/round{round_num}.md
        """
        agent_dir = paths.contributions_dir / agent_id
        filepath = agent_dir / f"round{round_num}.md"
        filepath.write_text(content, encoding="utf-8")

    def load_contribution(self, paths: SessionPaths, agent_id: str,
                         round_num: int) -> str:
        """读取单个 agent 的单轮发言"""
        filepath = paths.contributions_dir / agent_id / f"round{round_num}.md"
        return filepath.read_text(encoding="utf-8")

    def load_all_contributions(self, paths: SessionPaths,
                               agents: List[str], rounds: int) -> List[Dict[str, Any]]:
        """
        加载所有发言，按时间顺序排列。
        返回 List[Message]，Message = {agent, round, content, timestamp}
        """
        messages = []
        for round_num in range(1, rounds + 1):
            for agent in agents:
                try:
                    content = self.load_contribution(paths, agent, round_num)
                    filepath = paths.contributions_dir / agent / f"round{round_num}.md"
                    mtime = datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
                    messages.append({
                        "agent": agent,
                        "round": round_num,
                        "content": content,
                        "timestamp": mtime
                    })
                except FileNotFoundError:
                    pass
        return messages

    # ────────────────────────────────────────────────
    # History JSON 操作
    # ────────────────────────────────────────────────

    def append_history(self, paths: SessionPaths, round_num: int,
                       messages: List[Dict[str, Any]]):
        """追加一轮发言到 history.json"""
        data = self._read_json(paths.history_json)
        data["rounds"].append({
            "round": round_num,
            "messages": messages
        })
        self._write_json(paths.history_json, data)

    def read_history(self, paths: SessionPaths) -> Dict[str, Any]:
        return self._read_json(paths.history_json)

    # ────────────────────────────────────────────────
    # 总结写入
    # ────────────────────────────────────────────────

    def write_summary(self, paths: SessionPaths, summary_content: str):
        """写入总结报告"""
        paths.summary.write_text(summary_content, encoding="utf-8")
        self.update_manifest(paths, {"summary_path": str(paths.summary)})

    # ────────────────────────────────────────────────
    # 工具方法
    # ────────────────────────────────────────────────

    @staticmethod
    def _read_json(path: Path) -> Dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _write_json(path: Path, data: Dict[str, Any]):
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
