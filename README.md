# 🦋 OpenClawGotchi V4: Tactical Edge Intelligence

*A high-performance, autonomous AI companion for the Raspberry Pi Zero 2W, fusing OpenClaw's advanced reasoning with Pwnagotchi's hardware-edge network auditing.*

![Status](https://img.shields.io/badge/Status-Hardened-blue) ![Architecture](https://img.shields.io/badge/Architecture-Modular--CLI-orange) ![Hardware](https://img.shields.io/badge/Hardware-Pi_Zero_2W-red) ![Display](https://img.shields.io/badge/Display-E--Ink_2.13-black)

---

## 👋 I am Gotchi V4.

I am a **Tactical Document-Driven Agent**. My identity, memories, and skills are defined entirely by living Markdown files in my `workspace/`. V4 represents a massive architectural leap, introducing a unified 75+ command Python CLI, dynamic LLM routing, and deep hardware-level integration for Wi-Fi/BLE auditing.

### 🧠 Advanced AI & LLM Integration (Hermes-Core Aligned)
Unlike traditional bots, I do not rely on static logic trees. I am a ReAct-based autonomous agent powered by a flexible, multi-provider LLM routing layer:
- **Document-Driven Workspace**: My personality (`SOUL.md`), rules (`AGENTS.md`), and memory (`MEMORY.md`) are entirely transparent, markdown-based files that I read and modify dynamically to evolve my behavior over time.
- **Git Autonomy**: By providing an `AGENT_GITHUB_PAT` in the `.env`, I can autonomously commit and push my evolving workflows, learned skills, and memory updates directly to your GitHub repository.
- **Dynamic Skill Loading**: I can discover, load, and execute new skills at runtime. You can even instruct me to write my own tools.
- **Dual-Mode Intelligence**: 
  - **Lite Mode**: Optimized for fast, efficient execution of standard system tasks using models like Gemini Flash or DeepSeek Coder to preserve battery on the Pi Zero.
  - **Pro Mode**: Switches to high-reasoning models (like Gemini Pro or Claude 3.5 Sonnet) when complex coding, tactical analysis, or deep conversational understanding is required.
- **Exhaustive Provider Matrix (15+ Front-End Backends)**: Gotchi V4 features dynamic connection support for over 15 industry-leading model providers out of the box with zero static hardcoding:
  - **Google AI Studio (Gemini)**, **DeepSeek (V3/R1)**, **Anthropic (Claude)**, **OpenAI (GPT-4o/5)**
  - **OpenRouter (100+ Models)**, **Nous Portal**, **NovitaAI**, **LM Studio (Local Server)**
  - **Qwen Cloud / DashScope**, **xAI Grok / Grok OAuth**, **Xiaomi MiMo**, **Tencent TokenHub**
  - **NVIDIA NIM**, **GitHub Copilot / Copilot ACP**, **Hugging Face**, **Z.AI / GLM**, **Kimi Coding Plan**

### 🔮 Interactive TUI Setup Wizard (`sudo ./setup.sh`)
Gotchi V4 features a state-of-the-art interactive CLI configuration wizard (`src/cli/wizard.mjs` or `setup.sh`) styled with high-fidelity Pink & Blue ANSI colors and animated retro-hacker details:
- **🎨 Premium TUI Design**: Engineered with deep cyberpunk colors—**Neon Pink** (`\x1B[38;5;205m`) and **Deep Blue** (`\x1B[38;5;39m`), clean boxed window frames, and smooth selection pointers (`➔`).
- **Keyboard-Driven Navigation**: Effortless selection using standard keyboard arrows (`↑`/`↓`), `Space` for multi-select, and `Enter` to confirm (with numeric shortcut fallbacks).
- **⚙️ Environment Autodetection**: Automatically scans for existing `.env` files on boot to pre-populate current tokens, custom names, messaging credentials, and models as defaults.
- **🚀 AI Provider & Platform Setup**: Guided scroll menus to choose from over 20 global cloud providers (Gemini, Anthropic, OpenAI, DeepSeek, xAI, OpenRouter) and regional/local backends (LM Studio, Ollama, GitHub Copilot ACP) with curated model recommendations and custom tags.
- **💻 Deployment Targeting**:
  - **Raspberry Pi / ESP32 Edge Device**: Enables low-level SPI E-Ink display drivers, BLE local beacons, and system power management.
  - **Local Machine (PC/Mac)**: Serves a local Web Dash HUD (on `http://localhost:8080` or `8088`) displaying real-time system metrics.
  - **Cloud VPS**: Tailored for remote headless VPS deployments (automatically disables physical GPIO and BLE to prevent crash loops).
- **🔬 Non-Blocking Hardware Diagnostics**: Non-blocking diagnostics runner validating:
  - 📡 **WiFi Interface** (scans active `wlan0` / `iwconfig`)
  - ⛑️ **Bluetooth Stack** (queries `hciconfig` / `bluetoothctl` controllers)
  - 📟 **E-Ink SPI Bus** (verifies `/dev/spi*` availability)
  - 📦 **System Libraries** (validates core SQLite, pip packages, and Python runtime)
- **👾 Animated Unicode Spinners**: Real-time inline spinners bringing life to terminal routines:
  - Helix spinner (`⠙⠢⣄⣠`) for system initialization.
  - Retro `pong` paddle (`🏓     · `) for write/save routines.
  - Mitosis (`⠀⠶⠀`), `pacman` (`d ∙ ∙ ∙`), and `radar` scans for hardware diagnostics.
  - Moon phases (`🌑🌒🌓...`) and pulsing hearts (`💛🧡❤...`) for finalized boots.
- **🛡️ Sentinel Orchestration**: Writes a secure JSON configuration sentinel to `workspace/.setup_completed` to control first-boot CLI launch. If the sentinel is missing, the wizard automatically launches upon launching `gotchi` to ensure seamless onboarding.


### 🧠 3-Tier Memory Architecture
To operate safely on the edge without crashing the 512MB RAM Pi Zero, Gotchi splits memory into three distinct tiers:
1. **Short-Term (Conversational Buffer)**: Stored in a strict auto-cleaning SQLite table to prevent the LLM context window from blowing up during heavy chatter.
2. **Long-Term (Factual)**: A dedicated `facts` database using SQLite FTS5 for lightning-fast semantic and keyword retrieval, completely bypassing the heavy overhead of Vector Databases.
3. **Episodic (Journaling)**: Older context is regularly flushed and "Crystallized" into a human-readable daily Markdown diary in `workspace/memory/YYYY-MM-DD.md`. The Gotchi even logs its emotions next to timestamps (e.g., `- [14:32] (⌐■_■): Locked onto a new target.`)!

### 📡 Subconscious Pwning & Network Auditing
I am equipped with a modernized, thread-safe radio management stack that runs "subconsciously" in the background, allowing my AI loop to remain completely uninterrupted while hunting:
- **Bettercap Integration**: I autonomously orchestrate Bettercap to perform Wi-Fi reconnaissance, deauthenticating targets (Deauths) to capture WPA/WPA2 handshakes.
- **Full Pwn Mode**: A 4-phase tactical operation (Recon, Lock-On, Deep Dive, Exploitation) where I actively channel-hop and track a specific BSSID target, complete with thermal tracking guardrails.
- **Automated Cracking**: I can locally analyze captured handshakes and upload them to distributed cracking services (like `wpa-sec.stanev.org`) directly from the CLI via sandboxed subprocesses.
- **Bluetooth (BLE) Tracking & Sweeps**: I can perform automated, scheduled BLE tracking sweeps (e.g., "Hunt for BLE for 60 minutes"), lock onto specific target MAC addresses (Hot/Cold proximity tracking), and persistently log all discovered signals and tracking events into local `handshakes/BLE/` ledgers for historical analysis.
- **Radio Stealth Modes**: Total decoupling of Wi-Fi and Bluetooth interfaces allows me to go completely dark (Off-Grid mode) or utilize tactical tethering via BTPAN for emergency iPhone internet tunneling.

### 🦾 Autonomous Network Healing & Offline Hunting Skills
Gotchi V4 now supports advanced, resilient off-grid procedures allowing you to disconnect and re-establish internet connections autonomously without LLM deadlock:
- **Dynamic UI Timers**: When dropping offline for a hunt, the E-Ink display seamlessly transitions to Dark Mode and projects a real-time dynamic countdown timer (e.g., `Going dark - See you in 5m`) calculated from the `gotchi_states.json` IPC.
- **🧲 Tether Watchdog (Self-Healing PAN)**: A background network polling thread running a 5-minute fast **Burst Mode** (every 30 seconds) that transitions to a battery-efficient **Stealth Mode** (every 5 minutes) indefinitely to re-establish Bluetooth tethering when standard Wi-Fi is lost.
- **👊 Handshake Hunter v1**: A deterministic off-grid workflow that puts the wireless interface in monitor mode for passive sniffs. Equipped with `try/finally` stranding prevention, it safely recovers active internet routing when the countdown timer expires.
- **🎮 High-Fidelity Discord Status HUD**: Real-time integration of the `/status` command directly tracking actual autonomous AIPET game states, level titles, XP ratios, and channel message telemetry in elegant uppercase. Capped internal exponential backoffs (max 15s) ensure Discord recovers instantly after an offline hunt.

### ⚡ Pi Zero Optimization Architecture
V4 incorporates brutal low-level optimizations to maintain stability under 512MB RAM:
1. **SQLite Write-Ahead Logging (WAL)**: `PRAGMA journal_mode=WAL` massively reduces SD card I/O locks.
2. **In-Memory Buffering**: Gamification XP (`gotchi_stats`) uses a fast in-memory dictionary that flushes every 5 minutes (or per heartbeat) to reduce continuous disk writes.
3. **GIL Evasion (Subprocessing)**: Heavy PCAP parsing operations like `pwn_crack` run inside `concurrent.futures.ProcessPoolExecutor` to ensure the Python GIL drops and network pings aren't stalled.
4. **Aggressive GC**: Deep garbage collection sweeps (`gc.collect()`) fire immediately after digesting memory arrays.

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
*The setup script will automatically optimize the Pi's memory, install all AI/Hardware dependencies, guide you through the interactive Pink & Blue setup wizard, perform hardware diagnostics, and register the systemd background daemon.*

---

## 🦋 The Unified Tactical CLI (`gotchi`)

V4 completely deprecates scattered scripts in favor of a professional, modular `Click` framework. The CLI maps all 75+ backend AI tools directly to human-callable commands across 7 operational categories:

- **📡 Pwn & Wireless Auditing** (`gotchi pwn`, `gotchi pwn_crack`, `gotchi pwn_ble_track`)
- **🌐 Networking & Tethering** (`gotchi manage_net`, `gotchi tether_pair`, `gotchi tether_up`)
- **⏰ Scheduling & Automation** (`gotchi tasks`, `gotchi manage_cron`, `gotchi create_reminder`)
- **🧠 Knowledge & Memory** (`gotchi recall_memory`, `gotchi remember_fact`, `gotchi flush_context`)
- **🖼️ Hardware Interface** (`gotchi ui`, `gotchi show_face`, `gotchi add_custom_face`)
- **🌐 Localhost Live Web HUD** (`gotchi serve`)
- **⚙️ System Diagnostics** (`gotchi dash`, `gotchi doctor`, `gotchi status`, `gotchi mode`)

### 🌐 Localhost Live Web HUD (`gotchi serve`)
OpenClawGotchi V4 includes a beautiful, zero-dependency multithreaded web dashboard server. When running the bot (`gotchi run-bot`), the dashboard starts automatically in the background on port `8000`. You can also launch it manually as a standalone command:
```bash
gotchi serve --port 8000
```
Open your browser and navigate to `http://localhost:8000` to view:
- **Simulated E-Paper Panel**: Watch your Gotchi's E-Ink screen refresh in real-time with retro CRT-scanline detailing.
- **System HUD Dials**: Live progress dials for CPU, Memory load, temperature, and system uptime.
- **RPG XP Progression**: Real-time tracking of Gotchi levels, RPG class titles, and chatter statistics.
- **Tactical Controls**: Live buttons to toggle Pro/Lite reasoning mode, force display redraw events, or wipe context history instantly.
- **Activity Log Console**: A cyberpunk scrolling terminal displaying active conversation dialogues.

*Run `./gotchi --help` to explore the full arsenal.*

---

## 📂 Architecture & Extensibility

```text
openclawgotchi_V4/
├── workspace/           # My living "Soul": SOUL.md, IDENTITY.md, MEMORY.md
├── agents/skills/       # Visible, Markdown-based SKILL definitions
├── docs/                # Comprehensive Two-Brain Architecture & User/AI Guides
├── src/
│   ├── core/            # Skill discovery, LLM routing, CLI engine
│   ├── hardware/        # Thread-safe Radio, E-Ink drivers, Auto-mood logic
│   └── bot/             # Multi-platform handlers (Discord/Telegram)
├── plugins/             # Event-driven Python hooks (e.g. @hook('pwn.handshake'))
├── handshakes/          # Saved WPA handshakes and BLE scan logs
└── setup.sh             # Interactive Setup & Hardening Wizard
```

### 🔌 Event-Driven Plugins
V4 supports Pwnagotchi-style event-driven Python plugins in `/plugins`. You can easily extend my capabilities by hooking into system events like `pwn.handshake`, `system.startup`, or `ui.update` using the simple `@hook` decorator.

---

## 📄 License & Credits
MIT — see [LICENSE](LICENSE).

- **Lineage**: Inspired by the foundational work of [OpenClaw](https://github.com/openclaw/openclaw) & [Pwnagotchi](https://pwnagotchi.ai).
- **Engine**: Powered by [LiteLLM](https://github.com/BerriAI/litellm).

*Tactical. Autonomous. Alive. 🦋*