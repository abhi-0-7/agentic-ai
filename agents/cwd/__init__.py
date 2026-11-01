"""
agents.cwd
==========
Coordinator-Worker-Delegator (CWD) Multi-Agent System.
Course: AI373TA — Units III & IV.

Components:
- CoordinatorAgent: Supervisory authority, maintains global equilibrium & approves decisions.
- DelegatorAgent: Decomposes streaming triggers & assigns specialized tasks.
- TrafficWorker: Spatial mobility & traffic rerouting.
- PricingWorker: Micro-economic surge pricing & demand management.
- DiagnosticWorker: DLQ sensor fault triage & hardware quarantine.
- AgentNegotiator: Formal inter-agent negotiation & conflict resolution.
"""

from agents.cwd.coordinator import CoordinatorAgent
from agents.cwd.delegator import DelegatorAgent
from agents.cwd.diagnostic_worker import DiagnosticWorker
from agents.cwd.negotiator import AgentNegotiator
from agents.cwd.pricing_worker import PricingWorker
from agents.cwd.traffic_worker import TrafficWorker
from agents.cwd.worker_base import WorkerBase

__all__ = [
    "CoordinatorAgent",
    "DelegatorAgent",
    "TrafficWorker",
    "PricingWorker",
    "DiagnosticWorker",
    "AgentNegotiator",
    "WorkerBase",
]
