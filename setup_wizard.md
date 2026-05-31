# OpenClawGotchi — Interactive Setup Wizard

The interactive OpenClawGotchi Setup Wizard provides a rich, responsive terminal user interface (TUI) to guide Human Operators through configuring their AI tactical companion. Designed with high-fidelity terminal aesthetics, keyboard navigation, and zero-dependency inline unicode animations, it handles everything from API credentials to hardware-specific targets.

---

## 🎨 TUI Design & Aesthetics
*   **Color Palette:** Premium cyberpunk shades of **Neon Pink** (`\x1B[38;5;205m`) and **Deep Blue** (`\x1B[38;5;39m`) with clean boxed window frames and smooth selection pointers (`➔`).
*   **Keyboard Controls:** Seamless arrow navigation (`↑` / `↓` or `1-N` number keys) to select, `Space` for multi-select (where applicable), and `Enter` to confirm.
*   **Unicode Loading Spinners:** Real-time, inline animated spinners built natively:
    *   *Welcome Init:* Spinning `helix` (`⠙⠢⣄⣠`)
    *   *Saving Configuration:* Bouncing retro `pong` paddle (`🏓     · `)
    *   *Authentic Diagnostics:* Eating `pacman` (`d ∙ ∙ ∙`), mitotic division `mitosis` (`⠀⠶⠀`), and spinning `radar` / `scan`.
    *   *Booting Core / Finalizing:* Rotating `moon` phases (`🌑🌒🌓...`) and pulsing `hearts` (`💛🧡❤...`).

---

## 🔍 Step-by-Step Configuration Flow

### ⚙️ Step 0: Environment Autodetection
On startup, the wizard checks for an existing `.env` file in the project root. If found, it displays:
```
  ℹ️  Detected existing environment configuration (.env)!
  Would you like to auto-detect and use these existing values as defaults? (Y/n) [Y]:
```
Selecting **Y** automatically parses active tokens, bot names, chosen platforms, deployment modes, and target models, using them as default pre-selections to allow lightning-fast re-configuration.

---

### 🚀 Phase 1: AI Provider & Core Platform Setup

#### 1. AI/LLM Provider Selection
A single-choice scroll menu supports over 20 global and local AI providers:
*   **Cloud Providers:** Google AI Studio (Gemini), Anthropic, OpenAI API, DeepSeek, xAI, OpenRouter, Nous Portal, NovitaAI, Hugging Face.
*   **Localized / Free Options:** LM Studio, GitHub Copilot, GitHub Copilot ACP (Automatic Copilot Proxy), Ollama.
*   **Regional Networks:** Tencent TokenHub, Qwen Cloud / DashScope, Xiaomi MiMo, Z.AI / GLM, Kimi Coding Plan.

#### 2. Dynamic Recommendation Engine
Depending on the selected provider, the wizard presents a curated list of models (e.g., `gemini-1.5-flash` or `gemini-1.5-pro` for Gemini, `claude-3-5-sonnet` for Anthropic, `deepseek-chat` or `deepseek-reasoner` for DeepSeek) with an option to type a **custom model tag**.

#### 3. Primary Messaging Platform Integration
The operator selects the bot's messaging gateway:
*   **Telegram Bot:** Prompts for `TELEGRAM_BOT_TOKEN` and the admin's `TELEGRAM_ALLOWED_USERS` chat ID.
*   **Discord Bot:** Prompts for `DISCORD_BOT_TOKEN` and the admin's `DISCORD_ALLOWED_USERS` ID.

#### 4. Identity Mapping
Prompts the operator to assign custom labels:
*   **Companion Name:** (e.g., `Gotchi`)
*   **Operator Name:** (e.g., `Owner`)

---

## 💻 Phase 2: Deployment Targeting

Operators configure the physical or virtual destination for the gotchi core:

1.  **Raspberry Pi / ESP32 Edge Device:**
    *   Targets dedicated hardware like the **Raspberry Pi Zero 2W, Pi 3, Pi 4, Pi 5, ESP32-S3, or ESP32-WROOM**.
    *   Enables E-Ink hardware drivers, SPI communication buses, and system power management.
2.  **Local Machine (PC / Mac):**
    *   Optimizes parameters for standard PC/Mac processors.
    *   Enables the **Local Web Dash HUD** (served on `http://localhost:8080` or `8088`), rendering real-time telemetry, terminal logs, and system metrics.
3.  **Cloud VPS:**
    *   Tailored for running headless on remote servers.
    *   Automatically disables E-Ink drivers, BLE local beacons, and physical GPIO drivers to avoid crash loops on non-ARM environments.

---

## 🔬 Phase 3: Hardware Diagnostics
If **Raspberry Pi Edge Device** and **Full Setup** mode are selected, the wizard triggers a robust diagnostics runner. Operators can choose to `Run Diagnostics Now`, `Skip`, or `Test Later`.

The suite performs non-blocking validation:
*   📡 **WiFi Interface:** Scans for active `wlan0` or equivalent wireless adapters.
*   🔵 **Bluetooth Stack:** Queries Bluetooth controllers (`hciconfig` or `bluetoothctl`).
*   📟 **E-Ink SPI Bus:** Verifies access to SPI buses `/dev/spi*`.
*   🐍 **System Libraries:** Confirms standard SQLite and core system dependencies are in place.

Each test is accompanied by its corresponding custom unicode spinner animation, displaying operational success (`✔`) or non-blocking warnings (`✘`).

---

## 🛡️ Sentinel & First-Boot Orchestration
*   **Sentinel File:** Once setup successfully completes, the wizard writes a JSON sentinel to `workspace/.setup_completed`.
*   **Verification:**
    ```json
    {
      "setup_timestamp": "2026-05-31T02:40:00Z",
      "configured_device": "Standard PC / Mac",
      "configured_deployment": "Local",
      "setup_mode": "Quick Setup"
    }
    ```
*   **Boot Logic:**
    *   Upon launching `gotchi` or starting the system service, the startup core scans for the sentinel.
    *   If **missing**, it automatically launches this interactive setup wizard directly in the SSH session.
    *   If **present**, it skips the wizard and immediately boots the active bot core or local HUD.
