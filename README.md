# Smart Parking Cognitive Agentic Network (SMCAN)
## Autonomous Multi-Agent Coordination & Real-Time Cyber-Physical Stream Intelligence

[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.13-brightgreen.svg)](https://python.org)
[![Agentic AI: CWD Architecture](https://img.shields.io/badge/Agentic%20AI-Coordinator--Worker--Delegator-blue.svg)](#)
[![Model Context Protocol](https://img.shields.io/badge/MCP-JSON--RPC%202.0%20Stdio-purple.svg)](#)
[![Apache Spark: 3.5.1](https://img.shields.io/badge/Apache%20Spark-3.5.1%20Structured%20Streaming-orange.svg)](https://spark.apache.org)
[![Apache Kafka: KRaft](https://img.shields.io/badge/Apache%20Kafka-KRaft%20Mode-black.svg)](https://kafka.apache.org)
[![InfluxDB: 2.7](https://img.shields.io/badge/InfluxDB-2.7%20Time--Series-indigo.svg)](https://influxdata.com)
[![Grafana: 11](https://img.shields.io/badge/Grafana-Port%203001%20Live%20Sync-yellow.svg)](https://grafana.com)
[![Tests: 58/58 Passed](https://img.shields.io/badge/Tests-58%2F58%20Passed%20(0.25s)-success.svg)](#)

---

## 🌟 Executive Overview: Why Agentic AI?

Traditional smart city architectures rely on **Stream Processing (Kafka & Spark Streaming)** to ingest sensor telemetry and display dashboards on **Grafana**. 

However, **stream processing is purely passive**:
- When a central parking facility hits **95% capacity**, a streaming dashboard simply turns red.
- When an ultrasonic IoT sensor breaks and transmits corrupt GPS coordinates (`Lat: 999.0`), bad data enters the time-series database unchecked.
- **Human operators must constantly monitor screens to manually notice and fix problems.**

**This project introduces the Agentic AI Layer:** an autonomous, closed-loop multi-agent system that sits directly on top of real-time streaming data to **perceive bottlenecks, deliberate across spatial networks, execute concrete actions via tools, and verify real-world outcomes.**

> 📖 **Want a 2-minute plain-English guide?** Read [`WHAT_AGENTS_DO.md`](WHAT_AGENTS_DO.md).  
> 🚀 **Want beginner step-by-step instructions to run everything?** Read [`HOW_TO_RUN.md`](HOW_TO_RUN.md).

---

## 🧠 End-to-End System Architecture

```text
 ┌────────────────────────────────────────────────────────────────────────────────────────┐
 │                     SENSORY NERVOUS SYSTEM: REAL-TIME STREAMING                        │
 │                                                                                        │
 │  [Virtual IoT Sensors] ──> [Apache Kafka KRaft] ──> [Spark Structured Streaming]       │
 │  (8 Lots, 1,000 Bays)      Topic: raw-parking-events        • 2-Min Watermarking       │
 │                            Topic: parking-events-dlq        • 1-Min Tumbling Windows   │
 │                                                             • Slot State Machine (FSM) │
 └───────────────────────────────────────────┬────────────────────────────────────────────┘
                                             │ Micro-Batch Occupancies & DLQ Alerts
                                             ▼
 ┌────────────────────────────────────────────────────────────────────────────────────────┐
 │                       COGNITIVE BRAIN: MULTI-AGENT AGENTIC AI                          │
 │                                                                                        │
 │  1. THREE-TIER COGNITIVE MEMORY                                                        │
 │     ├── Working Memory (RAM): Ephemeral micro-batch occupancies, velocities, alerts.   │
 │     ├── Episodic Memory (JSONL): Audit trail of actions & post-action reflection scores│
 │     └── Knowledge Base (Long-Term): 8-facility spatial road graph & municipal bylaws.  │
 │                                                                                        │
 │  2. COORDINATOR - WORKER - DELEGATOR (CWD) ENGINE                                      │
 │     ┌────────────────────────────────────────────────────────────────────────────┐     │
 │     │                         COORDINATOR AGENT                                  │     │
 │     │      (Supervises 60-85% City Equilibrium, Authorizes Tool Executions)      │     │
 │     └─────────────────────────────────────┬──────────────────────────────────────┘     │
 │                                           │ Delegates Tasks                            │
 │     ┌─────────────────────────────────────┴──────────────────────────────────────┐     │
 │     │                          DELEGATOR AGENT                                   │     │
 │     │              (Triage streaming events & orchestrates workers)              │     │
 │     └─────────────┬───────────────────────┬──────────────────────┬───────────────┘     │
 │                   │                       │                      │                     │
 │                   ▼                       ▼                      ▼                     │
 │          ┌─────────────────┐     ┌─────────────────┐    ┌─────────────────┐            │
 │          │ TRAFFIC WORKER  │     │ALLOCATION WORKER│    │DIAGNOSTIC WORKER│            │
 │          │ Spatial Reroute │     │Fair Bay Reserve │    │DLQ Self-Healing │            │
 │          └────────┬────────┘     └────────┬────────┘    └────────┬────────┘            │
 │                   │                       │                      │                     │
 │                   └───────────┬───────────┘                      │                     │
 │                               ▼                                  │                     │
 │                     [PARETO NEGOTIATION]                         │                     │
 │                (Optimizes Reroute % without                      │                     │
 │                 overloading target corridors)                    │                     │
 │                               │                                  │                     │
 │                               └─────────────────┬────────────────┘                     │
 │                                                 │ Approved Execution Plan              │
 │  3. CONCRETE TOOL EXECUTION                     ▼                                      │
 │     • dispatch_reroute_guidance()     • allocate_overflow_bays()                       │
 │     • quarantine_sensor()             • inspect_dlq_anomalies()                        │
 │                                                                                        │
 │  4. MODEL CONTEXT PROTOCOL (MCP) SERVER                                                │
 │     • Standards-compliant JSON-RPC 2.0 stdio interface for external LLM orchestrators. │
 │                                                                                        │
 │  5. CLOSED-LOOP INTROSPECTIVE REFLECTION                                               │
 │     • Evaluates Delta: ΔOccupancy = Pre - Post | ΔVelocity = Pre - Post                │
 │     • Computes Normalized Score: +1.0 (Success) | 0.0 (Neutral) | -1.0 (Adverse)       │
 │     • Commits verified learnings to Episodic Memory (`data/episodic_memory.jsonl`).    │
 └───────────────────────────────────────────┬────────────────────────────────────────────┘
                                             │ Real-Time Decision Telemetry
                                             ▼
 ┌────────────────────────────────────────────────────────────────────────────────────────┐
 │                      VISUAL DECISION & COMMAND CENTERS                                 │
 │  • Web Command Center (Port 5000): Split-screen with Live Agent Dialogue Feed          │
 │  • Grafana Dashboard (Port 3001): 8-corridor live occupancy bar charts & time-series   │
 └────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🤖 The 4 Autonomous Agents Explained

| Agent | Core Responsibility | Tools Invoked | Real-World Impact |
| :--- | :--- | :--- | :--- |
| **Coordinator Agent** | Citywide Equilibrium & Supervisory Authority | `authorize_action()`, `commit_episodic_memory()` | Keeps all 8 facilities within the 60%–85% target window. Prevents rogue actions and logs persistent audit trails. |
| **Traffic Rebalancing Agent** | Spatial Corridor Routing & Congestion Relief | `get_spatial_neighbors()`, `dispatch_reroute_guidance()` | When MG Road hits 94.7%, identifies Indiranagar (3.8 km away, 70 open bays) and dispatches a 30% detour advisory via digital road signs. |
| **Capacity Allocation Agent** | Fair Slot Reservation & Anti-Gouging Compliance | `allocate_overflow_bays()`, `verify_statutory_rates()` | Reserves buffer capacity at destination lots so diverted cars have guaranteed spots; enforces standard ₹50/hr rates with zero surge pricing. |
| **Hardware Diagnostic Agent** | Self-Healing IoT & Kafka DLQ Triage | `inspect_dlq_anomalies()`, `quarantine_sensor()` | Detects corrupt sensor telemetry (e.g. `Lat: 999.0`), isolates bad hardware from the stream pipeline, and logs BBMP maintenance work orders. |

---

## ⚡ The 4 Cognitive Pillars of Agentic AI

### 1. Three-Tier Memory Hierarchy
- **Short-Term Working Memory (RAM):** Retains real-time 1-minute streaming aggregations, occupancy percentages, and active alerts.
- **Episodic Memory (`data/episodic_memory.jsonl`):** A persistent JSON Lines record storing every past event, the agents involved, the tools executed, and the post-intervention reflection score.
- **Long-Term Knowledge Base:** Spatial road graph of Bengaluru (inter-lot distances, transit times, corridor connections) and municipal statutory bylaws.

### 2. Multi-Agent Negotiation (Pareto Optimality)
Autonomous agents rarely have identical objectives:
- The **Traffic Worker** seeks to clear congestion immediately by diverting large volumes of vehicles.
- The **Capacity Allocation Worker** protects neighboring residential and commercial lots from sudden overflow.
- The **Agent Negotiator** mediates mathematically between them to find a Pareto-optimal equilibrium (e.g., capping the diversion to 30% to maintain equilibrium across both corridors).

### 3. Concrete Tool Execution (Function Calling)
Unlike conversational chatbots that only output text, these agents have **autonomous hands**:
- `dispatch_reroute_guidance(source, target, divert_percentage)`: Updates Variable Message Signs (VMS) on city expressways.
- `quarantine_sensor(lot_id, slot_id, fault_type)`: Flags faulty hardware in the state machine and prevents database contamination.
- `allocate_overflow_bays(lot_id, bay_count)`: Dynamically locks reserve slots for inbound redirected traffic.

### 4. Closed-Loop Reflection & Introspective Learning
Traditional automation executes and forgets. This agentic system features **introspective closed-loop evaluation**:
1. When an action is taken, pre-intervention metrics ($O_{pre}, V_{pre}$) are checkpointed.
2. After 3 minutes, the subsequent streaming micro-batch is evaluated ($O_{post}, V_{post}$).
3. The system computes a normalized reflection score:
   $$\text{Score} = \min\left(1.0, \frac{O_{pre} - O_{post}}{10.0}\right)$$
4. A score of **`+1.0 (SUCCESS)`** validates that occupancy dropped (e.g., from 94.7% to 81.3%), committing the validated strategy to Episodic Memory.

---

## 💻 Visual Interfaces

### 1. Autonomous Web Command Center (`http://localhost:5000`)
- **Split-Screen Design:** Left side displays live occupancies across 8 Bengaluru parking corridors; right side displays the **Live Multi-Agent Thought Stream**.
- **Interactive Action Triggers:**
  - `Simulate Rush Hour Jam (MG Road 95%)`: Triggers gridlock; watch agents coordinate and reroute traffic.
  - `Simulate Sensor Hardware Failure`: Injects corrupt GPS telemetry; watch the Diagnostic Worker isolate the sensor and log a repair ticket.
  - `Run Reflection Loop (+1.0)`: Evaluates post-intervention metrics and records the episode.
  - `Reset Equilibrium`: Restores city lots to standard baseline flow.

### 2. Live Grafana Telemetry Dashboard (`http://localhost:3001`)
- **Real-Time Synchronization:** Line-protocol writes to InfluxDB update Grafana instantly.
- **Key Panels:**
  - *Occupancy by Parking Lot:* Bar chart tracking all 8 facilities.
  - *Occupancy by Geographical Zone:* Central, East, North, and South corridors.
  - *Entries / Exits per Minute:* 1-minute tumbling window velocities.
  - *Throughput & Pipeline Latency:* Real-time streaming performance metrics.

---

## 🛠️ Quickstart: Run in 3 Steps

### Prerequisites
- Python 3.10+
- Docker Desktop running

### Step 1: Start Docker Containers
```powershell
docker compose up -d
```
*(Starts Kafka KRaft on port 9092, InfluxDB on port 8086, and Grafana on port 3001).*

### Step 2: Start the Web Command Center
```powershell
python -m web.app
```
Open **`http://localhost:5000`** in your browser.

### Step 3: Run the Autonomous Demo or Test Suite
```powershell
# Run the terminal multi-agent demonstration
python -m agents.orchestrator --demo

# Run the complete test suite (58/58 tests pass in ~0.25s)
python tests/run_all_tests.py
```

---

## 📁 Repository Structure

```text
agentic-ai/
├── agents/                          # Cognitive Multi-Agent Subsystem
│   ├── cwd/                         # Coordinator, Delegator, Workers, Negotiator
│   │   ├── coordinator.py           # Supervisory authority & legal governance
│   │   ├── delegator.py             # Event triage & worker assignment
│   │   ├── negotiator.py            # Pareto-optimal inter-agent negotiation
│   │   └── workers.py               # Traffic, Capacity Allocation & Diagnostic agents
│   ├── memory/                      # Three-Tier Memory Hierarchy
│   │   ├── working.py               # Ephemeral RAM state
│   │   ├── episodic.py              # Persistent JSONL journal & reflection history
│   │   └── knowledge_base.py        # Spatial graph & municipal statutory bylaws
│   ├── tools/                       # Typed Tool Registry & Function Schemas
│   │   ├── registry.py              # Tool execution engine
│   │   └── definitions.py           # Reroute, quarantine, and allocation tools
│   ├── reflection/                  # Closed-Loop Introspective Evaluation Engine
│   │   └── introspector.py          # Delta calculation & reflection scoring (+1.0)
│   ├── mcp/                         # Model Context Protocol (MCP) Server
│   │   └── server.py                # JSON-RPC 2.0 stdio server for LLM tools
│   └── orchestrator.py              # Cognitive master loop & demo CLI
│
├── web/                             # Web Command Center
│   ├── app.py                       # Flask server with instant InfluxDB dual-sync
│   └── templates/index.html         # Responsive split-screen command center
│
├── streaming/                       # Spark Structured Streaming Core Engine
│   ├── main.py                      # Pipeline bootstrap & execution graph
│   ├── event_time.py                # Authoritative 2-minute watermarking
│   ├── windowing.py                 # 1-min tumbling & 5-min sliding aggregations
│   ├── deduplication.py             # Watermarked stateful deduplication
│   └── stateful_tracker.py          # Slot-level Finite State Machine (FSM)
│
├── simulator/                       # Virtual IoT Sensor Network Simulator
│   ├── main.py                      # Normal (50 ev/s), High-Load (500 ev/s), Failure
│   ├── generator.py                 # Probabilistic slot event generator
│   └── parking_lot.py               # 8 Bengaluru facility models
│
├── storage/                         # Time-Series Persistence
│   ├── influx_client.py             # HTTP REST Line Protocol client
│   └── schema.py                    # Point definitions & measurements
│
├── tests/                           # 58 Automated Tests
│   ├── run_all_tests.py             # Master test runner (unit, integration, agents)
│   └── unit/test_agents.py          # Complete tests for CWD, memory, tools, & reflection
│
├── WHAT_AGENTS_DO.md                # Plain-English guide to the Agentic AI layer
├── HOW_TO_RUN.md                    # Step-by-step beginner run guide
└── docker-compose.yml               # Kafka, InfluxDB, and Grafana containers
```

---

## 🧪 Verification & Test Coverage

Run the automated test suite anytime:
```powershell
python tests/run_all_tests.py
```

```text
=================================================================
      SMART PARKING COGNITIVE NETWORK -- TEST SUITE
=================================================================
Tests Run:       58
Errors:          0
Failures:        0
Skipped:         2 (offline broker mocks)
Execution Time:  0.25 seconds
=================================================================
[SUCCESS] ALL TESTS PASSED!
```
The test suite validates:
- CWD multi-agent role assignment, delegation, and Pareto negotiation.
- Three-tier memory persistence and episodic retrieval.
- Tool registry function calling and statutory parameter bounds.
- Closed-loop reflection delta calculations and scoring.
- Spark 2-minute watermarking, tumbling windows, and slot state transitions.
