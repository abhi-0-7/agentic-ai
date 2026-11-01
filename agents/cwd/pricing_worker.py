"""
agents.cwd.pricing_worker
=========================
Dynamic Surge Pricing & Micro-Economic Demand Management Worker Agent.
Course: AI373TA — Units III & IV (Worker role specialization).

Specialization:
- Formulates price elasticity adjustments.
- Throttles incoming arrivals at saturated lots through statutory price surges.
- Safeguards citizen welfare by strictly enforcing BBMP municipal price ceilings.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from agents.cwd.worker_base import WorkerBase
from agents.tools.parking_tools import ParkingToolRegistry

logger = logging.getLogger("agents.cwd.pricing")


class PricingWorker(WorkerBase):
    """Specialized worker for micro-economic demand throttling and surge optimization."""

    def __init__(
        self,
        tool_registry: ParkingToolRegistry,
        base_rate_inr: float = 50.0,
        max_multiplier: float = 2.5,
    ) -> None:
        super().__init__(
            name="DynamicPricingWorker",
            role="Demand Throttling & Surge Optimization",
            tool_registry=tool_registry,
        )
        self.base_rate_inr = base_rate_inr
        self.max_multiplier = max_multiplier

    def evaluate_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        lot_id = task.get("lot_id", "LOT_MG_ROAD_01")
        occ_pct = task.get("occupancy_percentage", 80.0)
        entry_vel = task.get("entry_velocity_per_min", 0.0)

        self.log_action(f"Evaluating tariff elasticity at {lot_id} (Occupancy: {occ_pct}%)")

        # Demand-elastic pricing model:
        # Occupancy <= 75%: 1.0x (standard rate)
        # Occupancy 75-85%: 1.25x
        # Occupancy 85-92%: 1.50x
        # Occupancy > 92%: 2.0x (strong deterrent)
        if occ_pct < 75.0:
            recommended_mult = 1.0
            reason = "Occupancy below 75%; standard base tariff maintains customer flow."
        elif occ_pct < 85.0:
            recommended_mult = 1.25
            reason = "Moderate congestion detected; 1.25x surge disincentivizes non-essential parking."
        elif occ_pct < 92.0:
            recommended_mult = 1.50
            reason = "Severe congestion approaching capacity; 1.50x surge throttles incoming velocity."
        else:
            recommended_mult = min(self.max_multiplier, 2.0)
            reason = "Critical capacity threshold exceeded; 2.0x surge actively deters incoming arrivals."

        # Compute effective rate
        effective_rate = round(self.base_rate_inr * recommended_mult, 2)

        proposal = {
            "worker": self.name,
            "status": "ACTION_PROPOSED",
            "action_type": "ADJUST_DYNAMIC_TARIFF",
            "lot_id": lot_id,
            "surge_multiplier": recommended_mult,
            "effective_tariff_inr": effective_rate,
            "confidence": 0.88,
            "reason": reason,
            "execution_tool": "adjust_dynamic_tariff",
            "tool_kwargs": {
                "lot_id": lot_id,
                "surge_multiplier": recommended_mult,
                "reason": reason,
            },
        }
        self.log_action(f"Proposed surge: {recommended_mult}x ({effective_rate} INR/hr) | Reason: {reason}")
        return proposal
