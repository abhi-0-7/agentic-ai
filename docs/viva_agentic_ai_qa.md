# Viva Examination & Defense Q&A: Agentic AI
## Smart Parking Autonomous Mobility & Cognitive Network
**Course Title:** Agentic Artificial Intelligence  
**Course Code:** AI373TA (Semester VII, Professional Core Elective - IV)  
**Institution:** RV College of Engineering, Bengaluru  

---

### Q1: What fundamentally distinguishes this Agentic AI system from Traditional Machine Learning and Generative AI?
**Answer:**
- **Traditional ML** is primarily predictive and static (e.g. predicting whether a parking lot will be full in 30 minutes based on historical features); it does not take autonomous actions or perceive dynamic feedback loops.
- **Generative AI** generates text or media from a prompt (e.g. ChatGPT writing an explanation of parking rules), but lacks agency, autonomous goal-seeking behavior, and direct cyber-physical tool manipulation.
- **Agentic AI** combines perception, autonomous decision-making, tool execution, memory, and reflection. In our project, the agents continuously observe streaming Kafka/Spark telemetry, negotiate solutions to traffic spikes, execute real tools (rerouting, surge pricing, sensor quarantine), and introspectively evaluate whether their interventions reduced congestion.

---

### Q2: How is the Coordinator-Worker-Delegator (CWD) pattern implemented in your architecture?
**Answer:**
The CWD pattern partitions responsibilities:
1. **Coordinator Agent:** Supervisory authority holding the global objective (maintain city occupancy between 60% and 85%, avoid gridlock, uphold BBMP regulations).
2. **Delegator Agent:** Ingests streaming threshold triggers and assigns tasks to specialized workers based on domain competence.
3. **Worker Agents:**
   - *TrafficWorker:* Spatial rerouting and corridor balancing using topological road graphs.
   - *PricingWorker:* Micro-economic demand throttling through surge tariffs.
   - *DiagnosticWorker:* DLQ error triage and faulty IoT sensor isolation.

---

### Q3: What is the significance of Inter-Agent Negotiation, and what conflict does it resolve?
**Answer:**
When critical congestion occurs (>90% occupancy), the TrafficWorker and PricingWorker have conflicting domain incentives:
- TrafficWorker proposes rerouting 30% of traffic from MG Road to Indiranagar.
- PricingWorker proposes raising tariffs at MG Road by 2.0x, but might also raise rates at Indiranagar due to incoming traffic.
- If both act independently, drivers arriving at Indiranagar would be hit with surprise surge prices, undermining compliance with the rerouting signs.
The `AgentNegotiator` mediates a **Pareto-Optimal Compromise**:
1. Approves the traffic reroute to Indiranagar.
2. Moderates the MG Road surge to 1.35x to avoid panic traffic diversion into residential side streets.
3. Locks Indiranagar tariffs at baseline 1.0x (providing an explicit economic incentive for diverted commuters).

---

### Q4: Explain the Three-Tier Memory Architecture used in your project.
**Answer:**
Per Unit IV of the syllabus, the system implements three memory tiers:
1. **Short-Term Memory (Working Memory):** High-speed in-memory store (`WorkingMemory`) holding volatile micro-batch occupancy metrics, rolling velocities, active threshold alerts, and quarantined sensor IDs with TTL management.
2. **Episodic Memory:** Persistent JSONL log (`data/episodic_memory.jsonl`) recording chronological intervention episodes: trigger events, participating agents, executed actions, pre-action metrics, post-action reflection scores, and retrospective summaries.
3. **Long-Term Memory (Knowledge Base):** Static domain knowledge (`ParkingKnowledgeBase`) storing the 8-node Bengaluru spatial distance graph, road transit times, and BBMP municipal bylaws (statutory price floors and ceilings).

---

### Q5: How does the system implement Closed-Loop Reflection and Introspection?
**Answer:**
Per Unit II and Course Outcome CO2, after an intervention is executed, the episode is marked as `PENDING_EVALUATION`. The `Introspector` inspects subsequent streaming micro-batches, calculates the quantitative change in occupancy and entry velocity:
$$\Delta \text{Occupancy} = \text{Occupancy}_{pre} - \text{Occupancy}_{post}$$
It computes an empirical Reflection Score ($+1.0$ for successful relief, $+0.5$ for stabilization, $-0.5$ for adverse worsening) and updates the persistent episode record with lessons learned to guide future planning.

---

### Q6: How does the Model Context Protocol (MCP) integrate into this project?
**Answer:**
Per Unit V, the system exposes a standards-compliant JSON-RPC 2.0 Model Context Protocol (MCP) server (`agents/mcp/server.py`):
- **MCP Resources:** URIs such as `parking://system/status`, `parking://lots/{lot_id}`, and `parking://dlq/anomalies` allowing any LLM client to inspect real-time system state.
- **MCP Tools:** Typed tools such as `adjust_dynamic_tariff`, `dispatch_reroute_guidance`, and `quarantine_sensor` callable by AI clients.
- **MCP Prompts:** Pre-defined reasoning workflows like `diagnose_congestion` and `audit_sensor_health`.

---

### Q7: How do the Stream Processing (SPA) and Agentic AI layers interact?
**Answer:**
The two layers form a closed-loop cyber-physical system:
1. **Sensory Ingestion (SPA):** Spark Structured Streaming continuously processes raw IoT sensor events from Kafka, filters malformed records to DLQ, applies watermarks, and computes windowed occupancies and velocities.
2. **Cognitive Perception (Agentic AI):** The Master Orchestrator ingests these micro-batch updates and DLQ alerts into Working Memory.
3. **Autonomous Action (Agentic AI):** The CWD multi-agent system reasons, negotiates, and executes mitigation tools.
4. **Physical Feedback (SPA):** Diverted traffic and throttled demand alter the incoming raw sensor stream in subsequent Spark micro-batches, which the Agentic AI introspectively measures.

---

### Q8: What happens if an external LLM API is offline or unavailable?
**Answer:**
The Agentic AI layer is designed with a **Hybrid / Dual-Engine Architecture**. It features an offline deterministic heuristic and rule-based decision engine that executes the CWD coordination, negotiation, tool calling, and reflection with 100% functionality without requiring external network access or paid LLM tokens. When LLM API keys (Gemini / OpenAI) are provided, it dynamically enhances the reasoning steps with natural language rationale.

---

### Q9: How does the Diagnostic Worker handle sensor anomalies from the DLQ?
**Answer:**
When Spark schema validation rejects an event (e.g. GPS coordinates outside Karnataka: Lat=999.0, Lon=-999.0), it is quarantined to `parking-events-dlq`. The `DiagnosticWorker` inspects the error payload, classifies the fault (`CORRUPT_GPS_COORDINATES`, `STUCK_MAGNETIC_REED`), invokes the tool `quarantine_sensor` to isolate the slot from affecting downstream occupancy counts, and generates an automated municipal repair work order (`TICK_BBMP_*`).

---

### Q10: How are agent decisions visualized for human operators?
**Answer:**
The Orchestrator writes all agent decisions and telemetry points to InfluxDB measurement `agent_actions`. A dedicated **Row 500: Cognitive Agentic AI & Autonomous Operations** in the Grafana dashboard visualizes:
1. Live table of active autonomous agent interventions with rationales.
2. Dynamic surge pricing multiplier gauges per lot.
3. Traffic diversion advisory percentages.
4. Quarantined sensor counts and maintenance tickets.
