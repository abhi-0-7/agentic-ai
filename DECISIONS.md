# DECISIONS — Smart Parking Occupancy Analytics
**Course:** AI372IA — Stream Processing and Analytics  
**Institution:** RV College of Engineering, Bengaluru  
**Last Updated:** 2026-11-01T15:40:00+05:30  

---

## D-001: Python Version — Python 3.10+ / 3.13
**Decision:** Use the host system Python environment.  
**Reason:** PySpark 3.5.1 and kafka-python 2.2.11 are fully supported and verified. Type hints use `from __future__ import annotations` for seamless backwards and forwards compatibility.

## D-002: Kafka Client — kafka-python (Pure Python)
**Decision:** Use `kafka-python` as the primary Kafka client for producers and test runners.  
**Reason:** Pure Python implementation eliminates external C-library (`librdkafka`) DLL compilation dependencies on Windows. Delivers predictable throughput scaling past 1,000 events/sec.

## D-003: Spark Kafka Integration — spark-sql-kafka-0-10 Connector
**Decision:** Use the official `org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1` connector.  
**Reason:** Provides native micro-batch and continuous Kafka consumption with full access to Kafka partition offsets, message keys, and headers.

## D-004: Java Runtime — OpenJDK 8 (Temurin)
**Decision:** Configure `JAVA_HOME` pointing to OpenJDK 8u492.  
**Reason:** Proven, rock-solid JVM runtime required by Apache Spark 3.5.1 and Py4J gateway on Windows host.

## D-005: Docker Kafka Deployment — KRaft Mode (No ZooKeeper)
**Decision:** Deploy Kafka using KRaft (Kafka Raft Metadata mode).  
**Reason:** Simplifies architecture to a single container, reduces RAM budget by eliminating ZooKeeper (~256 MB overhead), and mirrors modern production standards.

## D-006: InfluxDB Storage — Version 2.7 OSS
**Decision:** Use InfluxDB 2.7 OSS with HTTP Line Protocol fallback.  
**Reason:** Native time-series database with nanosecond precision, Flux query capabilities, and zero external dependency footprint via lightweight REST line-protocol writing.

## D-007: Visualisation — Grafana 11.5 / 10.4
**Decision:** Deploy Grafana with automated provisioning of datasources and dashboards.  
**Reason:** Enables hands-off deployment: upon container boot, the InfluxDB Flux datasource and 24-panel dashboard are automatically imported and ready for evaluation.

## D-008: Spark Deployment Mode — Local[*]
**Decision:** Run Spark in `local[*]` mode with 4 shuffle partitions (`spark.sql.shuffle.partitions=4`).  
**Reason:** Single-laptop hardware constraint (Intel Core i7-12700H, 16 GB RAM). Conserves memory while executing true multi-threaded parallel stream processing across CPU cores.

## D-009: Stateful Slot Occupancy Tracking — In-Memory FSM with Idempotent Upserts
**Decision:** Process micro-batches deterministically using a per-slot Finite State Machine (`StatefulOccupancyTracker`).  
**Reason:** Tracks state transitions (`FREE` $\rightarrow$ `OCCUPIED` and `OCCUPIED` $\rightarrow$ `FREE`), computes net delta counts, and generates lot-level occupancy percentages without double-counting.

## D-010: Watermark Policy — Configurable 2 Minutes Allowed Lateness
**Decision:** Default watermark is set to 2 minutes (`event_timestamp` allowed lateness).  
**Reason:** Provides a realistic allowance for wireless IoT sensor packet delays while strictly bounding Spark's in-memory state store to prevent memory leaks.

## D-011: Kafka Partitioning Strategy — Key = lot_id
**Decision:** Partition Kafka topics by `lot_id` across 4 partitions.  
**Reason:** Preserves strict per-lot FIFO event ordering across micro-batches, preventing out-of-order race conditions for consecutive sensor transitions.

