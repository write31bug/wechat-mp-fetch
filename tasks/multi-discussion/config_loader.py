# config_loader.py
"""
从 config.yaml 加载预设角色包和配置
"""

import yaml
from pathlib import Path
from typing import List, Optional

from context_builder import AgentConfig


# config.yaml 路径（默认）
DEFAULT_CONFIG_PATH = Path(__file__).parent / "config.yaml"


def load_config(config_path: Optional[str] = None) -> dict:
    """加载 config.yaml"""
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    if not path.exists():
        raise FileNotFoundError(f"配置文件不存在: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_preset(preset_name: str, config_path: Optional[str] = None) -> List[AgentConfig]:
    """
    加载预定义角色包，返回 AgentConfig 列表。

    用法：
        # 加载投资分析讨论角色
        agents = get_preset("investment_debate")
        for a in agents:
            print(a.name)

        # 加载产品决策讨论角色
        agents = get_preset("product_debate")

    可用预设：
        - investment_debate：多头分析师、空头分析师、客观分析师
        - product_debate：产品经理、技术负责人、运营负责人
    """
    config = load_config(config_path)
    presets = config.get("presets", {})

    if preset_name not in presets:
        available = list(presets.keys())
        raise ValueError(
            f"未知的预设角色包: {preset_name}，可用: {available}"
        )

    raw_agents = presets[preset_name]
    return [_parse_agent(a) for a in raw_agents]


def get_default_agents(config_path: Optional[str] = None) -> List[AgentConfig]:
    """
    加载默认角色（optimist / skeptic / neutral）。
    """
    config = load_config(config_path)
    raw_agents = config.get("agents", [])
    return [_parse_agent(a) for a in raw_agents]


def _parse_agent(raw: dict) -> AgentConfig:
    """把 dict 转成 AgentConfig"""
    return AgentConfig(
        id=raw["id"],
        name=raw["name"],
        role=raw["role"],
        personality=raw.get("personality", ""),
        model=raw.get("model", ""),
        temperature=raw.get("temperature", 0.7),
    )
