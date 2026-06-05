# OpenClawGotchi V4 — Game Engine Architecture Audit

**Target:** `src/game_engine/` and interconnected modules (`db/stats.py`).
**Focus:** RPG Pet/Companion systems, leveling, missions, vitals, hardware constraints.

---

## 1. Core Architecture

The Game Engine operates as a lightweight, non-blocking RPG layer on top of the core agent. It bridges the gap between hardware telemetry, conversational interactions, and gamification without dragging down the Pi Zero's main event loop.

- **Dual-Storage Model:** 
  - **Authoritative Source:** SQLite `gotchi_stats` table in `db/stats.py`.
  - **Fast-Read Mirror:** `workspace/AIPET_STATE.json` managed via `state.py` and defined by Pydantic `models.py`. 
- **Data Flow:** All game actions (e.g., `add_xp`) are routed through `vitals.py`, which delegates the write to the database buffer, mirrors the new state to the JSON file, appends an audit row to `aipet_vitals_log`, and triggers UI hooks (E-ink flash, Discord webhooks).
- **Decoupling:** The engine is strictly synchronous but heavily buffered, meaning it never blocks the `asyncio` loop of the Discord/Telegram heartbeats.

## 2. Levelling & XP System

The progression system is highly reminiscent of Battlefield/Call of Duty combined with Tamagotchi elements.

- **XP Mechanics:** Located in `db/stats.py`.
  - **Sources:** Answering messages (+10), using tools (+5/each), completing tasks (+25), interacting with sibling bots (+50), daily survival (+100), and heartbeats (+5).
  - **In-Memory Buffering:** `_stat_buffer` caches XP and stat increments in memory and flushes them to SQLite every 5 minutes (or forcibly during a 4-hour heartbeat). This drastically reduces SD Card write wear.
- **Progression Scaling:** A hardcoded array of 20 `LEVEL_THRESHOLDS` (0 to 120,000 XP) and `LEVEL_TITLES`. The curve is exponential.
- **Titles/Flavor:** Ranks follow a hacker/hardware theme (e.g., *Newborn*, *Cron Job Enjoyer*, *Sudo Make Sandwich*, *Kernel Panic*, *Gotchi Prime*, *BF6 Reject*).

## 3. HP & Vitals System

Unlike traditional RPGs where HP is depleted by enemy attacks, the Gotchi's HP is a **derived hardware metric**.

- **Mechanics (`vitals.calculate_hp`):** 
  - HP is mathematically derived from system load: `(uptime_hours * 1.5) + ((100 - cpu) * 0.4) + ((100 - mem) * 0.3) + (battery * 0.2)`
  - **Critique:** The formula treats high `uptime_hours` as a net positive. In reality, extremely long uptimes on a Pi Zero often result in memory fragmentation. 
