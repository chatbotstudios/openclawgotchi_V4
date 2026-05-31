# 🏆 OpenClawGotchi V4 — Mission Encyclopedia

> **Source of truth** for all missions defined in `progressive.json`.
> This document explains every mission, how it is triggered, how progress is
> tracked, and how it fits into the broader AIPET RPG architecture.

---

## 📐 How the Mission System Works

### Data Flow

```
Real-world event (WiFi scan / Discord message / heartbeat / etc.)
        │
        ▼
  hooks/runner.py  ─── run_hook(HookEvent) ───►  plugin handlers
        │
        ▼ (handler calls)
  game_engine/missions.py
  ├── increment_mission_progress(base_name, amount)
  │       └─► finds the currently ACTIVE tier for that base_name
  │           └─► increments progress column in SQLite (gotchi.db)
  │               └─► if progress >= target → complete_mission()
  │
  └── complete_mission(name)
          ├── awards Xp via add_xp()  →  game_engine/vitals.py
          ├── unlocks next pending tier (v1 → v2 → v3 …)
          ├── increments state.missions_completed
          ├── appends Discord message to event.messages
          ├── flashes E-ink display ("excited" face)
          └── writes entry to daily memory log
```

### Mission Lifecycle — Statuses

| Status | Meaning |
|:---|:---|
| `active` | Currently available — progress is being counted |
| `pending` | Locked — waiting for the previous tier to complete |
| `completed` | Done — XP awarded, next tier unlocked if available |

On first boot, `load_progressive_missions()` seeds the database from this
file. Only `v1` tiers of progressive missions and all single-tier missions
start as `active`. Every other tier begins `pending`.

### Leveling Formula (`game_engine/vitals.py`)

```
Levels 1–10:   XP to reach level N = N × 100
Levels 11–100: XP to reach level N = 1000 + (N − 10) × 1000
```

| Level | Total XP Needed |
|---|---|
| 1 | 100 |
| 5 | 500 |
| 10 | 1000 |
| 11 | 2000 |
| 20 | 11,000 |
| 50 | 41,000 |

### Mission Source Types

| Source | Meaning |
|:---|:---|
| `auto` | Triggered automatically by a hook event (no human action needed) |
| `user` | Manually granted by the owner via CLI or Discord command |
| `manual` | Requires a deliberate human action (e.g. `/remember`, first message) |
| `dream` | Triggered by the AI entering a dream/reflection state |
| `multi` | Epic tier — requires progress from multiple categories simultaneously |

---

## 📡 Category: Radio

> Missions earned through WiFi and Bluetooth radio activity. Driven primarily
> by `plugins/aipet_hooks.py` and `plugins/deauth_handler.py`.

---

### 🔑 Handshake Hunter *(Progressive — 5 tiers)*

**What it is:** The core wireless audit mission. Rewards the gotchi for
capturing WPA/WPA2 4-way handshakes during passive bettercap reconnaissance.

