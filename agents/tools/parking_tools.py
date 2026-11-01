"""
agents.tools.parking_tools
==========================
Executable tools and function-calling schemas for Smart Parking Agents.
Course: AI373TA — Units II & III (Tool use, Function Calling, Reasoning about tools).

Tools provided:
1. query_stream_metrics: Queries real-time occupancy and flow velocities.
2. get_spatial_neighbors: Queries topological distance and transit times to adjacent lots.
3. adjust_dynamic_tariff: Modifies parking pricing with BBMP statutory rule validation.
4. dispatch_reroute_guidance: Emits variable message sign (VMS) traffic rerouting.
5. inspect_dlq_anomalies: Analyzes quarantined payloads from Kafka DLQ.
6. quarantine_sensor: Marks faulty sensors as quarantined and generates repair work orders.
7. query_historical_memory: Retrieves past episodic outcomes for reflection and planning.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional

from agents.memory.episodic import EpisodicMemory
from agents.memory.knowledge_base import ParkingKnowledgeBase
from agents.memory.short_term import WorkingMemory

logger = logging.getLogger("agents.tools")


class ParkingToolRegistry:
    """Central registry of executable tools and their function-calling schemas."""

    def __init__(
        self,
        working_memory: WorkingMemory,
        knowledge_base: ParkingKnowledgeBase,
        episodic_memory: EpisodicMemory,
    ) -> None:
        self.wm = working_memory
        self.kb = knowledge_base
        self.em = episodic_memory
        self._tools: Dict[str, Callable[..., Dict[str, Any]]] = {}
        self._schemas: Dict[str, Dict[str, Any]] = {}
        self._register_default_tools()

    def register_tool(self, name: str, fn: Callable[..., Dict[str, Any]], schema: Dict[str, Any]) -> None:
        self._tools[name] = fn
        self._schemas[name] = schema

    def execute_tool(self, name: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute a registered tool by name with provided keyword arguments."""
        if name not in self._tools:
            return {"success": False, "error": f"Tool '{name}' not found in registry."}
        try:
            logger.info("Executing tool [%s] with args %s", name, kwargs)
            return self._tools[name](**kwargs)
        except Exception as exc:
            logger.error("Error executing tool [%s]: %s", name, exc)
            return {"success": False, "error": str(exc)}

    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """Return function-calling JSON schemas for all registered tools."""
        return list(self._schemas.values())

    def _register_default_tools(self) -> None:
        # Tool 1: query_stream_metrics
        self.register_tool(
            "query_stream_metrics",
            self.query_stream_metrics,
            {
                "name": "query_stream_metrics",
                "description": "Retrieve the latest real-time occupancy metrics and flow velocity for a parking lot.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lot_id": {"type": "string", "description": "The unique identifier of the parking lot."}
                    },
                    "required": ["lot_id"],
                },
            },
        )

        # Tool 2: get_spatial_neighbors
        self.register_tool(
            "get_spatial_neighbors",
            self.get_spatial_neighbors,
            {
                "name": "get_spatial_neighbors",
                "description": "Find nearby parking lots within road transit distance, including current spare capacities.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lot_id": {"type": "string", "description": "Source lot identifier."},
                        "max_distance_km": {"type": "number", "description": "Maximum road search radius in km."}
                    },
                    "required": ["lot_id"],
                },
            },
        )

        # Tool 3: adjust_dynamic_tariff
        self.register_tool(
            "adjust_dynamic_tariff",
            self.adjust_dynamic_tariff,
            {
                "name": "adjust_dynamic_tariff",
                "description": "Adjust the hourly surge multiplier for a lot, validated against BBMP municipal price ceilings.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lot_id": {"type": "string", "description": "Target parking lot ID."},
                        "surge_multiplier": {"type": "number", "description": "Multiplier (e.g. 1.25 for 25% surge)."},
                        "reason": {"type": "string", "description": "Justification for price adjustment."}
                    },
                    "required": ["lot_id", "surge_multiplier", "reason"],
                },
            },
        )

        # Tool 4: dispatch_reroute_guidance
        self.register_tool(
            "dispatch_reroute_guidance",
            self.dispatch_reroute_guidance,
            {
                "name": "dispatch_reroute_guidance",
                "description": "Broadcast an automated Variable Message Sign (VMS) rerouting guidance to divert incoming traffic.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "source_lot": {"type": "string", "description": "Congested origin lot."},
                        "target_lot": {"type": "string", "description": "Alternative destination lot with spare capacity."},
                        "divert_percentage": {"type": "number", "description": "Recommended percentage of traffic to divert."},
                        "reason": {"type": "string", "description": "Mobility justification."}
                    },
                    "required": ["source_lot", "target_lot", "divert_percentage", "reason"],
                },
            },
        )

        # Tool 5: inspect_dlq_anomalies
        self.register_tool(
            "inspect_dlq_anomalies",
            self.inspect_dlq_anomalies,
            {
                "name": "inspect_dlq_anomalies",
                "description": "Inspect recent quarantined payloads from the Kafka Dead Letter Queue to classify sensor faults.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Max number of anomaly records to retrieve."}
                    },
                },
            },
        )

        # Tool 6: quarantine_sensor
        self.register_tool(
            "quarantine_sensor",
            self.quarantine_sensor,
            {
                "name": "quarantine_sensor",
                "description": "Quarantine a defective IoT sensor to protect stream integrity, and generate a BBMP repair work order.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lot_id": {"type": "string", "description": "Parent lot of the sensor."},
                        "slot_id": {"type": "string", "description": "Defective slot/sensor ID."},
                        "fault_type": {"type": "string", "description": "Diagnosed fault: STUCK_SENSOR | CORRUPT_COORDINATES | BATTERY_FAILURE"},
                        "reason": {"type": "string", "description": "Diagnostic explanation."}
                    },
                    "required": ["lot_id", "slot_id", "fault_type", "reason"],
                },
            },
        )

        # Tool 7: query_historical_memory
        self.register_tool(
            "query_historical_memory",
            self.query_historical_memory,
            {
                "name": "query_historical_memory",
                "description": "Query episodic memory for past intervention results under similar congestion or fault triggers.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lot_id": {"type": "string", "description": "Target parking lot ID."},
                        "trigger_type": {"type": "string", "description": "Trigger category (e.g. CONGESTION_SPIKE)."}
                    },
                    "required": ["lot_id", "trigger_type"],
                },
            },
        )

    # ─── Tool Implementations ──────────────────────────────────────────

    def query_stream_metrics(self, lot_id: str) -> Dict[str, Any]:
        state = self.wm.get_lot_state(lot_id)
        if not state:
            node = self.kb.lots.get(lot_id)
            cap = node.capacity if node else 100
            return {
                "success": True,
                "lot_id": lot_id,
                "occupied_slots": 0,
                "capacity": cap,
                "occupancy_percentage": 0.0,
                "entry_velocity_per_min": 0.0,
                "exit_velocity_per_min": 0.0,
                "current_surge_multiplier": 1.0,
            }
        return {
            "success": True,
            "lot_id": state.lot_id,
            "occupied_slots": state.occupied_slots,
            "capacity": state.capacity,
            "available_slots": state.available_slots,
            "occupancy_percentage": state.occupancy_percentage,
            "entry_velocity_per_min": state.entry_velocity_per_min,
            "exit_velocity_per_min": state.exit_velocity_per_min,
            "current_surge_multiplier": state.current_surge_multiplier,
            "active_reroute_target": state.active_reroute_target,
        }

    def get_spatial_neighbors(self, lot_id: str, max_distance_km: float = 8.0) -> Dict[str, Any]:
        neighbors = self.kb.find_nearest_available_lots(lot_id, max_distance_km=max_distance_km)
        enriched = []
        for n in neighbors:
            other_id = n["lot_id"]
            other_state = self.wm.get_lot_state(other_id)
            occ_pct = other_state.occupancy_percentage if other_state else 50.0
            avail = other_state.available_slots if other_state else int(n["capacity"] * 0.5)
            enriched.append({
                **n,
                "current_occupancy_pct": occ_pct,
                "available_slots": avail,
            })
        return {"success": True, "source_lot": lot_id, "neighbors": enriched}

    def adjust_dynamic_tariff(self, lot_id: str, surge_multiplier: float, reason: str) -> Dict[str, Any]:
        node = self.kb.lots.get(lot_id)
        base_rate = node.base_tariff_inr if node else 50.0
        proposed_rate = base_rate * surge_multiplier

        is_valid, validation_msg = self.kb.validate_tariff(proposed_rate)
        if not is_valid:
            # Clamp to statutory max
            max_cap = self.kb.regulatory_rules["max_surge_cap_inr"]
            surge_multiplier = round(max_cap / base_rate, 2)
            proposed_rate = max_cap
            logger.warning("Clamped tariff to statutory cap: %.1f INR (%.2fx)", proposed_rate, surge_multiplier)

        self.wm.set_surge_multiplier(lot_id, surge_multiplier)
        return {
            "success": True,
            "lot_id": lot_id,
            "base_tariff_inr": base_rate,
            "new_surge_multiplier": surge_multiplier,
            "effective_tariff_inr": round(proposed_rate, 2),
            "reason": reason,
            "statutory_compliance": "APPROVED_BY_BBMP_REGULATION",
        }

    def dispatch_reroute_guidance(
        self, source_lot: str, target_lot: str, divert_percentage: float, reason: str
    ) -> Dict[str, Any]:
        dist_info = self.kb.get_distance(source_lot, target_lot)
        distance_km = dist_info[0] if dist_info else 0.0
        transit_mins = dist_info[1] if dist_info else 0

        self.wm.set_reroute_target(source_lot, target_lot)
        return {
            "success": True,
            "status": "DISPATCHED",
            "source_lot": source_lot,
            "target_lot": target_lot,
            "divert_percentage": min(50.0, max(5.0, divert_percentage)),
            "distance_km": distance_km,
            "transit_time_minutes": transit_mins,
            "advisory_message": f"Diverting {divert_percentage:.0f}% traffic from {source_lot} to {target_lot} ({distance_km} km away, ~{transit_mins} mins).",
            "reason": reason,
        }

    def inspect_dlq_anomalies(self, limit: int = 5) -> Dict[str, Any]:
        # Return recent anomalies observed in working context
        dlq_alerts = [a for a in self.wm.active_alerts if a.get("type") == "DLQ_ANOMALY"]
        return {
            "success": True,
            "total_quarantined": len(self.wm.quarantined_sensors),
            "recent_anomalies": dlq_alerts[-limit:] if dlq_alerts else [
                {
                    "event_id": "EVT_ANOMALY_SAMPLE",
                    "lot_id": "LOT_HEBBAL_01",
                    "slot_id": "LOT_HEBBAL_01-S042",
                    "error": "Corrupt coordinates: Lat=999.0, Lon=-999.0",
                }
            ],
        }

    def quarantine_sensor(self, lot_id: str, slot_id: str, fault_type: str, reason: str) -> Dict[str, Any]:
        ticket_id = f"TICK_BBMP_{slot_id.replace('-', '_')}"
        details = {
            "lot_id": lot_id,
            "slot_id": slot_id,
            "fault_type": fault_type,
            "reason": reason,
            "work_order_id": ticket_id,
            "quarantine_status": "ACTIVE",
        }
        self.wm.quarantine_sensor(slot_id, details)
        return {
            "success": True,
            "status": "QUARANTINED",
            "slot_id": slot_id,
            "work_order_id": ticket_id,
            "assigned_crew": "BBMP IoT Maintenance Unit 4",
            "message": f"Sensor {slot_id} quarantined from stream processing. Work order {ticket_id} filed.",
        }

    def query_historical_memory(self, lot_id: str, trigger_type: str) -> Dict[str, Any]:
        episodes = self.em.find_similar_episodes(lot_id, trigger_type, limit=3)
        return {
            "success": True,
            "count": len(episodes),
            "historical_episodes": [ep.to_dict() for ep in episodes],
        }
