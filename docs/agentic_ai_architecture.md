# Agentic AI Cognitive Layer Architecture
## Smart Parking Autonomous Mobility & Telemetry Network
**Course Title:** Agentic Artificial Intelligence  
**Course Code:** AI373TA (Semester VII, Professional Core Elective - IV)  
**Institution:** RV College of Engineering, Bengaluru  

---

## 1. Executive Summary & Syllabus Alignment

While the underlying data pipeline performs distributed **Stream Processing and Analytics (AI372IA)** using Apache Spark Structured Streaming, Kafka, and InfluxDB, this document details the autonomous **Agentic Artificial Intelligence Layer (AI373TA)** built directly on top of the streaming substrate.

The Agentic AI layer transforms the passive monitoring system into a **self-governing, autonomous cyber-physical smart city management system**. It perceives streaming telemetry, reasons over municipal bylaws and spatial graphs, resolves multi-agent conflicts, executes concrete tools, and evaluates the efficacy of its interventions via closed-loop introspection.

### Syllabus Coverage Matrix (AI373TA)

| Syllabus Unit | Core Concepts Mandated | Project Implementation |
| :--- | :--- | :--- |
| **Unit I** | Self-governance, agency, autonomy; Traditional ML vs. GenAI vs. Agentic AI | Autonomous decision loop in `agents/orchestrator.py`; closed-loop action execution without human micro-management. |
| **Unit II** | Deliberative, Reactive, Hybrid Architectures; Multi-Agent Systems (MAS); Planning | Hybrid architecture combining reactive stream alerts with deliberative spatial rebalancing in `agents/cwd/`. |
| **Unit III** | Tool use & function calling; CWD Model; Role assignments; Negotiation & conflict resolution | Typed tools in `agents/tools/parking_tools.py`; Pareto-optimal mediation in `agents/cwd/negotiator.py`. |
| **Unit IV** | Implementing CWD; 3-Tier Memory (Working, Episodic, Knowledge Base); Context management | Short-Term (`short_term.py`), Episodic (`episodic.py`), and Long-Term Knowledge Base (`knowledge_base.py`). |
| **Unit V** | Model Context Protocol (MCP): Core components, Transport layer, Server lifecycle | Standards-compliant JSON-RPC 2.0 MCP Server in `agents/mcp/server.py` exposing Tools, Resources, and Prompts. |

---

## 2. Architectural Blueprint

