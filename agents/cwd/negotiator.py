"""
agents.cwd.negotiator
=====================
Inter-Agent Negotiation and Conflict Resolution.
Course: AI373TA — Unit III (Negotiation and conflict resolution in Multi-Agent Systems).

Academic Principle:
When multiple worker agents with disparate domain objectives (e.g. Traffic Mobility
vs. Revenue/Demand Optimization) propose conflicting actions for the same operational
corridor, the Negotiator applies a Pareto-optimal mediation protocol to synthesize
a unified, non-conflicting intervention plan.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("agents.cwd.negotiator")


class AgentNegotiator:
    """Arbitrates and negotiates consensus between competing worker proposals."""

    def __init__(self, strategy: str = "pareto_optimal") -> None:
        self.strategy = strategy

    def resolve_conflict(
        self,
        traffic_proposal: Optional[Dict[str, Any]],
        pricing_proposal: Optional[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Negotiate a Pareto-optimal consensus between TrafficWorker and PricingWorker.

        Conflict Pattern:
        - TrafficWorker wants to reroute 30-35% of traffic to a neighboring lot.
        - PricingWorker wants to apply a heavy surge at the congested lot.
        - If surge is too high without incentives at the destination lot, drivers
          disregard reroute signage and spill into residential streets.

        Negotiated Compromise:
        1. Moderate the origin lot's surge to 1.35x (mild deterrent).
        2. Enact TrafficWorker's rerouting diversion to destination lot.
        3. Protect destination lot tariff at 1.0x (or apply a 10% discount)
           to serve as an explicit incentive for diverted commuters.
        """
        lot_id = context.get("lot_id", "LOT_MG_ROAD_01")
        occ_pct = context.get("occupancy_percentage", 90.0)

        logger.info("[Negotiation] Mediating between TrafficWorker and PricingWorker for %s (Occupancy: %.1f%%)",
                    lot_id, occ_pct)

        # If only one worker proposed, no conflict exists
        if traffic_proposal and not pricing_proposal:
            return {
                "status": "CONSENSUS_REACHED",
                "negotiation_rounds": 1,
                "resolution_strategy": "UNCONTESTED_TRAFFIC",
                "actions": [traffic_proposal],
                "explanation": "Pricing worker had no objection; traffic proposal adopted in full.",
            }

        if pricing_proposal and not traffic_proposal:
            return {
                "status": "CONSENSUS_REACHED",
                "negotiation_rounds": 1,
                "resolution_strategy": "UNCONTESTED_PRICING",
                "actions": [pricing_proposal],
                "explanation": "Traffic worker had no objection; pricing proposal adopted in full.",
            }

        # Both proposed -> Negotiate Pareto-Optimal Compromise
        target_lot = traffic_proposal.get("target_lot", "LOT_INDIRANAGAR_01")
        divert_pct = traffic_proposal.get("divert_percentage", 25.0)

        raw_surge = pricing_proposal.get("surge_multiplier", 1.5)
        # Compromise: Moderate the surge to prevent panic spillover
        negotiated_surge = round(min(raw_surge, 1.35), 2)

        negotiated_traffic = {
            **traffic_proposal,
            "divert_percentage": divert_pct,
            "negotiated": True,
            "negotiation_note": f"Synchronized with {negotiated_surge}x tariff at origin.",
        }

        negotiated_pricing = {
            **pricing_proposal,
            "surge_multiplier": negotiated_surge,
            "negotiated": True,
            "negotiation_note": f"Moderated from {raw_surge}x to {negotiated_surge}x to allow VMS reroute adoption.",
            "tool_kwargs": {
                **pricing_proposal.get("tool_kwargs", {}),
                "surge_multiplier": negotiated_surge,
                "reason": f"Negotiated consensus: moderated surge ({negotiated_surge}x) combined with traffic reroute to {target_lot}.",
            },
        }

        # Destination incentive action
        destination_incentive = {
            "worker": "NegotiatedConsensus",
            "action_type": "ADJUST_DYNAMIC_TARIFF",
            "lot_id": target_lot,
            "surge_multiplier": 1.0,
            "effective_tariff_inr": 50.0,
            "confidence": 0.95,
            "reason": f"Off-peak destination incentive for commuters diverted from {lot_id}.",
            "execution_tool": "adjust_dynamic_tariff",
            "tool_kwargs": {
                "lot_id": target_lot,
                "surge_multiplier": 1.0,
                "reason": f"Commuter incentive rate for drivers diverted from {lot_id}.",
            },
        }

        logger.info("[Negotiation] Consensus reached: Surge capped at %.2fx; Traffic diverted %.1f%% to %s; Target lot held at 1.0x.",
                    negotiated_surge, divert_pct, target_lot)

        return {
            "status": "CONSENSUS_REACHED",
            "negotiation_rounds": 2,
            "resolution_strategy": "PARETO_OPTIMAL_MOBILITY_ECONOMIC_EQUILIBRIUM",
            "actions": [negotiated_pricing, negotiated_traffic, destination_incentive],
            "explanation": (
                f"Multi-agent consensus resolved trade-off: {lot_id} surge moderated to {negotiated_surge}x "
                f"to throttle arrivals, while {divert_pct:.0f}% traffic is rerouted to {target_lot} with protected base rates."
            ),
        }
