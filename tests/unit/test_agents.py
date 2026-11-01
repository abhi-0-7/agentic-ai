"""
tests/unit/test_agents.py
=========================
Unit Tests for the Agentic AI Subsystem.
Course: AI373TA — Agentic Artificial Intelligence (Semester VII)
RV College of Engineering, Bengaluru.

Covers:
1. Three-Tier Memory Architecture (Knowledge Base, Working Memory, Episodic Memory)
2. Concrete Tool Execution and Schema Compliance
3. Coordinator-Worker-Delegator (CWD) Model and Inter-Agent Negotiation
4. Closed-Loop Reflection and Introspection Engine
5. Model Context Protocol (MCP) Server and JSON-RPC Transport
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from agents.cwd.coordinator import CoordinatorAgent
from agents.cwd.delegator import DelegatorAgent
from agents.cwd.diagnostic_worker import DiagnosticWorker
from agents.cwd.negotiator import AgentNegotiator
from agents.cwd.pricing_worker import PricingWorker
from agents.cwd.traffic_worker import TrafficWorker
from agents.mcp.server import ParkingMCPServer
from agents.memory.episodic import Episode, EpisodicMemory
from agents.memory.knowledge_base import ParkingKnowledgeBase
from agents.memory.short_term import WorkingMemory
from agents.orchestrator import ParkingAgentOrchestrator
from agents.reflection.introspector import Introspector
from agents.tools.parking_tools import ParkingToolRegistry


class TestAgentMemoryHierarchy(unittest.TestCase):
    """Test Suite for Unit IV: Three-Tier Agent Memory Architecture."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.episodic_file = Path(self.temp_dir) / "test_episodic.jsonl"
        self.kb = ParkingKnowledgeBase()
        self.wm = WorkingMemory(ttl_seconds=300.0)
        self.em = EpisodicMemory(persistence_path=self.episodic_file)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_knowledge_base_distances_and_topology(self) -> None:
        """KB correctly computes topological distance and transit times."""
        dist_info = self.kb.get_distance("LOT_MG_ROAD_01", "LOT_INDIRANAGAR_01")
        self.assertIsNotNone(dist_info)
        dist_km, transit_mins = dist_info
        self.assertGreater(dist_km, 0)
        self.assertGreater(transit_mins, 0)

        # Nearest available neighbors
        neighbors = self.kb.find_nearest_available_lots("LOT_MG_ROAD_01", max_distance_km=10.0)
        self.assertGreater(len(neighbors), 0)
        self.assertEqual(neighbors[0]["lot_id"], "LOT_INDIRANAGAR_01")

    def test_knowledge_base_bbmp_statutory_validation(self) -> None:
        """KB enforces BBMP municipal tariff ceilings."""
        valid, _ = self.kb.validate_tariff(75.0)
        self.assertTrue(valid)

        # Below legal minimum
        valid_low, msg_low = self.kb.validate_tariff(15.0)
        self.assertFalse(valid_low)
        self.assertIn("below legal minimum", msg_low.lower())

        # Exceeds statutory ceiling
        valid_high, msg_high = self.kb.validate_tariff(200.0)
        self.assertFalse(valid_high)
        self.assertIn("exceeds bbmp statutory ceiling", msg_high.lower())

    def test_working_memory_state_updates(self) -> None:
        """Working memory accurately updates and retrieves lot state."""
        state = self.wm.update_lot_metrics("LOT_MG_ROAD_01", occupied=120, capacity=150, entry_vel=10.0)
        self.assertEqual(state.occupancy_percentage, 80.0)
        self.assertEqual(state.available_slots, 30)

        retrieved = self.wm.get_lot_state("LOT_MG_ROAD_01")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.occupied_slots, 120)

    def test_episodic_memory_persistence_and_retrieval(self) -> None:
        """Episodic memory persists episodes and retrieves matching histories."""
        ep = Episode(
            trigger_type="CONGESTION_SPIKE",
            lot_id="LOT_MG_ROAD_01",
            initial_metrics={"occupancy_percentage": 88.0},
            status="EVALUATED",
            reflection_score=1.0,
        )
        self.em.record_episode(ep)
        self.assertTrue(self.episodic_file.is_file())

        # Query similar episodes
        matches = self.em.find_similar_episodes("LOT_MG_ROAD_01", "CONGESTION_SPIKE")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].reflection_score, 1.0)