- **Other Vitals:** `RP` (Reputation) and `current_mood` are tracked in the state schema but seem to be loosely integrated (mostly altered manually via `trigger_dream()`). 
- **Impact:** Currently, HP acts purely as narrative flavor and a read-only metric on the dashboard. There are no systemic failure states (e.g., the Gotchi doesn't refuse to run tasks if HP hits 0).

## 4. Missions & Progression

The `missions.py` module introduces a surprisingly deep "Bounty" system.

- **Design:** Stored in `aipet_missions` SQLite table. Missions are seeded from a `progressive.json` file.
- **Progressive Tiers:** The system supports multi-tier missions using a `base_name` column. When a "v1" mission hits its target, `complete_mission()` automatically unlocks the "v2" pending tier.
- **Rewards & Hooks:** Completing a mission awards XP, writes to the daily memory log, triggers an E-Ink flash (`show_face("excited")`), and spins up a background thread to fire a Discord webhook announcement.

## 5. Technical Quality

- **Performance on Pi Zero:** **Excellent**. Enabling `PRAGMA journal_mode=WAL` and using the in-memory `_stat_buffer` dictionary for the gamification tracker is a textbook best practice for heavily constrained SD card environments.
- **Thread Safety:** The stat buffer's `flush_stats()` isn't explicitly protected by a lock. While Python's GIL makes dictionary operations pseudo-thread-safe, concurrent heavy writes from different `ProcessPoolExecutor` workers might lead to race conditions when clearing `_stat_buffer.clear()`.
- **Modularity:** High. `vitals.py` successfully hides the implementation details of `db/stats.py` from the rest of the application.
- **Edge Cases:** The auto-migration code in `__init__.py` ensures older versions of the SQLite database gracefully adopt the new progressive mission columns (`target`, `progress`, `base_name`).

## 6. Integrations & UX

- **TUI & CLI:** `cli.py` uses `rich` to render an incredibly polished terminal UI, complete with progress bars, color-coded mission tables, and detailed stat breakdowns (`gotchi aipet status`).
- **E-Ink Display:** Tightly integrated. Every level-up and mission completion immediately proxies to `hardware.display.show_face` to give physical feedback to the user.
- **Discord:** Slash commands (`/status`, `/xp`, `/jobs`) directly hook into the game engine. Status commands format the LLM prompt to include the Gotchi's current "mood" and "level", deeply coupling the RPG mechanics to the AI's "Subconscious" persona generation.

---

## 7. Strengths

1. **Immersive Persona Integration:** By feeding the "Level", "XP", and "Title" directly into the LLM context prompt, the agent's tone naturally evolves from a "Newborn" to a "Gotchi Prime" without requiring complex prompt engineering.
2. **Zero-Overhead Gamification:** The use of in-memory buffering for rapid XP events (like token usage or task completions) ensures the "game" never throttles the primary radio/AI duties.
3. **Hardware Tying:** Making HP a reflection of RAM/CPU/Thermal load gives the user a gamified way to monitor their Pi Zero's health.

## 8. Weaknesses & Technical Risks

1. **State Synchronization Drift:** Maintaining both an `AIPET_STATE.json` and the SQLite `gotchi_stats` table is risky. If the daemon crashes before the JSON buffer writes, the display engine (which reads the JSON) might show stale data until the next DB flush overwrites it.
2. **Uptime HP Logic Flaw:** `(uptime_hours * 1.5)` constantly increases HP over time. A Pi running for 60 hours will max out its HP regardless of severe CPU/Memory throttling.
3. **Lack of Consequences:** Low HP or bad moods have no tangible effect on the Gotchi's capability (e.g., it won't refuse to run `pwn_crack` if it is exhausted).

## 9. Recommendations & Action Items

### High Priority
- **Fix the HP Formula:** Invert the uptime modifier. Uptime should *decay* HP slightly (simulating exhaustion/memory fragmentation), which regenerates when the Gotchi "sleeps" (reboots or triggers `dream()` mode).
- **Thread Safety in Stat Buffering:** Add a `threading.Lock()` inside `db/stats.py` to wrap the `flush_stats()` and `increment_stat()` operations, preventing potential race conditions during heavy async webhook traffic.

### Medium Priority
- **Consolidate State Management:** Deprecate `AIPET_STATE.json` entirely. With WAL mode enabled, SQLite reads are fast enough that the E-Ink display loop can fetch the canonical state directly without needing the JSON mirror.
- **Implement Mechanical Consequences:** If `HP < 20.0`, the system should automatically block heavy operations like `ProcessPoolExecutor` pcap cracking and force the LLM into "Lite Mode" to shed thermal load.

### Low Priority / Future Features
- **Skill Tree Implementation:** Use the Level threshold to gate capabilities. For example, the `Full Pwn Mode` command should return "Level 10 (0xDEADBEEF) Required" if requested by a lower-level Gotchi.
- **Mood Decay:** Add a cron-triggered function that slowly shifts `current_mood` back to `neutral` if no positive interactions (brother chats, user messages) occur for X hours.
