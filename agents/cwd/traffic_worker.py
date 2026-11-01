"""
agents.cwd.traffic_worker
=========================
Traffic Rebalancing & Corridor Mobility Worker Agent.
Course: AI373TA — Units III & IV (Worker role specialization).

Specialization:
- Spatial corridor congestion relief.
- Identifies optimal alternative parking facilities using topological graphs.
- Dispatches Variable Message Signs (VMS) rerouting guidance.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from agents.cwd.worker_base import WorkerBase
from agents.tools.parking_tools import ParkingToolRegistry

logger = logging.getLogger("agents.cwd.traffic")


class TrafficWorker(WorkerBase):
    """Specialized worker for spatial traffic rerouting and corridor balancing."""

    def __init__(self, tool_registry: ParkingToolRegistry, max_divert_pct: float = 35.0) -> None:
        super().__init__(
            name="TrafficRebalancingWorker",
            role="Spatial Traffic Rebalancing",
            tool_registry=tool_registry,
        )
        self.max_divert_pct = max_divert_pct

    def evaluate_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        lot_id = task.get("lot_id", "LOT_MG_ROAD_01")
        occ_pct = task.get("occupancy_percentage", 85.0)
        entry_vel = task.get("entry_velocity_per_min", 0.0)

        self.log_action(f"Evaluating traffic congestion at {lot_id} (Occupancy: {occ_pct}%, Velocity: {entry_vel}/min)")

        # 1. Query spatial neighbors with spare capacity
        neighbors_res = self.tools.execute_tool("get_spatial_neighbors", lot_id=lot_id, max_distance_km=8.0)
        neighbors = neighbors_res.get("neighbors", [])

        # Filter neighbors with low occupancy (< 75%) and positive availability (> 15 slots)
        viable_candidates = [
            n for n in neighbors
            if n.get("current_occupancy_pct", 100.0) < 75.0 and n.get("available_slots", 0) > 15
        ]

        if not viable_candidates:
            self.log_action(f"No viable alternative lots found within 8 km with spare capacity for {lot_id}.")
            return {
                "worker": self.name,
                "status": "NO_VIABLE_TARGET",
                "proposed_action": None,
                "confidence": 0.3,
                "reason": "All neighboring parking facilities are saturated or beyond acceptable transit distance.",
            }

        # Select best candidate (lowest occupancy weighted by proximity)
        best_target = min(viable_candidates, key=lambda x: (x["current_occupancy_pct"] * 0.6 + x["distance_km"] * 5.0))
        target_lot = best_target["lot_id"]
        target_dist = best_target["distance_km"]
        target_time = best_target["transit_time_mins"]

        # Calculate recommended diversion percentage
        # Higher occupancy -> divert higher proportion (up to max_divert_pct)
        divert_pct = min(self.max_divert_pct, round(max(10.0, (occ_pct - 70.0) * 1.2), 1))

        proposal = {
            "worker": self.name,
            "status": "ACTION_PROPOSED",
            "action_type": "DISPATCH_REROUTE_GUIDANCE",
            "source_lot": lot_id,
            "target_lot": target_lot,
            "divert_percentage": divert_pct,
            "distance_km": target_dist,
            "transit_time_mins": target_time,
            "confidence": 0.92,
            "reason": f"Divert {divert_pct}% traffic to {best_target['name']} ({target_dist} km away) to prevent gridlock.",
            "execution_tool": "dispatch_reroute_guidance",
            "tool_kwargs": {
                "source_lot": lot_id,
                "target_lot": target_lot,
                "divert_percentage": divert_pct,
                "reason": f"Alleviate {occ_pct}% occupancy at {lot_id}.",
            },
        }
        self.log_action(f"Proposed reroute: {proposal['reason']}")
        return proposal
