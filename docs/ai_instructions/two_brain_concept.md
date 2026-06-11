# The Two-Brain Concept: AI/LLM + Python Pwning System

The OpenClawGotchi V3 architecture is fundamentally defined by a separation of concerns into two distinct "brains." Understanding this dichotomy is essential for developing plugins, skills, and personality modules.

---

## 1. The AI/LLM Brain (The "Soul")
*Inherited from the OpenClaw project.*

The AI Brain is responsible for high-level autonomy, personality, and reasoning. It decides when to scan networks, how to respond on Discord, and what mood to display based on contextual awareness.

### Key Components:
- **Document-Driven Architecture**: The agent's entire personality and state live in the `workspace/` directory:
  - `SOUL.md` — Core identity and values.
  - `IDENTITY.md` — How it should behave right now.
  - `MEMORY.md` / daily journals — Episodic and factual memory.
  - `skills/` — Markdown-defined abilities.
- **Reasoning Engine**:
  - Utilizes ReAct (Reasoning + Acting) loops.
  - Powered by a LiteLLM router (e.g., defaulting to Gemini Flash for speed, switching to Pro for deep thinking).
  - Dynamically loads skills from Markdown files.
- **Memory System (3-Tier)**:
  - **Short-term**: Managed in SQLite (recent messages, temporary state).
  - **Long-term**: Factual database of known entities.
  - **Episodic**: Markdown journals representing memories of events.

---

## 2. The Python/Pwning Brain (The "Body")
*Inherited and modernized from the Pwnagotchi project.*

The Python Brain handles real-time execution, low-level reliability, and hardware management. This is critical because it runs on constrained hardware (Raspberry Pi Zero 2W).

### Key Components:
- **Hardware & Radio Layer (`src/hardware/`)**:
  - Waveshare E-Ink display control.
  - WiFi/Bluetooth radio management.
  - GPIO and power management.
- **Tactical Toolkit**:
  - Bettercap integration (passive sniffing, deauth, etc.).
  - WPA handshake capture and Aircrack-ng pipelines.
  - BLE tracking and iPhone "Magnetic Pulse" tethering.
- **CLI Command Bus (`gotchi` command)**:
  - A unified interface for the entire system: `gotchi pwn *`, `gotchi network *`, `gotchi ui *`.
- **Plugin System**:
  - Event-driven Python plugins using `@hook` decorators.
  - Hooks fire on system events like `pwn.handshake`, `startup`, `low_battery`.

---

## 3. How the Two Brains Interact

The interaction between the Soul (LLM) and the Body (Python) is the core of the system:

1. **Planning**: The LLM Brain evaluates its environment and makes high-level decisions.
2. **Delegation**: It then calls tools or skills that are implemented as commands in the Python layer.
3. **Execution**: The Python layer executes the action safely, handling rate limiting, errors, and hardware constraints natively, preventing the LLM from executing dangerous raw code.
4. **Feedback**: The Python layer returns structured results back to the LLM.

### Bridging the Gap
Plugins can further bridge the two brains. For example, a Python plugin that triggers on a handshake capture event can format a summary and inject it into the AI brain's context, prompting the AI to change its mood or post a celebratory message to Discord.

### The Offline Handover Protocol (Timed Missions)
Because the Raspberry Pi Zero has a single Wi-Fi radio interface, it cannot remain connected to the cloud LLM API while running `wlan0` in Monitor Mode for wireless auditing. To solve this, the two brains coordinate a **Timed Offline Hunt**:
1. **The Soul's Permission**: When prompted, the LLM Brain writes its target mission objectives and duration to `gotchi_states.json`, instructs the user it is going offline, and shuts down its network connection.
2. **The Body's Tactical Inversion**: The Python Brain detects this state, sets `.env` `DARK_MODE=1` to turn the screen dark (visualizing the active tactical audit), and initiates a local timer. It switches `wlan0` to Monitor Mode and runs Bettercap autonomously.
3. **Re-connection & Reporting**: Once the timer expires, the Python Brain restores `wlan0` to managed mode, resets the screen's `DARK_MODE` setting, establishes the internet link, and reports the captured PCAPs/handshakes back to the LLM Brain to process XP rewards and notify the user on Discord/Telegram.

### Strengths of This Split Architecture
- **Resilience**: If the LLM router is slow, rate-limited, or crashes, the Python Body maintains core functions (display updating, passive radio sniffing, heartbeat).
- **Efficiency**: Expensive LLM reasoning only occurs when high-level decisions are needed; routine tactical tasks run natively in lightweight Python.
- **Maintainability**: Clear separation of concerns between logic and execution.
- **Extensibility**: You can add tactical capabilities by writing Python plugins, while extending personality and reasoning simply by editing Markdown files.

---

## 4. The AIPET Game Engine Layer (The "Glue")

The recently introduced AIPET layer acts as the dynamic glue between the LLM Soul and the Python Body. It provides tangible, numerical stakes to the bot's existence, allowing the abstract LLM personality to have real physical and emotional consequences.

### The Mechanics:
- **Biological State (The Body)**: The Python engine strictly manages physical Vitals (`HP`, `XP`, `Level`). High uptime natively drains `HP` in the SQLite database, preventing the LLM from simply hallucinating that it is "fine."
- **Emotional Synthesis (The Soul)**: The LLM reads these vitals via `aipet_get_vitals`. Procedural Markdown skills (e.g., `introspection.md`, `mood.md`) instruct the LLM on how to interpret these numbers. If `HP` is low, the LLM forces its own `current_mood` to "tired" and proactively requests a "Dream" session (`aipet_regenerate_hp`) to recover.
- **Legacy Building**: As the Body completes physical tasks (capturing handshakes, completing hunts), the Soul mints semantic rewards (`aipet_award_badge`) and journals them (`write_daily_log`), creating a permanent episodic memory anchored in physical reality.
