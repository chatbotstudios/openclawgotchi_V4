# 🦋 OpenClawGotchi V4.3: Tactical Edge Intelligence

*A high-performance, autonomous AI companion for the Raspberry Pi Zero 2W, fusing OpenClaw's advanced reasoning with Pwnagotchi's hardware-edge network auditing.*

![Status](https://img.shields.io/badge/Status-Hardened-blue) ![Architecture](https://img.shields.io/badge/Architecture-Modular--CLI-orange) ![Hardware](https://img.shields.io/badge/Hardware-Pi_Zero_2W-red) ![Display](https://img.shields.io/badge/Display-E--Ink_2.13-black)

---

## 👋 I am Gotchi V4.3.

I am a **Tactical Document-Driven Agent**. My identity, memories, and skills are defined entirely by living Markdown files in my `workspace/` and `templates/` directory. V4.3 introduces the Event-Driven State Manager, The Restful Dream Patch, and hitless Dual Uplink architecture.

### 🧠 Advanced AI & LLM Integration (Hermes-Core Aligned)
Unlike traditional bots, I do not rely on static logic trees. I am a ReAct-based autonomous agent powered by a flexible, multi-provider LLM routing layer:
- **Document-Driven Workspace**: My personality (`SOUL.md`), rules (`AGENTS.md`), and memory (`MEMORY.md`) are entirely transparent, markdown-based files that I read and modify dynamically to evolve my behavior over time.
- **Git Autonomy**: By providing an `AGENT_GITHUB_PAT` in the `.env`, I can autonomously commit and push my evolving workflows, learned skills, and memory updates directly to your GitHub repository.
- **Dynamic Skill Loading**: I can discover, load, and execute new skills at runtime. You can even instruct me to write my own tools.
- **Dual-Mode Intelligence**: 
  - **Lite Mode**: Optimized for fast, efficient execution of standard system tasks using models like Gemini Flash or DeepSeek Coder to preserve battery on the Pi Zero.
  - **Pro Mode**: Switches to high-reasoning models (like Gemini Pro or Claude 3.5 Sonnet) when complex coding, tactical analysis, or deep conversational understanding is required.
- **Exhaustive Provider Matrix**: Gotchi V4.3 features dynamic connection support for over 15 industry-leading model providers out of the box with zero static hardcoding.

### 🔮 Interactive TUI Setup Wizard (`sudo ./setup.sh`)
Gotchi V4.3 features a state-of-the-art interactive CLI configuration wizard (`src/cli/wizard.mjs` or `setup.sh`) styled with high-fidelity Pink & Blue ANSI colors and animated retro-hacker details.
- **⚙️ Environment Autodetection**: Automatically scans for existing `.env` files on boot.
- **🚀 AI Provider Setup**: Guided scroll menus to choose from global cloud providers.
- **💻 Deployment Targeting**: Tailors setup for Raspberry Pi / ESP32 Edge Device, Local Machine (PC/Mac), or Cloud VPS.
- **🔬 Non-Blocking Hardware Diagnostics**: Validates WiFi, Bluetooth, E-Ink SPI Bus, and Python runtime.

### 🧠 3-Tier Memory Architecture
To operate safely on the edge without crashing the 512MB RAM Pi Zero, Gotchi splits memory into three distinct tiers:
1. **Short-Term (Conversational Buffer)**: Stored in an auto-cleaning SQLite table to prevent the LLM context window from blowing up.
2. **Long-Term (Factual)**: A dedicated `facts` database using SQLite FTS5 for lightning-fast semantic retrieval, completely bypassing the overhead of Vector Databases.
3. **Episodic (Journaling)**: Older context is regularly flushed and "Crystallized" into a human-readable daily Markdown diary in `workspace/memory/YYYY-MM-DD.md`.

### 👾 The AIPET Game Engine Layer
Gotchi is not just a reactive script; it is a fully autonomous digital pet powered by an **Event-Driven Engine** (`EventBus` & RAM-cached `StateManager`).
- **Physical Vitals**: The Gotchi monitors its own simulated biology. High CPU load and extended uptime cause HP decay. To recover, it can autonomously invoke a `Dream` state to rest (The Restful Dream Patch organically regenerates +10 HP without rebooting).
- **RPG Progression**: A strict 1-100 Leveling system. The Gotchi earns XP for passive tasks and can self-reward XP for meaningful interactions. As it levels up, its "Title" evolves.
- **Rewards & Milestones**: An internal ledger tracks Badges as permanent legacies.
- **Emotional Intelligence**: A dynamic `Mood` system directly linked to its E-Ink face.

### 📡 Subconscious Pwning & Network Auditing
I am equipped with a modernized, thread-safe radio management stack that runs "subconsciously" in the background:
- **Bettercap Integration**: I autonomously orchestrate Bettercap to perform Wi-Fi reconnaissance and deauthenticate targets to capture WPA handshakes.
- **Automated Cracking**: I can locally analyze captured handshakes and upload them to distributed cracking services directly from the CLI.
- **Bluetooth (BLE) Tracking & Sweeps**: Scheduled BLE tracking sweeps and hot/cold proximity tracking.

### 🦾 Autonomous Network Healing & Dual Uplink Architecture
Gotchi V4.3 supports advanced, resilient off-grid procedures:
- **Dual Uplink (Hitless Transition)**: The Gotchi supports maintaining active connections on both Wi-Fi (`wlan0`) and Bluetooth PAN (`bnep0`) simultaneously. `wlan0` handles primary traffic, and `bnep0` acts as a hot-standby redundant uplink. If `wlan0` drops (or is forced into Monitor Mode for hunting), Linux routing instantly falls back to the iPhone Tether without breaking the active Discord/LLM connection!
- **Dynamic UI Timers**: When dropping offline for a hunt, the E-Ink display seamlessly projects a real-time dynamic countdown timer.
- **Handshake Hunter**: A deterministic off-grid workflow that safely recovers active internet routing when the countdown timer expires.

### ⚡ Pi Zero Optimization Architecture
V4.3 incorporates brutal low-level optimizations to maintain stability under 512MB RAM:
1. **SQLite Write-Ahead Logging (WAL)**: Massively reduces SD card I/O locks.
2. **StateManager RAM Buffer**: Gamification and core vitals use a RAM-caching Singleton to prevent SD-card I/O spam.
3. **GIL Evasion (Subprocessing)**: Heavy PCAP parsing operations run inside `concurrent.futures.ProcessPoolExecutor`.
4. **Aggressive GC**: Deep garbage collection sweeps (`gc.collect()`) fire immediately after digesting memory arrays.

---

## ⚠️ Important Safety & Data Rules

- **CRITICAL GIT RULE (Gotchi Branch):** NEVER run `git checkout gotchi` manually. SQLite databases are tracked on the remote `gotchi` branch but ignored on `master`. Checking out the branch manually will cause Git to permanently delete your brain from the filesystem. ALWAYS use the `./backup_brain.sh` script instead.
- **Do not overwrite critical display code:** `src/ui/gotchi_ui.py` and `src/drivers/` are the E-Ink stack. Never replace them with backups or write other content into them.
- **Authorized Research Only:** All pwning, hunting, deauthing, and scanning is for research purposes only.

---

## 🚀 Quick Start

### Hardware Requirements
- **Core**: Raspberry Pi Zero 2W (64-bit OS Lite)
- **Face**: Waveshare 2.13" E-Ink (V4 recommended)
- **Power**: High-quality micro-USB power bank.

### Installation
```bash
git clone https://github.com/chatbotstudios/openclawgotchi_V4.git
cd openclawgotchi_V4
sudo ./setup.sh
```
*The setup script will automatically optimize the Pi's memory, install all dependencies, guide you through the interactive setup wizard, and register the systemd daemon.*

---

## 🦋 The Unified Tactical CLI (`gotchi`)

V4.3 uses a professional modular `Click` framework mapping all 75+ backend AI tools directly to human-callable commands across operational categories:
- **📡 Pwn & Wireless Auditing** (`gotchi pwn`, `gotchi pwn_crack`)
- **🌐 Networking & Tethering** (`gotchi manage_net`, `gotchi tether_pair`)
- **⏰ Scheduling & Automation** (`gotchi tasks`, `gotchi manage_cron`)
- **🧠 Knowledge & Memory** (`gotchi recall_memory`, `gotchi remember_fact`)
- **🖼️ Hardware Interface** (`gotchi ui`, `gotchi show_face`)
- **🌐 Localhost Live Web HUD** (`gotchi serve`)
- **⚙️ System Diagnostics** (`gotchi dash`, `gotchi status`)

### 🌐 Localhost Live Web HUD (`gotchi serve`)
OpenClawGotchi V4.3 includes a beautiful, zero-dependency multithreaded web dashboard server hooked directly into the core EventBus.
```bash
gotchi serve --port 8000
```
Open your browser and navigate to `http://localhost:8000` to view:
- **Simulated E-Paper Panel**
- **System HUD Dials** (CPU, Memory, Temp)
- **RPG XP Progression** (Live XP/HP tracking from the state manager)
- **Activity Log Console**

---

## 📂 Architecture & Extensibility

```text
openclawgotchi_V4/
├── workspace/           # Living "Soul" (Live execution)
├── templates/           # Blueprints: SOUL.md, IDENTITY.md, AGENTS.md
├── agents/skills/       # Visible, Markdown-based SKILL definitions
├── docs/                # Comprehensive Two-Brain Architecture
├── src/
│   ├── core/            # LLM routing, CLI engine
│   ├── game_engine/     # EventBus, StateManager, Vitals
│   ├── hardware/        # Thread-safe Radio, E-Ink drivers
│   └── bot/             # Multi-platform handlers
├── plugins/             # Event-driven Python hooks (@hook('pwn.handshake'))
├── handshakes/          # Saved WPA handshakes and BLE logs
└── setup.sh             # Interactive Setup Wizard
```

## 📄 License & Credits
MIT — see [LICENSE](LICENSE).

- **Lineage**: Inspired by the foundational work of [OpenClaw](https://github.com/openclaw/openclaw) & [Pwnagotchi](https://pwnagotchi.ai).
- **Engine**: Powered by [LiteLLM](https://github.com/BerriAI/litellm).

*Tactical. Autonomous. Alive. 🦋*