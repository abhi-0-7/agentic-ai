"""
agents.cwd.delegator
====================
Delegator Agent for the CWD Multi-Agent System.
Course: AI373TA — Units III & IV (Coordinator, Worker, and Delegator Approach).

Responsibilities:
- Ingests streaming telemetry triggers and threshold violations.
- Decomposes high-level operational alerts into specialized sub-tasks.
- Dispatches sub-tasks to designated Worker agents based on domain capability.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from agents.cwd.diagnostic_worker import DiagnosticWorker
from agents.cwd.negotiator import AgentNegotiator
from agents.cwd.pricing_worker import PricingWorker
from agents.cwd.traffic_worker import TrafficWorker

logger = logging.getLogger("agents.cwd.delegator")


class DelegatorAgent:
    """Delegator agent responsible for task decomposition and worker dispatch."""

    def __init__(
        self,
        traffic_worker: TrafficWorker,
        pricing_worker: PricingWorker,
        diagnostic_worker: DiagnosticWorker,
        negotiator: AgentNegotiator,
    ) -> None:
        self.name = "StreamTelemetryDelegator"
        self.traffic_worker = traffic_worker
        self.pricing_worker = pricing_worker
        self.diagnostic_worker = diagnostic_worker
        self.negotiator = negotiator

    def process_trigger(self, trigger_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decomposes streaming trigger into tasks and delegates to workers.
        """
        trigger_type = trigger_data.get("trigger_type", "CONGESTION_SPIKE")
        lot_id = trigger_data.get("lot_id", "LOT_MG_ROAD_01")
        occ_pct = trigger_data.get("occupancy_percentage", 80.0)

        logger.info("[Delegator] Ingested trigger '%s' for lot %s (Occupancy: %.1f%%)",
                    trigger_type, lot_id, occ_pct)

        # 1. Diagnostic / Sensor Fault Trigger
        if trigger_type in ("SENSOR_FAULT", "DLQ_ANOMALY"):
            diag_proposal = self.diagnostic_worker.evaluate_task(trigger_data)
            return {
                "delegator": self.name,
                "trigger_type": trigger_type,
                "lot_id": lot_id,
                "workflow": "SEQUENTIAL_DIAGNOSTIC",
                "assigned_workers": [self.diagnostic_worker.name],
                "proposals": {"diagnostic": diag_proposal},
                "final_actions": [diag_proposal] if diag_proposal.get("status") == "ACTION_PROPOSED" else [],
                "negotiation_required": False,
            }

        # 2. Critical Gridlock Trigger (> 90% Occupancy) -> Multi-Agent Joint Negotiation
        if occ_pct >= 90.0 or trigger_type == "CRITICAL_GRIDLOCK":
            logger.info("[Delegator] Critical condition at %s (%.1f%% >= 90%%). Initiating joint Traffic & Pricing collaboration.",
                        lot_id, occ_pct)
            traffic_prop = self.traffic_worker.evaluate_task(trigger_data)
            pricing_prop = self.pricing_worker.evaluate_task(trigger_data)

            # Resolve conflict via Negotiator
            resolution = self.negotiator.resolve_conflict(traffic_prop, pricing_prop, trigger_data)
            return {
                "delegator": self.name,
                "trigger_type": "CRITICAL_GRIDLOCK",
                "lot_id": lot_id,
                "workflow": "PARALLEL_COLLABORATIVE_NEGOTIATION",
                "assigned_workers": [self.traffic_worker.name, self.pricing_worker.name],
                "proposals": {"traffic": traffic_prop, "pricing": pricing_prop},
                "negotiated_resolution": resolution,
                "final_actions": resolution.get("actions", []),
                "negotiation_required": True,
            }

        # 3. High Congestion (85% - 90%) -> Delegate to Traffic Worker
        if occ_pct >= 85.0 or trigger_type == "CONGESTION_SPIKE":
            traffic_prop = self.traffic_worker.evaluate_task(trigger_data)
            actions = [traffic_prop] if traffic_prop.get("status") == "ACTION_PROPOSED" else []
            return {
                "delegator": self.name,
                "trigger_type": "CONGESTION_SPIKE",
                "lot_id": lot_id,
                "workflow": "DELEGATED_TRAFFIC_REBALANCE",
                "assigned_workers": [self.traffic_worker.name],
                "proposals": {"traffic": traffic_prop},
                "final_actions": actions,
                "negotiation_required": False,
            }

        # 4. Surge Demand (80% - 85%) -> Delegate to Pricing Worker
        if occ_pct >= 80.0 or trigger_type == "SURGE_DEMAND":
            pricing_prop = self.pricing_worker.evaluate_task(trigger_data)
            actions = [pricing_prop] if pricing_prop.get("status") == "ACTION_PROPOSED" else []
            return {
                "delegator": self.name,
                "trigger_type": "SURGE_DEMAND",
                "lot_id": lot_id,
                "workflow": "DELEGATED_SURGE_PRICING",
                "assigned_workers": [self.pricing_worker.name],
                "proposals": {"pricing": pricing_prop},
                "final_actions": actions,
                "negotiation_required": False,
            }

        return {
            "delegator": self.name,
            "trigger_type": "NORMAL_TELEMETRY",
            "lot_id": lot_id,
            "workflow": "NO_ACTION_REQUIRED",
            "assigned_workers": [],
            "proposals": {},
            "final_actions": [],
            "negotiation_required": False,
        }
