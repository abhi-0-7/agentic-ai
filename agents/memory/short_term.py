"""
agents.memory.short_term
========================
Working Memory (Short-Term Memory & Context Management).
Course: AI373TA — Unit IV (Working Memory & Context Management).

Maintains:
- Ephemeral active micro-batch streaming metrics for all parking lots.
- Active threshold alerts & triggering events.
- In-flight interventions pending reflection evaluation.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class LotCurrentState:
    lot_id: str
    occupied_slots: int
    capacity: int
    occupancy_percentage: float
    entry_velocity_per_min: float = 0.0
    exit_velocity_per_min: float = 0.0
    current_surge_multiplier: float = 1.0
    active_reroute_target: Optional[str] = None
    last_updated_epoch: float = field(default_factory=time.time)

    @property
    def available_slots(self) -> int:
        return max(0, self.capacity - self.occupied_slots)


class WorkingMemory:
    """Fast, volatile in-memory working scratchpad for agent perception and context."""

    def __init__(self, ttl_seconds: float = 600.0) -> None:
        self.ttl_seconds = ttl_seconds
        self.lot_states: Dict[str, LotCurrentState] = {}
        self.active_alerts: List[Dict[str, Any]] = []
        self.in_flight_actions: Dict[str, Dict[str, Any]] = {}  # action_id -> metadata
        self.quarantined_sensors: Dict[str, Dict[str, Any]] = {}  # sensor_id -> quarantine info

    def update_lot_metrics(
        self,
        lot_id: str,
        occupied: int,
        capacity: int,
        entry_vel: float = 0.0,
        exit_vel: float = 0.0,
    ) -> LotCurrentState:
        """Update or insert the latest micro-batch telemetry for a lot."""
        pct = (occupied / max(1, capacity)) * 100.0
        current = self.lot_states.get(lot_id)
        surge = current.current_surge_multiplier if current else 1.0
        reroute = current.active_reroute_target if current else None

        state = LotCurrentState(
            lot_id=lot_id,
            occupied_slots=occupied,
            capacity=capacity,
            occupancy_percentage=round(pct, 2),
            entry_velocity_per_min=round(entry_vel, 2),
            exit_velocity_per_min=round(exit_vel, 2),
            current_surge_multiplier=surge,
            active_reroute_target=reroute,
            last_updated_epoch=time.time(),
        )
        self.lot_states[lot_id] = state
        return state

    def get_lot_state(self, lot_id: str) -> Optional[LotCurrentState]:
        return self.lot_states.get(lot_id)

    def set_surge_multiplier(self, lot_id: str, multiplier: float) -> None:
        if lot_id in self.lot_states:
            self.lot_states[lot_id].current_surge_multiplier = round(multiplier, 2)

    def set_reroute_target(self, lot_id: str, target_lot_id: Optional[str]) -> None:
        if lot_id in self.lot_states:
            self.lot_states[lot_id].active_reroute_target = target_lot_id

    def record_alert(self, alert: Dict[str, Any]) -> None:
        alert["timestamp"] = alert.get("timestamp", datetime.now(timezone.utc).isoformat())
        self.active_alerts.append(alert)
        if len(self.active_alerts) > 100:
            self.active_alerts = self.active_alerts[-100:]

    def clear_resolved_alerts(self, lot_id: str) -> None:
        self.active_alerts = [a for a in self.active_alerts if a.get("lot_id") != lot_id]

    def register_in_flight_action(self, action_id: str, action_data: Dict[str, Any]) -> None:
        action_data["registered_at"] = time.time()
        self.in_flight_actions[action_id] = action_data

    def pop_in_flight_action(self, action_id: str) -> Optional[Dict[str, Any]]:
        return self.in_flight_actions.pop(action_id, None)

    def quarantine_sensor(self, sensor_id: str, details: Dict[str, Any]) -> None:
        details["quarantined_at"] = datetime.now(timezone.utc).isoformat()
        self.quarantined_sensors[sensor_id] = details

    def is_sensor_quarantined(self, sensor_id: str) -> bool:
        return sensor_id in self.quarantined_sensors
