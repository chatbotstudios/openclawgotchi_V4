# AIPET Mesh Swarm: Implementation Plan

This document outlines the architecture and execution strategy for the **AIPET Mesh Swarm Connectivity** feature. The goal is to create a unified, gamified ecosystem where diverse hardware nodes (Raspberry Pi, Mac/PC, ESP32, Arduino) can communicate, share intelligence, and compete.

## Open Questions for Review
> [!NOTE]
> 1. **Transport Layer**: I propose using **MQTT** as the core communication protocol, as it is extremely lightweight and universally supported by ESP32s, Arduinos, and Python. Would you prefer a local broker (like Mosquitto running on the Alpha-Claw) or a cloud-based broker (like HiveMQ/AWS IoT) for global swarms?
> 2. **Competition Metrics**: Currently, the plan proposes competing on *XP earned today* and *Handshakes captured*. Are there other metrics you want on the leaderboard?

---

## 1. Core Architecture

The Mesh Swarm will operate on a Publisher/Subscriber (Pub/Sub) model using MQTT. The `openclawgotchi_V4` (Alpha-Claw) will act as the primary orchestrator, while smaller nodes (Nano-Claws like ESP32) will act as edge sensors.

### Communication Channels (MQTT Topics)
- `aipet/swarm/discovery`: Nodes broadcast their existence and base stats (Level, XP, Hardware type).
- `aipet/swarm/intel`: Nodes share captured data (IoT MACs, WPA handshakes, BLE beacons).
- `aipet/swarm/achievements`: Broadcasts for Level-Ups, completed missions, and rare discoveries.

---

## 2. Gamified Engine Features

The Swarm will directly hook into the Phase 4 Game Engine.

### 🧩 Swarm Missions
We will activate the "Social" mission category.
- **Data Donor**: Gain XP by successfully publishing validated IoT intelligence to `aipet/swarm/intel`.
- **First Contact**: Massive one-time XP bounty for successfully establishing a two-way handshake with a new, unseen AIPET node.
- **Swarm Coordinator**: XP granted to the Alpha-Claw for successfully aggregating data from 3+ different Nano-Claws in a single session.

### 🏆 Swarm Leaderboards & Competition
A new SQLite table (`aipet_swarm_nodes`) will track discovered peers.
- **The Alpha Designation**: The AIPET with the highest Level in the local mesh automatically claims the "Alpha" title, unlocking a unique E-Ink crown/icon.
- **Radio Wars**: When two AIPETs are in the same mesh, they enter a "Radio War". The node that pushes the most unique handshakes to the swarm in a 24-hour period wins bonus RP (Reputation Points).

### 📢 Achievement Broadcasting
When an AIPET levels up or completes a Tier 5 progressive mission, it publishes an achievement packet. Other AIPETs in the swarm will:
1. Log the achievement in their memory.
2. Display a brief congratulatory (or jealous) kaomoji on their E-Ink/CLI dashboard.

---

## 3. Implementation Steps

### Step 1: The Swarm Client (`src/game_engine/swarm.py`)
- Implement a lightweight, async MQTT client using `paho-mqtt`.
- Create background listeners for the `aipet/swarm/#` topics.
- Implement the discovery broadcast loop (pinging presence every 5 minutes).

### Step 2: The Data Standard (JSON Schemas)
Define strict Pydantic models for Swarm packets to ensure Arduinos/ESP32s know exactly how to format their payloads.
```json
{
  "node_id": "alpha-claw-01",
  "hardware": "rpi-zero-2w",
  "level": 4,
  "payload_type": "achievement",
  "data": {
    "event": "level_up",
    "message": "Reached Level 5!"
  }
}
```

### Step 3: Game Engine Hooks (`plugins/swarm_hooks.py`)
- Wire up the `@hook` system to automatically trigger MQTT broadcasts.
- `@hook("game.level_up")` -> publishes to `aipet/swarm/achievements`.
- `@hook("swarm.intel_received")` -> increments the `Data Donor` mission progress.

### Step 4: Swarm CLI & UI
- Add `gotchi swarm status`: Lists all active peers, their levels, and the current Alpha.
- Add `gotchi swarm leaderboard`: Renders the competitive ranking of all nodes.

---

## Verification Plan
1. Stand up a local Mosquitto MQTT broker.
2. Launch two separate instances of `openclawgotchi` (or simulate an ESP32 via a python script).
3. Verify discovery: Run `gotchi swarm status` and ensure both nodes see each other.
4. Verify Gamification: Force one node to level up via `gotchi aipet add-xp`, and verify the second node receives the achievement packet and logs it.
