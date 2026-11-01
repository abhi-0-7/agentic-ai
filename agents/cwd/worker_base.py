"""
agents.cwd.worker_base
======================
Abstract Base Class for CWD Worker Agents.
Course: AI373TA — Unit III (Designing agents with role assignments).
"""

from __future__ import annotations

import abc
import logging
from typing import Any, Dict

from agents.tools.parking_tools import ParkingToolRegistry

logger = logging.getLogger("agents.cwd")


class WorkerBase(abc.ABC):
    """Base class for specialized Worker agents in the CWD architecture."""

    def __init__(self, name: str, role: str, tool_registry: ParkingToolRegistry) -> None:
        self.name = name
        self.role = role
        self.tools = tool_registry

    @abc.abstractmethod
    def evaluate_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reason about the assigned task, invoke tools if necessary,
        and return a formal proposal to the Delegator/Coordinator.
        """
        raise NotImplementedError

    def log_action(self, message: str) -> None:
        logger.info("[%s (%s)] %s", self.name, self.role, message)