class TestAgentToolsRegistry(unittest.TestCase):
    """Test Suite for Units II & III: Tool and Function Calling."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.kb = ParkingKnowledgeBase()
        self.wm = WorkingMemory()
        self.em = EpisodicMemory(persistence_path=Path(self.temp_dir) / "ep.jsonl")
        self.registry = ParkingToolRegistry(self.wm, self.kb, self.em)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_tool_schemas_compliance(self) -> None:
        """All registered tools have valid JSON Schema function definitions."""
        schemas = self.registry.get_all_schemas()
        self.assertGreaterEqual(len(schemas), 6)
        for s in schemas:
            self.assertIn("name", s)
            self.assertIn("description", s)
            self.assertIn("parameters", s)

    def test_adjust_dynamic_tariff_tool(self) -> None:
        """Tool adjusts tariff within statutory bounds and updates working memory."""
        res = self.registry.execute_tool(
            "adjust_dynamic_tariff",
            lot_id="LOT_MG_ROAD_01",
            surge_multiplier=1.4,
            reason="Demand surge test",
        )
        self.assertTrue(res["success"])
        self.assertEqual(res["new_surge_multiplier"], 1.4)
        self.assertEqual(res["effective_tariff_inr"], 70.0)

        # Working memory should reflect the new multiplier
        state = self.wm.get_lot_state("LOT_MG_ROAD_01")
        if state:
            self.assertEqual(state.current_surge_multiplier, 1.4)

    def test_quarantine_sensor_tool(self) -> None:
        """Tool isolates sensor and files work order."""
        res = self.registry.execute_tool(
            "quarantine_sensor",
            lot_id="LOT_HEBBAL_01",
            slot_id="LOT_HEBBAL_01-S012",
            fault_type="CORRUPT_COORDINATES",
            reason="Test fault",
        )
        self.assertTrue(res["success"])
        self.assertTrue(self.wm.is_sensor_quarantined("LOT_HEBBAL_01-S012"))


class TestCWDMultiAgentEngine(unittest.TestCase):
    """Test Suite for Units III & IV: CWD Architecture & Negotiation."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.kb = ParkingKnowledgeBase()
        self.wm = WorkingMemory()
        self.em = EpisodicMemory(persistence_path=Path(self.temp_dir) / "ep.jsonl")
        self.tools = ParkingToolRegistry(self.wm, self.kb, self.em)

        self.traffic_worker = TrafficWorker(self.tools)
        self.pricing_worker = PricingWorker(self.tools)
        self.diagnostic_worker = DiagnosticWorker(self.tools)
        self.negotiator = AgentNegotiator()
        self.delegator = DelegatorAgent(
            self.traffic_worker, self.pricing_worker, self.diagnostic_worker, self.negotiator
        )
        self.coordinator = CoordinatorAgent(
            self.delegator, self.tools, self.wm, self.kb, self.em
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_traffic_worker_proposal(self) -> None:
        """Traffic worker evaluates congestion and proposes viable reroute."""
        task = {"lot_id": "LOT_MG_ROAD_01", "occupancy_percentage": 92.0}
        proposal = self.traffic_worker.evaluate_task(task)
        self.assertEqual(proposal["status"], "ACTION_PROPOSED")
        self.assertEqual(proposal["action_type"], "DISPATCH_REROUTE_GUIDANCE")
        self.assertIn("target_lot", proposal)

    def test_pricing_worker_proposal(self) -> None:
        """Pricing worker evaluates demand and proposes surge multiplier."""
        task = {"lot_id": "LOT_MG_ROAD_01", "occupancy_percentage": 93.0}
        proposal = self.pricing_worker.evaluate_task(task)
        self.assertEqual(proposal["status"], "ACTION_PROPOSED")
        self.assertGreater(proposal["surge_multiplier"], 1.0)

    def test_negotiation_resolves_conflict(self) -> None:
        """Negotiator resolves conflict with Pareto-optimal consensus."""
        traffic_prop = {
            "worker": "TrafficWorker",
            "action_type": "DISPATCH_REROUTE_GUIDANCE",
            "target_lot": "LOT_INDIRANAGAR_01",
            "divert_percentage": 30.0,
            "tool_kwargs": {"source_lot": "LOT_MG_ROAD_01", "target_lot": "LOT_INDIRANAGAR_01", "divert_percentage": 30.0, "reason": "test"},
        }
        pricing_prop = {
            "worker": "PricingWorker",
            "action_type": "ADJUST_DYNAMIC_TARIFF",
            "lot_id": "LOT_MG_ROAD_01",
            "surge_multiplier": 2.0,
            "tool_kwargs": {"lot_id": "LOT_MG_ROAD_01", "surge_multiplier": 2.0, "reason": "test"},
        }
        context = {"lot_id": "LOT_MG_ROAD_01", "occupancy_percentage": 95.0}

        resolution = self.negotiator.resolve_conflict(traffic_prop, pricing_prop, context)
        self.assertEqual(resolution["status"], "CONSENSUS_REACHED")
        self.assertIn("PARETO_OPTIMAL", resolution["resolution_strategy"])
        self.assertEqual(len(resolution["actions"]), 3)

    def test_coordinator_execution_and_episode_creation(self) -> None:
        """Coordinator executes delegated plan and records episode."""
        trigger = {
            "trigger_type": "CRITICAL_GRIDLOCK",
            "lot_id": "LOT_MG_ROAD_01",
            "occupancy_percentage": 94.0,
            "entry_velocity_per_min": 12.0,
        }
        res = self.coordinator.handle_stream_event(trigger)
        self.assertEqual(res["status"], "EXECUTED")
        self.assertIn("episode_id", res)
        self.assertEqual(len(self.em.episodes), 1)


class TestReflectionIntrospection(unittest.TestCase):
    """Test Suite for Unit II & CO2: Reflection & Introspection."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.wm = WorkingMemory()
        self.em = EpisodicMemory(persistence_path=Path(self.temp_dir) / "ep.jsonl")
        self.introspector = Introspector(self.wm, self.em)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_reflection_evaluates_success(self) -> None:
        """Reflection assigns score +1.0 when occupancy drops significantly."""
        ep = Episode(
            trigger_type="CONGESTION_SPIKE",
            lot_id="LOT_MG_ROAD_01",
            initial_metrics={"occupancy_percentage": 95.0, "entry_velocity_per_min": 15.0},
            status="PENDING_EVALUATION",
        )
        self.em.record_episode(ep)

        # Simulate subsequent stream state in working memory showing improvement
        self.wm.update_lot_metrics("LOT_MG_ROAD_01", occupied=120, capacity=150, entry_vel=4.0)  # 80.0%

        reports = self.introspector.evaluate_pending_episodes()
        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0]["score"], 1.0)
        self.assertEqual(ep.status, "EVALUATED")


class TestMCPServer(unittest.TestCase):
    """Test Suite for Unit V: Model Context Protocol (MCP) Server."""

    def setUp(self) -> None:
        self.server = ParkingMCPServer()

    def test_mcp_initialize(self) -> None:
        """JSON-RPC initialize returns server info and capabilities."""
        req = json.dumps({"jsonrpc": "2.0", "method": "initialize", "params": {}, "id": 1})
        res = json.loads(self.server.handle_json_rpc(req))
        self.assertEqual(res["result"]["serverInfo"]["name"], "bengaluru-smart-parking-mcp")
        self.assertTrue(res["result"]["capabilities"]["tools"]["listChanged"])

    def test_mcp_tools_list_and_call(self) -> None:
        """JSON-RPC tools/list and tools/call work seamlessly."""
        list_req = json.dumps({"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 2})
        list_res = json.loads(self.server.handle_json_rpc(list_req))
        tool_names = [t["name"] for t in list_res["result"]["tools"]]
        self.assertIn("query_stream_metrics", tool_names)

        call_req = json.dumps({
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": "query_stream_metrics", "arguments": {"lot_id": "LOT_MG_ROAD_01"}},
            "id": 3,
        })
        call_res = json.loads(self.server.handle_json_rpc(call_req))
        self.assertIn("content", call_res["result"])

    def test_mcp_resources_list_and_read(self) -> None:
        """JSON-RPC resources/list and resources/read work seamlessly."""
        read_req = json.dumps({
            "jsonrpc": "2.0",
            "method": "resources/read",
            "params": {"uri": "parking://system/status"},
            "id": 4,
        })
        read_res = json.loads(self.server.handle_json_rpc(read_req))
        contents = json.loads(read_res["result"]["contents"][0]["contents"])
        self.assertEqual(contents["city"], "Bengaluru")


if __name__ == "__main__":
    unittest.main()