## D-012: Checkpoint Management — Local Directory with Clean Reset Utility
**Decision:** Store query checkpoints in `./checkpoints/`, managed via `scripts/reset.py --force`.  
**Reason:** Guarantees fault tolerance and exactly-once processing resumption across restarts, with an automated utility to wipe state cleanly between distinct evaluation runs.

## D-013: Dual Ingestion Strategy — Synthetic Simulator & Live REST API
**Decision:** Provide both a realistic synthetic IoT simulator (8 Bengaluru zones, diurnal waves) and a live external smart parking open-data REST API producer with API key authentication.  
**Reason:** Satisfies both deterministic academic stress testing (100 to 1,000 ev/s) and live real-world external streaming evaluation.

## D-014: Single Authoritative Watermark Architecture
**Decision:** Declare the event-time watermark exactly once on `valid_stream` immediately following schema validation.  
**Reason:** Spark 3.5 introduced strict watermark validation: calling `.withWatermark()` multiple times on the same stream graph triggers `AnalysisException: Redefining watermark is disallowed`. Centralizing the watermark in `streaming/event_time.py` satisfies deduplication and windowing simultaneously.

## D-015: Dual-Schema InfluxDB Persistence for Telemetry Compatibility
**Decision:** Spark synchronously emits snapshots to both `parking_occupancy` & `parking_occupancy_window` and `stream_performance` & `parking_processing`.  
**Reason:** Guarantees that any Grafana dashboard template (whether querying primary tables or historical window-specific views) renders real-time data without schema conflicts.

## D-016: Windows Console CP1252 Character Encoding Resiliency
**Decision:** Standardize all terminal CLI outputs to pure ASCII indicators (`[OK]`, `[INFO]`, `[ERROR]`).  
**Reason:** Prevents `UnicodeEncodeError` crashes on default Windows PowerShell environments using the CP1252 code page.

## D-017: Coordinator-Worker-Delegator (CWD) Multi-Agent Architecture
**Decision:** Implement the CWD pattern with specialized Worker agents (Traffic, Pricing, Diagnostics), an automated Delegator, and a supervisory Coordinator.  
**Reason:** Mandated by Unit III and IV of the AI373TA syllabus. Establishes clean separation of concerns: task decomposition is decoupled from execution and global system governance.

## D-018: Three-Tier Agent Memory Architecture
**Decision:** Implement volatile Short-Term Working Memory (`WorkingMemory`), persistent JSONL Episodic Memory (`EpisodicMemory`), and static domain Knowledge Base (`ParkingKnowledgeBase`).  
**Reason:** Fulfills Unit IV memory requirements. Working memory enables instant reactive decisions, episodic memory powers retrospective reflection, and the knowledge base guarantees strict compliance with BBMP municipal bylaws.

## D-019: Pareto-Optimal Inter-Agent Conflict Resolution
**Decision:** Implement formal negotiation (`AgentNegotiator`) to mediate between competing TrafficWorker and PricingWorker objectives.  
**Reason:** Solves real-world multi-agent coordination deadlocks: balances traffic diversion with moderated surge pricing and destination off-peak discounts, ensuring commuters adhere to rerouting advisories.

## D-020: Model Context Protocol (MCP) Standards Compliance
**Decision:** Implement a JSON-RPC 2.0 MCP Server (`ParkingMCPServer`) exposing parking state as Resources, management actions as Tools, and workflows as Prompts.  
**Reason:** Fulfills Unit V of the syllabus. Provides open interoperability, allowing any LLM client (Claude Desktop, Antigravity, custom agents) to autonomously interact with the parking network.

## D-021: Closed-Loop Reflection via Stream Introspection
**Decision:** Implement an automated introspective evaluation engine (`Introspector`) that quantifies the impact of agent interventions on subsequent stream micro-batches.  
**Reason:** Fulfills Course Outcome CO2. Binds the Agentic AI and Stream Processing layers into a true cyber-physical closed loop, empirically validating decision efficacy.
