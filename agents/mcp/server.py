"""
agents.mcp.server
=================
Model Context Protocol (MCP) Server Implementation.
Course: AI373TA — Unit V (Model Context Protocol Architecture, Tools, Resources, Prompts).

Architecture Implemented:
- Core Components: Resources, Tools, Prompts.
- Transport: JSON-RPC 2.0 (compatible with Claude Desktop, Antigravity, and MCP clients).
- Server Lifecycle: initialize, list_tools, call_tool, list_resources, read_resource, list_prompts.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from typing import Any, Dict, List, Optional

from agents.memory.episodic import EpisodicMemory
from agents.memory.knowledge_base import ParkingKnowledgeBase
from agents.memory.short_term import WorkingMemory
from agents.tools.parking_tools import ParkingToolRegistry

logger = logging.getLogger("agents.mcp")


class ParkingMCPServer:
    """Standard Model Context Protocol (MCP) Server for Smart Parking Analytics."""

    def __init__(
        self,
        working_memory: Optional[WorkingMemory] = None,
        knowledge_base: Optional[ParkingKnowledgeBase] = None,
        episodic_memory: Optional[EpisodicMemory] = None,
    ) -> None:
        self.kb = knowledge_base or ParkingKnowledgeBase()
        self.wm = working_memory or WorkingMemory()
        self.em = episodic_memory or EpisodicMemory()
        self.tools = ParkingToolRegistry(self.wm, self.kb, self.em)

        self.server_info = {
            "name": "bengaluru-smart-parking-mcp",
            "version": "1.0.0",
            "description": "Model Context Protocol Server for Bengaluru Smart Parking Cognitive Control Network (AI373TA)",
        }

    # ─── 1. MCP Resources (Unit V) ──────────────────────────────────────

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all available read-only resources in the parking system."""
        resources = [
            {
                "uri": "parking://system/status",
                "name": "City Parking Telemetry Overview",
                "mimeType": "application/json",
                "description": "Aggregated real-time capacity and occupancy across all 8 Bengaluru zones.",
            },
            {
                "uri": "parking://dlq/anomalies",
                "name": "Dead Letter Queue Anomalies",
                "mimeType": "application/json",
                "description": "Quarantined sensor packets rejected by Spark schema validation.",
            },
            {
                "uri": "parking://episodes/recent",
                "name": "Recent Episodic Interventions",
                "mimeType": "application/json",
                "description": "Audit log of autonomous agent decisions, negotiated compromises, and reflection scores.",
            },
        ]
        for lot_id in self.kb.lots:
            resources.append({
                "uri": f"parking://lots/{lot_id}",
                "name": f"Lot State: {lot_id}",
                "mimeType": "application/json",
                "description": f"Real-time occupancy, tariff, and sensor health for {lot_id}.",
            })
        return resources

    def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read the dynamic content of a specified resource URI."""
        if uri == "parking://system/status":
            total_cap = sum(node.capacity for node in self.kb.lots.values())
            total_occ = sum(s.occupied_slots for s in self.wm.lot_states.values())
            return {
                "uri": uri,
                "mimeType": "application/json",
                "contents": json.dumps({
                    "city": "Bengaluru",
                    "total_capacity": total_cap,
                    "total_occupied": total_occ,
                    "overall_occupancy_pct": round((total_occ / max(1, total_cap)) * 100.0, 2),
                    "active_quarantines": len(self.wm.quarantined_sensors),
                    "active_reroutes": sum(1 for s in self.wm.lot_states.values() if s.active_reroute_target),
                }),
            }

        if uri == "parking://dlq/anomalies":
            res = self.tools.execute_tool("inspect_dlq_anomalies")
            return {"uri": uri, "mimeType": "application/json", "contents": json.dumps(res)}

        if uri == "parking://episodes/recent":
            episodes = [ep.to_dict() for ep in self.em.episodes[-10:]]
            return {"uri": uri, "mimeType": "application/json", "contents": json.dumps(episodes)}

        if uri.startswith("parking://lots/"):
            lot_id = uri.replace("parking://lots/", "")
            res = self.tools.execute_tool("query_stream_metrics", lot_id=lot_id)
            return {"uri": uri, "mimeType": "application/json", "contents": json.dumps(res)}

        raise ValueError(f"Resource not found: {uri}")

    # ─── 2. MCP Tools (Unit V) ──────────────────────────────────────────

    def list_tools(self) -> List[Dict[str, Any]]:
        """List all callable tools available for agent function calling."""
        return self.tools.get_all_schemas()

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool via the MCP protocol."""
        return self.tools.execute_tool(tool_name, **arguments)

    # ─── 3. MCP Prompts (Unit V) ────────────────────────────────────────

    def list_prompts(self) -> List[Dict[str, Any]]:
        """Return standardized prompts for agent reasoning workflows."""
        return [
            {
                "name": "diagnose_congestion",
                "description": "Prompt for autonomous reasoning when a lot exceeds 85% occupancy.",
                "arguments": [
                    {"name": "lot_id", "description": "Congested parking facility", "required": True}
                ],
            },
            {
                "name": "audit_sensor_health",
                "description": "Prompt for triaging DLQ errors and deciding sensor quarantine.",
                "arguments": [
                    {"name": "slot_id", "description": "Anomalous sensor identifier", "required": True}
                ],
            },
        ]

    def get_prompt(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Construct prompt template for LLM consumption."""
        if name == "diagnose_congestion":
            lot_id = arguments.get("lot_id", "LOT_MG_ROAD_01")
            return {
                "name": name,
                "description": "Congestion Mitigation Workflow",
                "messages": [
                    {
                        "role": "user",
                        "content": {
                            "type": "text",
                            "text": (
                                f"Parking lot {lot_id} has exceeded the 85% critical threshold. "
                                f"Inspect its spatial neighbors, evaluate price surge elasticity, "
                                f"and invoke 'dispatch_reroute_guidance' and 'adjust_dynamic_tariff' "
                                f"to achieve system equilibrium."
                            ),
                        },
                    }
                ],
            }

        if name == "audit_sensor_health":
            slot_id = arguments.get("slot_id", "LOT_HEBBAL_01-S042")
            return {
                "name": name,
                "description": "Sensor Fault Triage Workflow",
                "messages": [
                    {
                        "role": "user",
                        "content": {
                            "type": "text",
                            "text": (
                                f"Sensor {slot_id} is continuously emitting malformed packets to Kafka DLQ. "
                                f"Classify the hardware failure mode and invoke 'quarantine_sensor' "
                                f"to preserve Spark streaming integrity."
                            ),
                        },
                    }
                ],
            }

        raise ValueError(f"Prompt '{name}' not found.")

    # ─── 4. JSON-RPC 2.0 Dispatcher (Unit V: Transport Layer) ──────────

    def handle_json_rpc(self, request_str: str) -> str:
        """Handle incoming JSON-RPC 2.0 message."""
        try:
            req = json.loads(request_str)
        except Exception as e:
            return json.dumps({"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None})

        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        if method == "initialize":
            return json.dumps({
                "jsonrpc": "2.0",
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": self.server_info,
                    "capabilities": {
                        "resources": {"subscribe": False, "listChanged": True},
                        "tools": {"listChanged": True},
                        "prompts": {"listChanged": True},
                    },
                },
                "id": req_id,
            })

        if method == "tools/list":
            return json.dumps({"jsonrpc": "2.0", "result": {"tools": self.list_tools()}, "id": req_id})

        if method == "tools/call":
            name = params.get("name")
            args = params.get("arguments", {})
            res = self.call_tool(name, args)
            return json.dumps({
                "jsonrpc": "2.0",
                "result": {"content": [{"type": "text", "text": json.dumps(res)}]},
                "id": req_id,
            })

        if method == "resources/list":
            return json.dumps({"jsonrpc": "2.0", "result": {"resources": self.list_resources()}, "id": req_id})

        if method == "resources/read":
            uri = params.get("uri")
            try:
                res = self.read_resource(uri)
                return json.dumps({"jsonrpc": "2.0", "result": {"contents": [res]}, "id": req_id})
            except Exception as e:
                return json.dumps({"jsonrpc": "2.0", "error": {"code": -32602, "message": str(e)}, "id": req_id})

        if method == "prompts/list":
            return json.dumps({"jsonrpc": "2.0", "result": {"prompts": self.list_prompts()}, "id": req_id})

        if method == "prompts/get":
            name = params.get("name")
            args = params.get("arguments", {})
            try:
                res = self.get_prompt(name, args)
                return json.dumps({"jsonrpc": "2.0", "result": res, "id": req_id})
            except Exception as e:
                return json.dumps({"jsonrpc": "2.0", "error": {"code": -32602, "message": str(e)}, "id": req_id})

        return json.dumps({
            "jsonrpc": "2.0",
            "error": {"code": -32601, "message": f"Method '{method}' not found"},
            "id": req_id,
        })


def main() -> None:
    """CLI runner for the Model Context Protocol Server."""
    parser = argparse.ArgumentParser(description="Bengaluru Smart Parking MCP Server (AI373TA)")
    parser.add_argument("--list-tools", action="store_true", help="Print available MCP tools and exit")
    parser.add_argument("--list-resources", action="store_true", help="Print available MCP resources and exit")
    parser.add_argument("--test-call", type=str, help="Test tool call e.g. 'query_stream_metrics'")
    args = parser.parse_args()

    server = ParkingMCPServer()

    if args.list_tools:
        print("\n=== REGISTERED MCP TOOLS (Unit V) ===")
        print(json.dumps(server.list_tools(), indent=2))
        return

    if args.list_resources:
        print("\n=== REGISTERED MCP RESOURCES (Unit V) ===")
        print(json.dumps(server.list_resources(), indent=2))
        return

    if args.test_call:
        print(f"\n=== TESTING MCP TOOL CALL: {args.test_call} ===")
        out = server.call_tool(args.test_call, {"lot_id": "LOT_MG_ROAD_01"})
        print(json.dumps(out, indent=2))
        return

    print("Smart Parking MCP Server active. Awaiting JSON-RPC requests on stdio...")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        response = server.handle_json_rpc(line)
        print(response, flush=True)


if __name__ == "__main__":
    main()