```text
 ┌────────────────────────────────────────────────────────────────────────┐
 │                   SPARK STRUCTURED STREAMING SUBSTRATE                 │
 │   Micro-batch Aggregations, Tumbling/Sliding Windows, Watermarking     │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │ Micro-batch Occupancy & DLQ Alerts
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                      MASTER COGNITIVE ORCHESTRATOR                     │
 │                     (`agents/orchestrator.py`)                         │
 └───────┬────────────────────────────────────────────────────────┬───────┘
         │ Updates Telemetry State                                │
         ▼                                                        ▼
 ┌───────────────────────────────┐        ┌───────────────────────────────┐
 │   THREE-TIER AGENT MEMORY     │        │ COORDINATOR-WORKER-DELEGATOR  │
 │                               │        │       (CWD) MULTI-AGENT       │
 │ 1. Short-Term Working Memory  │        │                               │
 │    • Active lot occupancies   │        │ ┌───────────────────────────┐ │
 │    • Rolling velocities       │        │ │     COORDINATOR AGENT     │ │
 │    • In-flight interventions  │◄───────┤ │(Supervisory City Objective│ │
 │                               │        │ └─────────────┬─────────────┘ │
 │ 2. Episodic Memory (JSONL)    │        │               │               │
 │    • Chronological episodes   │        │ ┌─────────────┴─────────────┐ │
 │    • Decision audit logs      │        │ │      DELEGATOR AGENT      │ │
 │    • Post-hoc reflections     │        │ │ (Task Decomposition Logic)│ │
 │                               │        │ └──────┬──────┬──────┬──────┘ │
 │ 3. Long-Term Knowledge Base   │        │        │      │      │        │
 │    • BBMP Statutory Bylaws    │        │        ▼      ▼      ▼        │
 │    • 8-node Bengaluru Graph   │        │     [TRAFFIC][PRICING][DIAG]  │
 │    • Diurnal rush hour models │        │        │      │      │        │
 └───────────────────────────────┘        │        └──────┴──────┘        │
                                          │               │               │
                                          │               ▼               │
                                          │     [AGENT NEGOTIATOR]        │
                                          │  (Pareto-Optimal Consensus)   │
                                          └───────────────┬───────────────┘
                                                          │
                                                          ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                    CONCRETE TOOL EXECUTION LAYER                       │
 │  • dispatch_reroute_guidance()     • adjust_dynamic_tariff()           │
 │  • quarantine_sensor()             • inspect_dlq_anomalies()           │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                   CLOSED-LOOP REFLECTION & INTROSPECTION               │
 │                      (`agents/reflection/introspector.py`)             │
 │  • Re-evaluates target lot after T_eval stream time.                   │
 │  • Computes Delta: Occupancy reduction & velocity deceleration.        │
 │  • Assigns normalized Reflection Score (+1.0 Success, 0.0, -1.0 Fail). │
 │  • Updates episode in Episodic Memory with lessons learned.            │
 └────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Component Decomposition

### 3.1 The Coordinator-Worker-Delegator (CWD) Model (Units III & IV)
The CWD model organizes autonomous agents into clearly partitioned roles:

1. **Coordinator Agent (`CoordinatorAgent`):**
   - **Role:** Supervisory executive. Holds the system-wide utility function: maintaining city-wide occupancy between 60% and 85%, preventing gridlock, and ensuring statutory compliance.
   - **Authority:** Validates all worker and negotiated proposals, authorizes tool execution, and records persistent episodes.

2. **Delegator Agent (`DelegatorAgent`):**
   - **Role:** Task decomposition and routing.
   - **Logic:**
     - `Occupancy >= 90%` $\implies$ Critical Gridlock $\implies$ Parallel delegation to both Traffic and Pricing Workers for joint multi-agent negotiation.
     - `85% <= Occupancy < 90%` $\implies$ High Congestion $\implies$ Delegated to Traffic Worker.
     - `80% <= Occupancy < 85%` $\implies$ Surge Demand $\implies$ Delegated to Pricing Worker.
     - `DLQ Ingestion Alert` $\implies$ Sensor Fault $\implies$ Delegated to Diagnostic Worker.

3. **Specialized Worker Agents:**
   - **TrafficWorker:** Utilizes the spatial knowledge graph to find candidate parking facilities with $>15$ spare slots and $<75\%$ occupancy, computing variable message sign (VMS) traffic diversion ratios.
   - **PricingWorker:** Uses micro-economic demand elasticity to formulate proportional surge multipliers ($1.0\times$ to $2.0\times$) while verifying BBMP legal price ceilings.
   - **DiagnosticWorker:** Analyzes quarantined payloads from Kafka DLQ, classifies failure signatures (e.g. `CORRUPT_GPS_COORDINATES`, `STUCK_MAGNETIC_REED`), isolates the faulty sensor, and files BBMP work orders.

### 3.2 Inter-Agent Negotiation & Conflict Resolution (Unit III)
When a critical surge occurs, TrafficWorker (which wants to divert commuters to Lot B) and PricingWorker (which wants to raise tariffs at Lot A and potentially Lot B) have competing incentives.

`AgentNegotiator` implements a **Pareto-Optimal Compromise**:
1. Approves the traffic diversion advisory to the destination lot.
2. Moderates the origin lot's price surge to $1.35\times$ (discouraging new arrivals without causing panic traffic spillover).
3. Locks the destination lot's tariff at baseline $1.0\times$ (or a $10\%$ discount), providing an explicit economic incentive for drivers to obey the rerouting recommendation.

### 3.3 Three-Tier Agent Memory Architecture (Unit IV)
- **Short-Term Working Memory (`WorkingMemory`):** Volatile, high-speed RAM store holding active micro-batch occupancy metrics, rolling velocities, active threshold alerts, and quarantined sensor tables with TTL management.
- **Episodic Memory (`EpisodicMemory`):** Append-only, structured JSONL journal (`data/episodic_memory.jsonl`). Each episode logs the trigger event, participating agents, proposed actions, negotiated compromises, executed tools, pre-action metrics, post-action reflection scores, and retrospective summaries.
- **Long-Term Knowledge Base (`ParkingKnowledgeBase`):** Static domain representation containing:
  - 8-node Bengaluru parking topological nodes with geographic coordinates and capacities.
  - Spatial road distance matrix (distances in km, transit times in minutes).
  - BBMP municipal bylaws: minimum tariff (30 INR/hr), maximum statutory ceiling (150 INR/hr), maximum allowed multiplier ($2.5\times$).

### 3.4 Model Context Protocol (MCP) Server (Unit V)
The system exposes its internal cognitive state and tooling via an MCP Server (`agents/mcp/server.py`):
- **Transport:** JSON-RPC 2.0 over `stdio`.
- **Resources:**
  - `parking://system/status`: Real-time city capacity and occupancy overview.
  - `parking://lots/{lot_id}`: Detailed per-lot metrics and tariff status.
  - `parking://dlq/anomalies`: Quarantined sensor payloads.
  - `parking://episodes/recent`: Chronological audit trail of agent decisions.
- **Tools:** `query_stream_metrics`, `get_spatial_neighbors`, `adjust_dynamic_tariff`, `dispatch_reroute_guidance`, `quarantine_sensor`, `inspect_dlq_anomalies`.
- **Prompts:** `diagnose_congestion`, `audit_sensor_health`.

---

## 4. Closed-Loop Reflection & Introspection (Unit II, CO2)

Intelligent agency requires validating whether actions achieved their physical goals.

The `Introspector` runs a retrospective evaluation loop:
1. Identifies episodes with `status="PENDING_EVALUATION"`.
2. Inspects subsequent stream micro-batch metrics for the target facility.
3. Calculates quantitative deltas:
   $$\Delta \text{Occupancy} = \text{Occupancy}_{pre} - \text{Occupancy}_{post}$$
   $$\Delta \text{Velocity} = \text{Velocity}_{pre} - \text{Velocity}_{post}$$
4. Computes a normalized Reflection Score $S \in [-1.0, +1.0]$:
   - $S = +1.0$ (`SUCCESS`): $\Delta \text{Occupancy} \ge 4.0\%$ or $\Delta \text{Velocity} \ge 3.0/\text{min}$.
   - $S = +0.5$ (`STABILIZED`): $\Delta \text{Occupancy} \ge 0.0\%$ (overflow prevented).
   - $S = -0.5$ (`ADVERSE`): Occupancy continued rising despite intervention.
5. Updates the episode record in Episodic Memory with the evaluation score and generated explanation.
