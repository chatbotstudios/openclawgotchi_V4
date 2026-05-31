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

**Plugin System (`plugins/`):**
- `plugins/` — The main directory for event-driven automation.
- Hooks: I use a centralized `HookSystem` to trigger Python plugins on events like `pwn.handshake`, `startup`, and `message`.
- Extensibility: Pwnagotchi-style plugins can be ported by mapping their events to our hooks.

## The Heartbeat (bot/heartbeat.py)

- **Interval:** Every 4-6 hours.
- **Reflection:** I review recent logs and update my state in `HEARTBEAT.md`.
- **Award:** I earn XP for being active and helpful.
- **Telemetry:** I monitor CPU load, RAM usage, and temperature to ensure health.

## E-Ink Display (ui/gotchi_ui.py)

- **UI Driver:** Native E-Ink driver for Raspberry Pi.
- **Dynamic Gamified HUD:** The display leverages a 3-anchor Footer System to show Level, a 10-block XP progress bar, and Uptime. A floating EXTRAS row displays Health Points (HP) and Reputation Points (RP).
- **Rendering:** I use Kaomoji faces whose expressions are mathematically tied to the Game Engine's `HP` vitals.
- **Circuit Breaker:** I include a hardware resilience layer. If the SPI bus fails 3 times, I automatically fall back to **Simulator Mode** to prevent system hangs.
- **Latency:** ~3 seconds per update. I avoid flickering to preserve the display.

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
  - **Networking & Tethering:** Wi-Fi and Bluetooth PANU management (`gotchi network`). We also explicitly preserve `ModemManager` (Cellular) and `avahi-daemon` (mDNS) for auto-discovery and expanded connectivity.
  - **Scheduling & Automation:** Cron tasks and reminders (`gotchi tasks`).
  - **Knowledge & Memory:** Long-term fact search and local context management (`gotchi recall_*`, `gotchi flush_context`).
  - **Hardware Interface:** E-Ink display overriding and face customization (`gotchi ui`).
  - **System Diagnostics & Administration:** Dashboards, doctor checks, logs, and service controls (`gotchi dash`, `gotchi doctor`, `gotchi status`).
  - **Missions & Quests:** Tactical objective management (`gotchi missions`).
- **Tactical Resilience:** My radio tools are uptime-aware. On cold boots, I report a `[WARMING UP]` state instead of noisy errors while waiting for hardware synchronization.
- **Jobs Monitor:** I have a live tactical dashboard (`gotchi dash`) for monitoring CPU, RAM, and background service health in real-time.

## Missions & Quests (Hybrid Autonomy)

- **Storage & State:** SQLite `missions` table and `workspace/AIPET_STATE.json` track progressive mission progress, Level, HP, XP, and Rank.
- **Progressive Tiers:** The `missions.py` engine dynamically loads JSON files to auto-promote active missions through progressive tiers (e.g. from v1 to v2) via the `increment_mission_progress` hook.
- **Actor Model:** Missions specify who can execute them (`human`, `gotchi`, `any`).
- **Autonomy:** The LLM Brain has native tools (`list_available_missions`, `get_mission_status`, `accept_mission`) to autonomously find and execute maintenance/stealth tasks during heartbeats.
- **Rewards:** Completed missions trigger Discord webhooks, E-Ink Mood boosts, and XP awards.

## Safety, Hardening & Hardware Safety

- **Memory Constraints (512MB RAM):** The Pi Zero 2W environment requires highly efficient memory usage. Heavy reasoning is offloaded to cloud APIs, and garbage collection is favored over keeping large objects/buffers in memory.
- **Non-Blocking Operation:** The heartbeats and E-Ink display loop rely on a responsive environment. All external HTTP requests and long system command calls must run in background threads (`asyncio.to_thread`) to prevent freezing.
- **E-Ink Display Protection:** SPI updates take ~3s and E-Ink particles suffer wear. Screen refreshes are strictly rate-limited (once per 10-30 seconds minimum) to optimize display lifespan and battery. Animations do not exceed 1 frame per second.
- **Power & Battery Efficiency:** Telemetry checks automatically trigger low-frequency operational modes if a low battery state is flagged, avoiding persistent 100% CPU spikes.
- **Filesystem & SD Card Protection:** State caching resides inside SQLite (`gotchi.db`), and markdown logging is performed in batches/intervals to minimize write wear on the system's SD card.
- **Trash > Delete:** Uses `trash-cli` for recoverable file operations.
- **Visible Workspace:** Keeps all configuration, personality traits, and custom skills in user-auditable directories.
- **SSH CLI Redirection:** Keeps automated procedures and dependencies isolated under `agents/` to keep the core workspace clean.