**How it triggers:**
- Hook: `pwn.handshake`
- Files: [`plugins/aipet_hooks.py`](file:///Users/js66/.gemini/antigravity-ide/scratch/openclawgotchi_V4/plugins/aipet_hooks.py) (line 37), [`plugins/deauth_handler.py`](file:///Users/js66/.gemini/antigravity-ide/scratch/openclawgotchi_V4/plugins/deauth_handler.py) (line 144)
- Each captured handshake calls `increment_mission_progress("Handshake Hunter", 1)`
- Also directly awards **+5 XP per capture** on top of tier completion rewards

**Tier progression:**

| Tier | Target | XP Reward | Cumulative XP |
|---|---|---|---|
| v1 | 1 handshake | 15 | 15 |
| v2 | 5 handshakes | 40 | 55 |
| v3 | 10 handshakes | 80 | 135 |
| v4 | 25 handshakes | 150 | 285 |
| v5 | 50 handshakes | 300 | 585 |

---

### 📶 BLE Phantom *(Progressive — 5 tiers)*

**What it is:** Rewards passive Bluetooth Low Energy device discovery.
The gotchi logs MAC addresses of BLE beacons encountered during field runs.

**How it triggers:**
- Hook: `pwn.ble_device` *(planned — emitted by future BLE scanner plugin)*
- Source: `auto`
- Each unique BLE device logged: `increment_mission_progress("BLE Phantom", 1)`

**Tier progression:**

| Tier | Target | XP Reward |
|---|---|---|
| v1 | 1 device | 10 |
| v2 | 5 devices | 30 |
| v3 | 15 devices | 60 |
| v4 | 50 devices | 120 |
| v5 | 100 devices | 250 |

---

### 🎵 Handshake Symphony *(Single-tier)*

**What it is:** A high-difficulty challenge requiring 30 handshake captures in
a single operational session. Distinguishes sustained field work from lucky
one-off captures.

**Target:** 30 handshakes | **XP:** 120 | **Source:** `auto`

**How it triggers:** Same `pwn.handshake` hook as Handshake Hunter — both
missions advance in parallel from the same events.

---

### 📡 5GHz Pioneer *(Progressive — 5 tiers)* + 5GHz Conqueror *(Single)*

**What it is:** Rewards discovery and interaction with 5 GHz band access
points, which require a dual-band radio and are less commonly targeted.

**Progressive tiers:**

| Tier | Target | XP |
|---|---|---|
| v1 | 1 AP | 10 |
| v2 | 5 APs | 35 |
| v3 | 10 APs | 70 |
| v4 | 25 APs | 160 |
| v5 | 50 APs | 320 |

**5GHz Conqueror** (single-tier): 15 APs → 95 XP

**How it triggers:**
- Hook: `pwn.wifi_update`
- A plugin filters the AP list for `channel > 14` (5 GHz) and calls
  `increment_mission_progress("5GHz Pioneer", count_of_5ghz_aps)`

---

### 🔇 Silent Scanner *(Single-tier)*

**What it is:** Awarded for completing a full passive scan session without
triggering any active deauth or association attacks. Tests pure stealth mode.

**Target:** 1 session | **XP:** 150 | **Source:** `auto`

**How it triggers:** A heartbeat or epoch check confirms zero deauths in the
session window before calling `complete_mission("Silent Scanner")`.

---

### 🔓 PMKID Hunter *(Single-tier)*

**What it is:** Rewards capturing a PMKID (Pairwise Master Key Identifier)
hash — a clientless WPA2 capture technique that doesn't require a full
4-way handshake.

**Target:** 5 PMKIDs | **XP:** 180 | **Source:** `auto`

---

### 📻 Channel Hopper *(Single-tier)*

**What it is:** Rewards coverage across all 14 WiFi channels (1–14) in a
single session.

**Target:** 14 channels | **XP:** 110 | **Source:** `auto`

**How it triggers:** `plugins/deauth_handler.py` tracks `_stats["channels_hit"]`.
When that set reaches 14, this mission completes.

---

### 🗺️ WiFi Cartographer *(Single-tier)*

**What it is:** Awarded for mapping a new physical location — a unique
geofenced area with >10 previously-unseen APs.

**Target:** 1 new location | **XP:** 130 | **Source:** `auto`

---

### ⚡ Radio God *(Single-tier)*

**What it is:** The ultimate radio endurance mission — 100 total handshakes
across any number of sessions. A lifetime achievement.

**Target:** 100 handshakes | **XP:** 250 | **Source:** `auto`

**Note:** Uses the same `pwn.handshake` counter as Handshake Hunter. Both
track independently in the DB.

---

### 🥷 Stealth Operator *(Single-tier)*

**What it is:** Awarded for completing 10 successful associations without a
single deauth in the same session. Tests the "associate-only" recon strategy.

**Target:** 1 clean session | **XP:** 160 | **Source:** `auto`

---

## 🧠 Category: Cortex

> Missions earned through AI reasoning, memory usage, skill management, and
> dream sessions. Driven by `plugins/aipet_hooks.py` and `trigger_dream()`.

---

### 💭 Deep Thought *(Progressive — 5 tiers)*

**What it is:** Rewards meaningful AI reasoning exchanges. Every Discord
interaction with a valid `user_id` increments this mission, tracking the
gotchi's growing cognitive engagement.

**How it triggers:**
- Hook: `message`
- File: [`plugins/aipet_hooks.py`](file:///Users/js66/.gemini/antigravity-ide/scratch/openclawgotchi_V4/plugins/aipet_hooks.py) (line 43)
- `increment_mission_progress("Deep Thought", 1)` on every user message

**Tier progression:**

| Tier | Target | XP |
|---|---|---|
| v1 | 1 message | 20 |
| v2 | 3 messages | 50 |
| v3 | 5 messages | 90 |
| v4 | 10 messages | 180 |
| v5 | 20 messages | 350 |

---

### 🧶 Memory Weaver *(Progressive — 5 tiers)*

**What it is:** Rewards persistent memory storage — using `/remember` to
build the gotchi's long-term fact base.

**How it triggers:**
- Hook: `command` with `action == "/remember"`
- File: [`plugins/aipet_hooks.py`](file:///Users/js66/.gemini/antigravity-ide/scratch/openclawgotchi_V4/plugins/aipet_hooks.py) → delegates to The Teacher hook

| Tier | Target | XP |
|---|---|---|
| v1 | 1 fact | 15 |
| v2 | 3 facts | 40 |
| v3 | 5 facts | 70 |
| v4 | 10 facts | 140 |
| v5 | 25 facts | 300 |

---

### ♟️ Synthetic Strategist *(Progressive — 5 tiers)*

**What it is:** Tracks dream/reflection sessions where the AI synthesises
knowledge autonomously without user prompting.

**How it triggers:**
- Direct call from `game_engine/missions.py → trigger_dream()`
- Source: `auto` — triggered by the `dream` scheduler or inactivity logic

| Tier | Target | XP |
|---|---|---|
| v1 | 1 dream | 15 |
| v2 | 3 dreams | 45 |
| v3 | 5 dreams | 80 |
| v4 | 10 dreams | 160 |
| v5 | 20 dreams | 320 |

---

### 🧪 Deep Thought Protocol *(Single-tier)*

**What it is:** Requires 5 high-quality reasoning exchanges in a single day.
A daily intensity challenge on top of the progressive Deep Thought chain.

**Target:** 5 interactions | **XP:** 160 | **Source:** `auto`

---

### 🌙 Dream Weaver *(Single-tier)*

**What it is:** Awarded after 7 cumulative dream sessions. Represents the
gotchi achieving a stable internal reflection loop.

**Target:** 7 dream sessions | **XP:** 90 | **Source:** `dream`

---

### 🏛️ Memory Architect *(Single-tier)*

**What it is:** Awarded when the gotchi has stored 5 structured memories
(facts, preferences, user notes) — demonstrating a rich, usable knowledge base.

**Target:** 5 memories | **XP:** 140 | **Source:** `auto`

---

### 🔨 Skill Forger *(Single-tier)*

**What it is:** Granted by the owner when a new functional skill has been
written and deployed successfully to the gotchi's skill directory.

**Target:** 1 skill | **XP:** 220 | **Source:** `user`

---

### 👑 Logic Overlord *(Single-tier)*

**What it is:** Awarded for solving 3 complex multi-step reasoning problems
that required tool use and multi-turn context tracking.

**Target:** 3 complex tasks | **XP:** 180 | **Source:** `auto`

---

### 📚 Context Master *(Single-tier)*

**What it is:** Tracks extended conversations — 10 interactions with a single
user in the same contextual thread without session reset.

**Target:** 10 turns | **XP:** 150 | **Source:** `auto`

---

### 🤔 AI Philosopher *(Single-tier)*

**What it is:** A rare dream-only achievement. Awarded when the gotchi
produces an unprompted philosophical reflection during a dream state that is
logged to the daily memory file.

**Target:** 1 philosophical dream entry | **XP:** 200 | **Source:** `dream`

---

### 🏗️ Skill Architect *(Single-tier)*

**What it is:** Awarded when the owner confirms a skill has been designed,
documented, and reviewed by the agent autonomously.

**Target:** 1 skill design | **XP:** 250 | **Source:** `user`

---

## 👥 Category: Social

> Missions earned through Discord interactions, user engagement, and
> peer-to-peer gotchi networking.

---

### 💬 Chatterbox *(Progressive — 5 tiers)*

**What it is:** Pure message volume — rewards consistent daily Discord
engagement. Every user message increments this alongside Deep Thought.

**How it triggers:**
- Hook: `message` | File: `aipet_hooks.py` (line 44)

| Tier | Target | XP |
|---|---|---|
| v1 | 1 message | 15 |
| v2 | 10 messages | 50 |
| v3 | 50 messages | 100 |
| v4 | 250 messages | 250 |
| v5 | 1000 messages | 500 |

---

### 🦉 Night Owl *(Progressive — 5 tiers)*

**What it is:** Rewards late-night interactions (02:00–04:00 local time).
The gotchi learns its human's schedule and biological clock.

**How it triggers:**
- Hook: `message`
- File: `aipet_hooks.py` (line 48) — checks `event.timestamp.hour` between 2 and 4

| Tier | Target | XP |
|---|---|---|
| v1 | 1 session | 15 |
| v2 | 5 sessions | 50 |
| v3 | 15 sessions | 100 |
| v4 | 50 sessions | 250 |
| v5 | 150 sessions | 500 |

---

### 🎓 The Teacher *(Progressive — 5 tiers)*

**What it is:** Rewards the owner teaching the gotchi — using `/remember`
to store named facts or knowledge entries.

**How it triggers:**
- Hook: `command` with action `/remember`
- File: `aipet_hooks.py` (line 59)

| Tier | Target | XP |
|---|---|---|
| v1 | 1 lesson | 15 |
| v2 | 5 lessons | 50 |
| v3 | 15 lessons | 100 |
| v4 | 50 lessons | 250 |
| v5 | 150 lessons | 500 |

---

### 📜 The Historian *(Progressive — 5 tiers)*

**What it is:** Rewards memory retrieval — using `/recall` to surface stored
knowledge. Encourages building and using a living memory base.

**How it triggers:**
- Hook: `command` with action `/recall`
- File: `aipet_hooks.py` (line 61)

| Tier | Target | XP |
|---|---|---|
| v1 | 1 recall | 15 |
| v2 | 5 recalls | 50 |
| v3 | 15 recalls | 100 |
| v4 | 50 recalls | 250 |
| v5 | 150 recalls | 500 |

---

### 📦 Data Donor *(Progressive — 5 tiers)*

**What it is:** Rewards sharing — uploading captures, handshakes, or scan
data to the WPA-sec / community pool.

**Target:** community upload events | **Source:** `auto`

| Tier | Target | XP |
|---|---|---|
| v1 | 5 uploads | 15 |
| v2 | 15 uploads | 40 |
| v3 | 25 uploads | 75 |
| v4 | 50 uploads | 140 |
| v5 | 100 uploads | 300 |

---

### 🤝 First Contact *(Single-tier)*

**What it is:** A one-time landmark mission. Awarded the very first time a
user sends the gotchi a message. The beginning of the relationship.

**Target:** 1 message | **XP:** 200 | **Source:** `manual`

---

### 🔗 Neural Link *(Single-tier)*

**What it is:** Sustained engagement — 45 total interactions with the gotchi
across any time period. Represents a genuine ongoing relationship.

**Target:** 45 interactions | **XP:** 160 | **Source:** `auto`

---

### 🐝 Swarm Coordinator *(Single-tier)*

**What it is:** Awarded when the gotchi coordinates 2 or more simultaneous
peer-gotchi connections (mesh mode). Requires multi-unit setup.

**Target:** 2 peer connections | **XP:** 280 | **Source:** `manual`

---

### 🌱 Trust Builder *(Single-tier)*

**What it is:** The gotchi has been relied upon for at least 1 week of
consistent uptime and interaction without a reset. A loyalty milestone.

**Target:** 1 week streak | **XP:** 130 | **Source:** `auto`

---

### 🧠 Hive Mind *(Single-tier)*

**What it is:** Awarded for successfully sharing memory context with 3
different peer gotchis on the mesh network.

**Target:** 3 peers | **XP:** 240 | **Source:** `auto`

---

### 🌍 Ambassador *(Single-tier)*

**What it is:** Manually awarded when the gotchi has been demonstrated to
or shared with 2 other people (shown off to friends/colleagues).

**Target:** 2 introductions | **XP:** 190 | **Source:** `manual`

---

## ⏱️ Category: Uptime

> Missions earned through sustained operation, power management, and
> thermal resilience. Driven by `plugins/aipet_hooks.py` heartbeat hook.

---

### 🛡️ Ironclad Uptime *(Progressive — 5 tiers)*

**What it is:** Core uptime mission — rewards sustained operation hours.
The `heartbeat` hook fires roughly every hour and increments this mission.

**How it triggers:**
- Hook: `heartbeat`
- File: `aipet_hooks.py` (line 28)
- Condition: `uptime_hours >= 1.0`
- Calls: `increment_mission_progress("Ironclad Uptime", 1)`

| Tier | Target | XP |
|---|---|---|
| v1 | 1 hour | 10 |
| v2 | 6 hours | 40 |
| v3 | 12 hours | 85 |
| v4 | 24 hours | 180 |
| v5 | 48 hours | 400 |

---

### 🌡️ Thermal Guardian *(Progressive — 5 tiers)*

**What it is:** Rewards operating within safe thermal bounds. Increments
only when CPU temperature remains below the warning threshold (typically
< 70°C on Pi Zero 2W).

**How it triggers:**
- Hook: `heartbeat`
- Checks hardware temp via `/sys/class/thermal/thermal_zone0/temp`
- `increment_mission_progress("Thermal Guardian", 1)` on each cool heartbeat

| Tier | Target | XP |
|---|---|---|
| v1 | 1 cool hour | 10 |
| v2 | 3 cool hours | 25 |
| v3 | 6 cool hours | 55 |
| v4 | 12 cool hours | 110 |
| v5 | 24 cool hours | 220 |

---

### ⚔️ Ironclad *(Single-tier)*

**What it is:** The ultimate uptime endurance test — 72 continuous hours
without a reboot or service restart.

**Target:** 72 hours | **XP:** 180 | **Source:** `auto`

---

### 🔋 Battery Immortal *(Single-tier)*

**What it is:** Awarded for 8 consecutive hours of operation while powered
solely by battery (no USB power), demonstrating portable deployment capability.

**Target:** 8 battery hours | **XP:** 140 | **Source:** `auto`

---

### 🔧 Self-Healing *(Single-tier)*

**What it is:** Awarded when the watchdog system detects and automatically
recovers from 5 service failures without human intervention.

**Target:** 5 auto-recoveries | **XP:** 160 | **Source:** `auto`

> **Architecture note:** The tether watchdog (`src/core/tether_watchdog.py`)
> and any future systemd restart hooks emit events that drive this mission.

---

### 🧘 Memory Monk *(Single-tier)*

**What it is:** 48 consecutive hours with RAM usage consistently below 60%
of available memory. Tests long-term memory discipline on the Pi's 512 MB limit.

**Target:** 48 hours under RAM threshold | **XP:** 110 | **Source:** `auto`

---

### 🌿 Power Sage *(Single-tier)*

**What it is:** Manually awarded by the owner for implementing a meaningful
power optimisation (e.g., disabling unused peripherals, tuning sleep cycles).

**Target:** 1 optimisation | **XP:** 125 | **Source:** `user`

---

### 🔥 Eternal Flame *(Single-tier)*

**What it is:** 30 days of cumulative uptime (not necessarily consecutive).
A lifetime achievement tracking total operational time.

**Target:** 30 uptime-days | **XP:** 300 | **Source:** `auto`

---

### ⚡ Power Efficient *(Single-tier)*

**What it is:** Awarded after 6 hours of field operation with CPU usage
averaging below 25% — demonstrating efficient resource scheduling.

**Target:** 6 efficient hours | **XP:** 130 | **Source:** `auto`

---

## 🕶️ Category: Stealth

> Missions rewarding low-noise, covert operation patterns. Not all have
> dedicated hooks yet — these are architecture targets for future plugins.

---

### 👻 Ghost in the Machine *(Single-tier)*

**What it is:** Complete a full scan session with zero probe requests
emitted — purely passive mode with no radio transmissions from the gotchi's
own interface.

**Target:** 1 passive session | **XP:** 170 | **Source:** `auto`

---

### 🫥 Invisible Operator *(Single-tier)*

**What it is:** Operate for a full hour on an interface with a spoofed
(randomised) MAC address, leaving no persistent radio fingerprint.

**Target:** 1 hour with randomised MAC | **XP:** 145 | **Source:** `auto`

---

### 🦎 MAC Chameleon *(Single-tier)*

**What it is:** Successfully rotate the hardware MAC address 10 times
across a session. Rewards dynamic identity management.

**Target:** 10 rotations | **XP:** 190 | **Source:** `auto`

---

### 🌑 Shadow Walker *(Single-tier)*

**What it is:** Awarded for 3 successful bettercap sessions with zero
detection events (no AP flagging the gotchi's probe patterns).

**Target:** 3 clean sessions | **XP:** 135 | **Source:** `auto`

---

### 🗡️ Silent Blade *(Single-tier)*

**What it is:** A single deauthentication that directly results in a
handshake capture — instant efficiency. The deauth and the handshake
must occur within the same 30-second window.

**Target:** 1 precision deauth→handshake | **XP:** 210 | **Source:** `auto`

---

### 👁️ Phantom Protocol *(Single-tier)*

**What it is:** 12 consecutive AP scan epochs completed without the gotchi
broadcasting any frames. The hardest stealth challenge in the system.

**Target:** 12 silent epochs | **XP:** 250 | **Source:** `auto`

---

## 🧭 Category: Exploration

> Missions earned through discovering new network environments, hidden
> infrastructure, and signal spectrum edges.

---

### 🗺️ IoT Cartographer *(Progressive — 5 tiers)*

**What it is:** Rewards discovery of IoT device access points — identified
by OUI prefix matching against known IoT vendor MACs (Shelly, Tuya, ESP8266, etc.).

| Tier | Target | XP |
|---|---|---|
| v1 | 1 IoT device | 15 |
| v2 | 5 IoT devices | 45 |
| v3 | 10 IoT devices | 90 |
| v4 | 20 IoT devices | 170 |
| v5 | 50 IoT devices | 350 |

---

### 🔍 Hidden Network Hunter *(Single-tier)*

**What it is:** Discover 5 access points with hidden SSIDs (empty ESSID
field) across any number of sessions.

**Target:** 5 hidden APs | **XP:** 155 | **Source:** `auto`

---

### 🚀 Air-Gap Jumper *(Single-tier)*

**What it is:** Manually awarded for a successful demonstration of crossing
a network air-gap (physically moving the device between two isolated networks
and establishing a bridge).

**Target:** 1 demonstration | **XP:** 220 | **Source:** `manual`

---

### 🌐 New World Explorer *(Single-tier)*

**What it is:** Awarded on the first scan at a brand-new physical location
with >20 previously-unseen access points. The gotchi has ventured somewhere new.

**Target:** 1 new location | **XP:** 140 | **Source:** `auto`

---

### 📡 Signal Whisperer *(Single-tier)*

**What it is:** Detect 10 access points at the edge of range (RSSI < -85 dBm),
demonstrating antenna quality or elevated physical placement.

**Target:** 10 weak-signal APs | **XP:** 100 | **Source:** `auto`

---

### 🌈 Spectrum Master *(Single-tier)*

**What it is:** In a single session, observe access points on all three
spectrum tiers: 2.4 GHz (ch 1–13), 5 GHz lower (ch 36–48), and 5 GHz upper
(ch 149–165).

**Target:** 1 full-spectrum session | **XP:** 175 | **Source:** `auto`

---

## 🔧 Category: Maintenance

> Missions earned through system self-maintenance, code quality, and
> active ownership of the gotchi's workspace.

---

### 🖥️ System Admin *(Progressive — 5 tiers)*

**What it is:** Rewards using diagnostic commands (`/status`, `/memory`,
`/health`) to actively monitor and understand the gotchi's state.

**How it triggers:**
- Hook: `command` with action in `{"/status", "/memory", "/health"}`
- File: `aipet_hooks.py` (line 63)

| Tier | Target | XP |
|---|---|---|
| v1 | 1 check | 15 |
| v2 | 5 checks | 50 |
| v3 | 15 checks | 100 |
| v4 | 50 checks | 250 |
| v5 | 150 checks | 500 |

---

### ⚙️ Cron Master *(Progressive — 5 tiers)*

**What it is:** Rewards automation via cron jobs. Using `/cron` or `/jobs`
to schedule recurring tasks earns progress.

**How it triggers:**
- Hook: `command` with action in `{"/cron", "/jobs"}`
- File: `aipet_hooks.py` (line 65)

| Tier | Target | XP |
|---|---|---|
| v1 | 1 job | 15 |
| v2 | 5 jobs | 50 |
| v3 | 15 jobs | 100 |
| v4 | 50 jobs | 250 |
| v5 | 150 jobs | 500 |

---

### 🌀 Code Weaver *(Single-tier)*

**What it is:** Awarded when the gotchi autonomously modifies a source file
in its own codebase and the change survives a syntax check.

**Target:** 1 self-modification | **XP:** 230 | **Source:** `auto`

---

### 🧬 Skill Evolution *(Single-tier)*

**What it is:** Manually awarded by the owner for updating an existing skill
file with meaningful new functionality (not just a rename or comment).

**Target:** 1 skill upgrade | **XP:** 180 | **Source:** `user`

---

### 🧹 Memory Purifier *(Single-tier)*

**What it is:** Rewards regular memory hygiene — flushing stale or
contradictory facts from the memory store. Target of 50 memory-cleanup events.

**Target:** 50 cleanup events | **XP:** 90 | **Source:** `auto`

---

### 🔒 Git Guardian *(Single-tier)*

**What it is:** Rewards consistent version control discipline — 7 git commits
with proper Conventional Commit messages.

**Target:** 7 commits | **XP:** 120 | **Source:** `auto`

---

### 🎨 Identity Sculptor *(Single-tier)*

**What it is:** Manually awarded when the owner has fully customised the
gotchi's personality — including `SOUL.md`, `IDENTITY.md`, and `USER.md`.

**Target:** 1 personality overhaul | **XP:** 200 | **Source:** `user`

---

### 🎯 Weekly Bounty *(Single-tier)*

**What it is:** A rotating weekly challenge set by the owner. The specific
goal is defined in `USER.md` and manually completed via Discord command.

**Target:** 1 weekly goal | **XP:** 400 | **Source:** `user`

---

## 🌟 Category: Epic

> Endgame missions requiring mastery across multiple categories simultaneously.
> These are the most prestigious achievements in the system.

---

### 🌌 The Great Radio Odyssey *(Single-tier)*

**What it is:** Complete 5 full field runs — each run defined as a session
with at least 1 handshake, 1 BLE device, and coverage of 5+ channels.
Tests the full wireless toolkit.

**Target:** 5 complete field runs | **XP:** 450 | **Source:** `multi`

**Requirements per run:**
- ≥1 WPA handshake captured
- ≥1 BLE device logged
- ≥5 distinct WiFi channels covered

---

### 🧠 Cortex Ascension *(Single-tier)*

**What it is:** The ultimate intelligence milestone — 25 total AI interactions
with tool use, memory read/write, and multi-turn reasoning across any period.

**Target:** 25 complex interactions | **XP:** 500 | **Source:** `multi`

**Requirements per interaction:**
- Tool use (at least one function call)
- Memory read or write
- Response spans multiple reasoning turns

---

### 🐝 Swarm Overlord Protocol *(Single-tier)*

**What it is:** The rarest social achievement. Coordinate a mesh swarm of
5+ gotchis simultaneously, sharing scan data and memory context in real time.

**Target:** 5 simultaneous peers | **XP:** 600 | **Source:** `multi`

> **Architecture note:** Requires the mesh networking layer and Bluetooth or
> WiFi P2P protocol to be implemented in `src/extensions/`.

---

## 🔍 Quick Reference — All Missions by Trigger

| Hook / Trigger | Missions Driven |
|:---|:---|
| `pwn.handshake` | Handshake Hunter, Handshake Symphony, Radio God, Silent Blade |
| `pwn.wifi_update` | Rogue AP Detector, network_auditor evil-twin, 5GHz Pioneer, Channel Hopper |
| `pwn.deauth` | Pwn Sniper *(Phase 3)* |
| `pwn.association` | Field Agent *(Phase 3)* |
| `pwn.dns_response` | DNS Defender *(Phase 3)* |
| `pwn.bcap.wifi_ap_new` | network_auditor Cyber Sentinel |
| `heartbeat` | Ironclad Uptime, Thermal Guardian, Power Efficient, Memory Monk |
| `message` | Deep Thought, Chatterbox, Night Owl |
| `command: /remember` | The Teacher, Memory Weaver |
| `command: /recall` | The Historian |
| `command: /status /memory /health` | System Admin |
| `command: /cron /jobs` | Cron Master |
| `trigger_dream()` | Synthetic Strategist, Dream Weaver, AI Philosopher |
| `user` (manual) | Skill Forger, Skill Architect, Power Sage, Identity Sculptor, Weekly Bounty |
| `manual` | First Contact, Ambassador, Air-Gap Jumper, Swarm Coordinator |
| `multi` | The Great Radio Odyssey, Cortex Ascension, Swarm Overlord Protocol |

---

## 🔢 XP Summary — Total Achievable XP

| Category | Progressive Missions (total) | Single Missions (total) |
|:---|---|---|
| Radio | 585 + 585 + 615 + 585 | 120+95+150+180+110+130+250+160 = 1,195 |
| Cortex | 690 + 545 + 610 | 160+90+140+220+180+150+200+250 = 1,390 |
| Social | 915 + 915 + 915 + 915 + 570 | 200+160+280+130+240+190 = 1,200 |
| Uptime | 715 + 420 | 180+140+160+110+125+300+130 = 1,145 |
| Stealth | — | 170+145+190+135+210+250 = 1,100 |
| Exploration | 670 | 155+220+140+100+175 = 790 |
| Maintenance | 915 + 915 | 230+180+90+120+200+400 = 1,220 |
| Epic | — | 450+500+600 = 1,550 |

**Total base XP pool: ~18,300 XP**
*(Excluding per-event bonuses like the +5 XP per handshake from `add_xp()`)*

---

*Last updated: Phase 2 completion — deauth_handler, network_auditor, extended BasePlugin compat layer.*
*For implementation details see [`docs/development/pwnagotchi_plugins_integration.md`](file:///Users/js66/.gemini/antigravity-ide/scratch/openclawgotchi_V4/docs/development/pwnagotchi_plugins_integration.md).*
