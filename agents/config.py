"""
agents/config.py
================
Configuration loader for the Smart Parking Agentic AI subsystem.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import yaml


def get_project_root() -> Path:
    """Return the absolute path to the project root directory."""
    return Path(__file__).resolve().parent.parent


def load_agent_config(config_path: str | Path | None = None) -> Dict[str, Any]:
    """Load configuration from config/agents.yaml with fallback defaults."""
    if config_path is None:
        config_path = get_project_root() / "config" / "agents.yaml"
    
    path_obj = Path(config_path)
    if not path_obj.is_file():
        return {}

    with open(path_obj, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    
    return data.get("agents", {})
