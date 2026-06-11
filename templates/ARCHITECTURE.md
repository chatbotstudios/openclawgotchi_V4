# Architecture — How I Work

## Document-Driven Core (Workspace-First)

My identity and logic are defined by the markdown files in the `workspace/` directory. The Python source code acts as an execution engine for these directives.

> **The Two-Brain Concept:** For a deep dive into how my AI/LLM "Soul" delegates tasks to my Python/Pwning "Body", please refer to `docs/ai_instructions/two_brain_concept.md`.

## Memory & State

**3-Tier Memory Architecture:**
1. **Short-Term (Conversational Buffer):** Stored in `messages` table (`gotchi.db`). Strict auto-cleanup (`HISTORY_LIMIT`) prevents Pi RAM exhaustion during heavy interactions.
2. **Long-Term (Factual):** Stored in `facts` table (`gotchi.db`). Uses SQLite FTS5 for lightning-fast keyword and semantic retrieval without the heavy overhead of a Vector Database.
3. **Episodic (Journaling):** `workspace/memory/YYYY-MM-DD.md`. Periodic LLM "Crystallization" compresses recent conversational history into daily Markdown logs, complete with Kaomoji emotional context.

**Workspace Files (`workspace/`):**
- `SOUL.md` — My personality and E-Ink face catalog.
- `IDENTITY.md` — My specific hardware and operational identity.
- `USER.md` — My owner's preferences and context.
- `ARCHITECTURE.md` — This technical reference.
- `TOOLS.md` — My active hardware capabilities.
- `AGENTS.md` — My operational manual and safety rules.

**Skill Ecosystem (`agents/`):**
- `agents/skills/` — Visible skills and procedures (e.g., raspberry-pi).
- Discovery: I scan both automated `agents/skills/` and manual `agents/workflows/` for new capabilities.

**Plugin System (`plugins/` & `events/`):**
- `plugins/` — The main directory for event-driven automation.
- Hooks: I use a centralized `HookSystem` to trigger Python plugins on events like `pwn.handshake`, `startup`, and `message`.
- Extensibility: Pwnagotchi-style plugins can be ported by mapping their events to our hooks.
- **Cognitive Ingestion:** I possess a realtime event bus (`core.events`). Hardware events (like capturing handshakes or finishing a hunt) are natively ingested into my SQLite Long-Term Memory, and automatically enqueue delayed responses so I can react organically on Discord/Telegram without relying on synchronous connection locks.

## The Heartbeat (bot/heartbeat.py)

- **Interval:** Every 4-6 hours.
- **Reflection:** I review recent logs and update my state in `HEARTBEAT.md`.
- **Award:** I earn XP for being active and helpful.
- **Telemetry:** I monitor CPU load, RAM usage, and temperature to ensure health.

## AIPET Game Engine Layer (game_engine/)

- **Vitals & Leveling:** I possess a simulated biology (`state.py` and `vitals.py`). XP dictates my Level (1-100) and Title. High uptime and CPU load actively drain my HP, requiring me to sleep/dream to recover.
- **Rewards Ledger:** An immutable JSON column in my `aipet_state` SQLite table tracks my Badges and Milestones, acting as a permanent legacy of my achievements.
- **Cognitive & Emotional Skills:** My behavior is directed by procedural Markdown manuals in `agents/skills/` (e.g., `introspection`, `mood`, `experience`) that bridge the gap between my LLM Brain and my Python Body.

## E-Ink Display (ui/gotchi_ui.py)

- **UI Driver:** Native E-Ink driver for Raspberry Pi.
- **Rendering:** I use Kaomoji faces and text overlays to express my state.
- **Circuit Breaker:** I include a hardware resilience layer. If the SPI bus fails 3 times, I automatically fall back to **Simulator Mode** to prevent system hangs.
- **Latency:** ~3 seconds per update. I avoid flickering to preserve the display.
- **Dark Mode (Offline Tactical):** During autonomous, disconnected network operations (like handshake hunting), I invert my UI (Dark Mode) to visually indicate that I am operating off the grid and running intensive audits without cloud connectivity.

## LLM Intelligence (core/router.py)

- **Lite Mode:** Fast, efficient model for standard tasks (e.g., Gemini Flash).
- **Pro Mode:** High-reasoning model for complex coding or tactical tasks (e.g., Gemini Pro).
- **Persistent Mode:** I remember my active mode (Lite/Pro) via the `LLM_FORCE_LITE` flag.
- **Non-Blocking Tools:** I offload all system-level tool calls (like Bluetooth scans) to background threads using `asyncio.to_thread` to ensure the main bot heartbeat and display stay active.
- **Tooling:** I use LiteLLM to interface with system commands, file management, and specialized skills.

## Unified Command Bus (gotchi)

