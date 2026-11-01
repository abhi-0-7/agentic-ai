# 🚀 How to Run the Entire Project (Beginner-Friendly Guide)

> **Hey there! 👋** Don't worry if all the big words sound complicated.  
> Think of this project like a **Smart City Toy Set**:
> 1. **Cars & Sensors (IoT Simulator):** Virtual cars parking in 8 lots across Bengaluru.
> 2. **Post Office (Kafka):** Carries sensor messages super fast without dropping them.
> 3. **Super-Fast Calculator (Spark):** Counts how full each parking lot is every 5 seconds.
> 4. **Robotic City Boss (Agentic AI):** Autonomous agents that reroute cars and fix problems before roads get jammed!
> 5. **Big TV Screen (Grafana):** A live dashboard with colourful dials and graphs.
>
> 📖 **Curious about what the AI Agents actually do?** Read [`WHAT_AGENTS_DO.md`](file:///c:/Users/Abhishek/Downloads/agentic%20ai/WHAT_AGENTS_DO.md) for a complete explanation.
>
> Follow these steps one by one. You will have everything running in under 5 minutes!

---

## 🛠️ Step 0: Open Docker Desktop First!

Before touching the terminal:
1. Click your Windows Start button.
2. Search for **Docker Desktop** and click it to open.
3. Wait about 30 seconds until the bottom-left icon in Docker Desktop turns **Green** (meaning *"Docker is running"*).

---

## 🖥️ The 4-Terminal Setup

You will open **3 or 4 PowerShell windows** (or tabs).  
In every terminal, make sure you are in this project folder:
```powershell
cd "C:\Users\Abhishek\Downloads\agentic ai"
```

---

### 🟢 Terminal 1: Start the Background Servers (Docker)

This starts Kafka, InfluxDB, and Grafana in the background.

```powershell
docker compose up -d
```

**How to know it worked:**  
You will see 3 green checkmarks:
- `[+] Running 3/3` (kafka, influxdb, grafana are started!)

*(If it's your first time, wait about 15 seconds for them to wake up).*

---

### 🟠 Terminal 2: Start the Spark Brain & Agentic AI

This is the main engine. It reads the car stream, counts the slots, and activates the AI agents whenever a lot gets too full.

```powershell
python -m streaming.main
```

**What you will see on screen:**
- It will say `SparkSession ready`
- Every few seconds, you will see it processing batches of cars:
  ```text
  [INFO] Batch 0: Processed 45 events in 0.35s
  [INFO] Batch 1: Processed 80 events in 0.40s
  ```
- **Leave this terminal running!** Do not close it.

---

### 🔵 Terminal 3: Start the Virtual Cars (Simulator)

Now we need cars driving into parking lots! Run:

```powershell
python -m simulator.main --mode normal --rate 50
```

**What you will see on screen:**
- Hundreds of virtual cars entering and leaving slots across MG Road, Koramangala, Indiranagar, etc.
  ```text
  [INFO] EVENT #1: [LOT_MG_ROAD_01] Slot LOT_MG_ROAD_01-S014 -> OCCUPIED
  [INFO] EVENT #2: [LOT_INDIRANAGAR_01] Slot LOT_INDIRANAGAR_01-S008 -> FREE
  ```
- **Leave this terminal running too!**

---

### 🟣 Step 4: Open the Dashboard in Your Web Browser!

Now go see the magic live on screen:
1. Open Google Chrome, Edge, or Brave.
2. Go to this URL: **[http://localhost:3001](http://localhost:3001)**
3. If it asks to login:
   - **Username:** `admin`
   - **Password:** `parking123` (or `admin`)
4. Click on **Dashboards** $\rightarrow$ **Smart Parking Occupancy Analytics — Bengaluru**.
5. Set the top-right refresh rate to **5s**.

**What you will see:**
- Big dials showing **Total Capacity (1,000 slots)** and **Available Slots**.
- Bar charts showing which areas (MG Road, Koramangala, etc.) are getting full.
- **Scroll down to Row 500:** You will see the **Agentic AI Table** showing the robot agents making decisions (rerouting traffic, adjusting surge prices, and quarantining broken sensors)!

---

## 🌟 The Interactive Agentic AI Visual Web Dashboard (No Docker Needed!)

If you want a **full visual screen with live clickable buttons, animated cards, and real-time agent thoughts** (instead of just terminal text):

In any PowerShell window, run:
```powershell
python -m web.app
```

Then open your browser at:
👉 **[http://localhost:5000](http://localhost:5000)**

### What You Will See on the Visual Dashboard:
1. **8 Live Bengaluru Parking Lots:** Clean cards showing real-time occupancy percentages, green/yellow/red progress bars, live slot counts, and active reroute advisories.
2. **Side-by-Side Multi-Agent Brain:** Shows the 4 autonomous agents discussing and acting in real time:
   - **Coordinator Agent:** Supervises the network and executes approved tools.
   - **Traffic Rebalancing Agent:** Detects road bottlenecks and calculates optimal detour percentages.
   - **Capacity Allocation Agent:** Scans neighboring facilities (Indiranagar, Koramangala) to reserve open slots.
   - **Hardware Diagnostic Agent:** Catches corrupted IoT packets in the Kafka DLQ and isolates bad sensors.
3. **Interactive Simulation Triggers:**
   - Click **`Simulate Rush Hour Jam (MG Road 95%)`**: Watch MG Road turn red (94.7%), the agents negotiate a 30% diversion to Indiranagar, and InfluxDB sync in real time so Grafana on port 3001 jumps!
   - Click **`Simulate Sensor Hardware Failure`**: Hebbal slot S042 sends invalid coordinates; the Diagnostic Agent quarantines the bay and files a BBMP repair ticket.
   - Click **`Run Reflection Loop (+1.0)`**: Traffic diverts, MG Road drops to 81.3%, and the Reflection Agent assigns a **+1.0 (SUCCESS)** score saved to episodic memory.
   - Click **`Reset Equilibrium`**: Restores all 8 facilities to normal calm flow!

---

## 🤖 The Terminal Demo (Alternative)

If your teacher says:  
> *"Show me specifically how the Agentic AI works and makes decisions!"*

Open a new terminal window and run:
```powershell
python -m agents.orchestrator --demo
```

**Watch the screen tell an amazing story in 5 steps:**
1. **Normal Day:** 3 parking lots are at 40-60% capacity. Everything is calm.
2. **The Traffic Spike:** Suddenly, MG Road reaches **94.7% capacity** (+14 cars/min)!
3. **The AI Team (CWD) Wakes Up:**
   - **Traffic Worker** says: *"MG Road is at 94.7%! Let's divert 30% of incoming cars to Indiranagar 100ft Rd (3.8 km away, 70 open slots)!"*
   - **Allocation Worker** says: *"Checked Indiranagar! It has plenty of space. I am reserving an overflow buffer bay and ensuring standard fair municipal rates (₹50/hr)—zero price gouging!"*
   - **Coordinator Agent** executes the tool: Digital road signs update immediately to reroute drivers.
4. **Self-Healing Broken Sensor:** A broken sensor at Hebbal sends corrupt GPS coordinates (`Lat=999.0`). The **Diagnostic Worker** spots it in the Dead Letter Queue (DLQ), quarantines the bad sensor from the database, and automatically generates repair ticket `TICK_BBMP_LOT_HEBBAL_01_S042`!
5. **The AI Reflection:** 3 minutes later, the AI inspects the new micro-batch: MG Road dropped from 94.7% down to 81.3%! The AI calculates a reflection score of **+1.0 (SUCCESS)** and saves the lesson to its episodic memory!

---

## 🧪 How to Run the Automated Tests (58/58 Pass)

If your teacher asks: *"Did you write tests for this?"*  
Run this command:
```powershell
python tests/run_all_tests.py
```
**Result:** In **0.25 seconds**, all **58 tests** will pass with green `[SUCCESS] ALL TESTS PASSED!`.

---

## 💡 Quick Cheat Sheet for Questions Your Teacher Might Ask

| Teacher Asks | Simple Answer to Give |
| :--- | :--- |
| **"What does Stream Processing do here?"** | *"It uses Apache Spark and Kafka to continuously count cars and detect traffic jams every few seconds without crashing."* |
| **"What does Agentic AI do here?"** | *"Instead of just showing red alerts on a screen, autonomous agents take action: they reroute cars to empty lots, reserve overflow capacity at fair rates, and quarantine broken sensors."* |
| **"What is the CWD model?"** | *"Coordinator-Worker-Delegator. The Delegator assigns tasks, the Workers (Traffic, Capacity Allocation, Diagnostics) propose solutions, and the Coordinator approves the final plan."* |
| **"What is Inter-Agent Negotiation?"** | *"When Traffic wants to reroute cars and Allocation protects neighboring facilities from being overwhelmed, they negotiate an optimal compromise so traffic is balanced fairly."* |
| **"Where is the memory stored?"** | *"In 3 levels: Working memory in RAM, Episodic memory in `data/episodic_memory.jsonl`, and Knowledge Base with Bengaluru road maps and BBMP parking laws."* |

---

## 🛑 How to Stop Everything When You Are Done

When you are done demonstrating:
1. In the terminals where Spark or the Simulator are running, just press **`Ctrl + C`** on your keyboard to stop them.
2. In Terminal 1, run:
   ```powershell
   docker compose down
   ```
This turns off all background containers cleanly!
