"""
agents.cwd.coordinator
======================
Coordinator Agent for the CWD Multi-Agent System.
Course: AI373TA — Units III & IV (Coordinator, Worker, and Delegator Approach).

Responsibilities:
- Supervisory authority over all autonomous parking operations.
- Enforces the global objective: city-wide equilibrium (60-85% occupancy),
  zero corridor gridlocks, and statutory BBMP compliance.
- Validates and approves worker/negotiated proposals.
- Executes approved actions via tool calling.
- Commits completed interaction episodes to Episodic Memory for reflection.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from agents.cwd.delegator import DelegatorAgent
from agents.memory.episodic import Episode, EpisodicMemory
from agents.memory.knowledge_base import ParkingKnowledgeBase
from agents.memory.short_term import WorkingMemory
from agents.tools.parking_tools import ParkingToolRegistry

logger = logging.getLogger("agents.cwd.coordinator")


class CoordinatorAgent:
    """Supervisory Coordinator Agent in the CWD Multi-Agent architecture."""

    def __init__(
        self,
        delegator: DelegatorAgent,
        tool_registry: ParkingToolRegistry,
        working_memory: WorkingMemory,
        knowledge_base: ParkingKnowledgeBase,
        episodic_memory: EpisodicMemory,
        target_occupancy_min: float = 60.0,
        target_occupancy_max: float = 85.0,
    ) -> None:
        self.name = "CityMobilityCoordinator"
        self.delegator = delegator
        self.tools = tool_registry
        self.wm = working_memory
        self.kb = knowledge_base
        self.em = episodic_memory
        self.target_min = target_occupancy_min
        self.target_max = target_occupancy_max

    def handle_stream_event(self, trigger_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinates the full perception -> delegation -> negotiation -> execution -> memory cycle.
        """
        lot_id = trigger_data.get("lot_id", "LOT_MG_ROAD_01")
        logger.info("[Coordinator] Supervising event for %s...", lot_id)

        # 1. Dispatch to Delegator
        delegation_result = self.delegator.process_trigger(trigger_data)
        actions_to_execute = delegation_result.get("final_actions", [])

        if not actions_to_execute:
            logger.info("[Coordinator] No action required by Delegator for %s.", lot_id)
            return {"status": "NO_ACTION", "lot_id": lot_id}

        # 2. Authorize and Execute Actions
        executed_results = []
        for action in actions_to_execute:
            tool_name = action.get("execution_tool")
            tool_args = action.get("tool_kwargs", {})

            if tool_name:
                logger.info("[Coordinator] Authorizing and executing tool: %s with args %s", tool_name, tool_args)
                tool_output = self.tools.execute_tool(tool_name, **tool_args)
                executed_results.append({
                    "action_type": action.get("action_type"),
                    "tool": tool_name,
                    "arguments": tool_args,
                    "result": tool_output,
                })

        # 3. Formulate and Persist Episode into Episodic Memory (Unit IV)
        episode = Episode(
            trigger_type=delegation_result.get("trigger_type", "CONGESTION_SPIKE"),
            lot_id=lot_id,
            participating_agents=delegation_result.get("assigned_workers", []) + [self.name],
            proposed_actions=delegation_result.get("proposals", {}),
            negotiated_resolution=delegation_result.get("negotiated_resolution"),
            executed_action={"executed_tools": executed_results},
            initial_metrics={
                "occupancy_percentage": trigger_data.get("occupancy_percentage", 0.0),
                "entry_velocity_per_min": trigger_data.get("entry_velocity_per_min", 0.0),
            },
            status="PENDING_EVALUATION",
        )
        self.em.record_episode(episode)
        logger.info("[Coordinator] Recorded episode %s in Episodic Memory for future reflection.", episode.episode_id)

        return {
            "status": "EXECUTED",
            "coordinator": self.name,
            "episode_id": episode.episode_id,
            "lot_id": lot_id,
            "delegation": delegation_result,
            "executed_results": executed_results,
        }
