"""
agents.cwd.diagnostic_worker
============================
Sensor Diagnostic, DLQ Triage & Fault Isolation Worker Agent.
Course: AI373TA — Units III & IV (Worker role specialization).

Specialization:
- Inspects anomalous records rejected by Spark streaming schema validation.
- Classifies IoT hardware failure modes (stuck sensors, dead batteries, corrupt coordinates).
- Quarantines rogue sensors to protect stream integrity and creates maintenance tickets.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from agents.cwd.worker_base import WorkerBase
from agents.tools.parking_tools import ParkingToolRegistry

logger = logging.getLogger("agents.cwd.diagnostic")


class DiagnosticWorker(WorkerBase):
    """Specialized worker for automated DLQ inspection and sensor maintenance ticketing."""

    def __init__(self, tool_registry: ParkingToolRegistry) -> None:
        super().__init__(
            name="SensorDiagnosticWorker",
            role="DLQ Triage & Sensor Fault Quarantine",
            tool_registry=tool_registry,
        )

    def evaluate_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        lot_id = task.get("lot_id", "LOT_HEBBAL_01")
        slot_id = task.get("slot_id") or f"{lot_id}-S042"
        error_msg = task.get("error_message", "Corrupt coordinates or schema rejection")

        self.log_action(f"Evaluating sensor anomaly at {lot_id} | Slot: {slot_id} | Error: {error_msg}")

        # Classify the sensor fault
        if "coordinate" in error_msg.lower() or "lat" in error_msg.lower():
            fault_type = "CORRUPT_GPS_COORDINATES"
            reason = "Sensor transmitted telemetry outside valid Karnataka geographic bounding box."
        elif "stuck" in error_msg.lower() or "duplicate" in error_msg.lower():
            fault_type = "STUCK_MAGNETIC_REED"
            reason = "Slot state oscillating with zero physical transit interval."
        else:
            fault_type = "COMMUNICATION_JITTER_FAILURE"
            reason = f"Stream ingestion rejected payload: {error_msg}"

        proposal = {
            "worker": self.name,
            "status": "ACTION_PROPOSED",
            "action_type": "QUARANTINE_SENSOR",
            "lot_id": lot_id,
            "slot_id": slot_id,
            "fault_type": fault_type,
            "confidence": 0.95,
            "reason": reason,
            "execution_tool": "quarantine_sensor",
            "tool_kwargs": {
                "lot_id": lot_id,
                "slot_id": slot_id,
                "fault_type": fault_type,
                "reason": reason,
            },
        }
        self.log_action(f"Proposed sensor quarantine: {slot_id} ({fault_type})")
        return proposal