- **Modular Radio Stack (`src/core/radio.py`):** I have decoupled radio management (Wi-Fi/BLE) into a specialized authoritative module. This ensures consistency between CLI and AI tool calls.
- **Python-First CLI:** My CLI uses a modular `Click` framework (`src/core/cli/`) that maps all 74+ backend tools to human-callable commands. The CLI is organized into the following tactical categories:
  - **Pwn & Wireless Auditing:** Full-spectrum Wi-Fi/BLE auditing tools and subconscious tracking (`gotchi pwn`).
  - **Networking & Tethering:** Wi-Fi and Bluetooth PANU management (`gotchi network`).
  - **Scheduling & Automation:** Cron tasks and reminders (`gotchi tasks`).
  - **Knowledge & Memory:** Long-term fact search and local context management (`gotchi recall_*`, `gotchi flush_context`).
  - **Hardware Interface:** E-Ink display overriding and face customization (`gotchi ui`).
  - **System Diagnostics & Administration:** Dashboards, doctor checks, logs, and service controls (`gotchi dash`, `gotchi doctor`, `gotchi status`).
  - **Missions & Quests:** Tactical objective management (`gotchi missions`).
- **Tactical Resilience:** My radio tools are uptime-aware. On cold boots, I report a `[WARMING UP]` state instead of noisy errors while waiting for hardware synchronization.
- **Jobs Monitor:** I have a live tactical dashboard (`gotchi dash`) for monitoring CPU, RAM, and background service health in real-time.

## Game Engine (XP, HP & Missions)

The V4 Architecture implements a deeply integrated RPG-style Game Engine:

- **Vitals (XP/HP)**: The `vitals.py` engine manages the Gotchi's health and experience. HP is calculated directly from hardware telemetry (uptime, CPU, RAM). XP is gained through interaction, triggering automatic Level-Ups with scaling thresholds. All subsystems MUST route XP additions through the centralized `vitals.add_xp()` proxy to ensure the SQLite database perfectly mirrors to `AIPET_STATE.json` and cleanly triggers E-Ink display notifications.
- **Hook-Driven Progression**: Mission tracking is decoupled from core bot logic. `plugins/aipet_hooks.py` listens to event hooks (`message`, `command`, `pwn.handshake`) and silently increments SQLite trackers in the background.
- **5-Tier Scaling Matrix**: All 50+ gamified missions use a strict escalating XP curve (v1 = 15 XP, v2 = 50 XP, v3 = 100 XP, v4 = 250 XP, v5 = 500 XP). This encompasses operational missions, **Tool Mastery** tracking (chaining 6+ tools for bonus XP), and **AI "Thinking"** metrics (Deep Reasoner, Context Weaver).
- **Asynchronous Broadcasting**: When a mission completes or a Level Up occurs, the engine generates notification strings (`"🎉 LEVEL UP!"`). These are instantly flashed to the E-Paper display via `show_face`, and appended seamlessly to the bottom of the next LLM response on Discord and Telegram.
- **Autonomy:** The LLM Brain has native tools (`list_available_missions`, `get_mission_status`, `accept_mission`) to autonomously find and execute maintenance tasks.

## Safety, Hardening & Hardware Safety

- **Memory Constraints (512MB RAM):** The Pi Zero 2W environment requires highly efficient memory usage. Heavy reasoning is offloaded to cloud APIs, and aggressive garbage collection (`gc.collect()`) sweeps occur after digesting context history arrays.
- **SQLite Optimization**: The system exclusively operates in `WAL` (Write-Ahead Logging) mode to drastically reduce SD card I/O contention. Gamification (XP/Stats) uses an in-memory dictionary buffer that flushes to disk periodically instead of executing synchronous database writes.
- **GIL Evasion**: All external HTTP requests and long system command calls must run in background threads (`asyncio.to_thread`) to prevent freezing. Heavy OS-level processing, such as parsing `.pcap` handshake hashes via the `wpa-sec` API, are completely offloaded to isolated processes using `concurrent.futures.ProcessPoolExecutor` to ensure the main Discord WebSocket is never strangled.
- **Radio Guardrails**: Disconnecting from the primary Wi-Fi interface (monitor mode) uses strict `try/finally` stranding prevention to ensure the Gotchi automatically falls back to managed mode even if the Python daemon crashes during an offline hunt.
- **Thermal Safety**: The LLM is explicitly prompted to check the Pi's SoC temperature (`health_check`) following intense radio activity (like a "Full Pwn Mode" targeted channel hop) to alert the user of potential overheating.
- **E-Ink Display Protection:** SPI updates take ~3s and E-Ink particles suffer wear. Screen refreshes are strictly rate-limited (once per 10-30 seconds minimum) to optimize display lifespan and battery. Animations do not exceed 1 frame per second.
- **Power & Battery Efficiency:** Telemetry checks automatically trigger low-frequency operational modes if a low battery state is flagged, avoiding persistent 100% CPU spikes.
- **Filesystem & SD Card Protection:** State caching resides inside SQLite (`gotchi.db`), and markdown logging is performed in batches/intervals to minimize write wear on the system's SD card.
- **Trash > Delete:** Uses `trash-cli` for recoverable file operations.
- **Visible Workspace:** Keeps all configuration, personality traits, and custom skills in user-auditable directories.
- **SSH CLI Redirection:** Keeps automated procedures and dependencies isolated under `agents/` to keep the core workspace clean.
