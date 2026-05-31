# 📟 OpenClawGotchi V3 — Local Visual HUD Manual

Guidelines and elements structure for developing a comprehensive, glassmorphic visual UI for `openclawgotchi_V4` (served at `http://localhost:8000/`), styled in the cyberpunk aesthetic of the AIPETS UI.

---

## 🎨 UI Core Layout & MUST HAVES

### 1. Header Panel (AI Pet Identity)
*Located at the top of the glassmorphic frame, this area designates the active virtual companion.*

*   **Design**: Sleek cyber font layout displaying:
    *   **AI Pet Identity Name**: `AI PET IDENTITY: Gotchi`
    *   **Context Menu (3-dots)**: A custom dropdown element in the top right opens the `openclawgotchi_V4` `.env` configuration panel.
*   **Purpose**: Manages active pet identity mapping and gives quick access to the system configuration panel.

---

### 2. Braille Dot Matrix Screen (The Primary Display)
*The centerpiece of the dashboard, rendering high-speed visual telemetry of the gotchi in real-time. As tokens are used, tools are called, prompts are generated, the UI updates dynamically to reflect the gotchi's cognitive state and actions.*

*   **Elements**:
    *   **System State Badge**: (`MAIN_SYSTEM_STATES: CONNECTING, ERROR, THINKING, SUCCESS, TOOL LOOP`, as well as `SPECIAL_STATES`) which dynamically changes background color based on the current active state of the gotchi.
    *   **Special System State Badge**: Displays specialized cognitive states (e.g. `pondering`, `contemplating`, `musing`, `cogitating`, `staring into the void`) mapped to their corresponding Unicode color boxes from the gotchi_states.json file.
    *   **Procedural Braille Matrix**: The 5×8 braille dot array is animated dynamically.
    *   **Kaomoji Face Overlay**: Renders the Gotchi's expression natively over the noise: `(ಠ_ಠ)` (smart/angry), `(★ ‿ ★)` (success), `(✖ █ ✖)` (errored), `(● _ ●)` (XP gain), etc.
*   **Procedural Animation Modes**:
    Depending on the active state, the grid applies random mathematical patterns, in the color of the state, to the 5x8 grid of braille cells, creating a dynamic and engaging visual display. 
    
    *   **`wave` (Connecting)**: Shifting phase-shifted row sine waves. Orange glow (`#FF7700`).
    *   **`random` (Thinking)**: High-speed backpropagating neural noise. Deep Blue glow (`#3B82F6`).
    *   **`spiral` (Tool Calls)**: Rotating coordinate spiral loops. Violet glow (`#9B51E0`).
    *   **`cascade` (Success)**: Bottom-up cascade dot accumulation. Emerald glow (`#00FF87`).
    *   **`rain` (Error)**: Cascading vertical digital matrix rain. Crimson glow (`#FF3366`).
    *   **`breathe` (Sleeping)**: Low-frequency breathing-rate brightness sweeps. Slate grey (`#4A5568`).
    *   **`static` (Idle)**: Ambient scan lines.


    ### 3. Agent Thought Box
*A glassmorphic telemetry pane positioned directly below the Braille Dot Matrix Screen.

*   **Design**: Linear glowing frame displaying the current mental state of gotchi. 
    *   **Header**: `AGENT THOUGHT:` in bright magenta.
    *   **Thought Ticker**: Dynamic textual status (e.g., `Failsafe triggered. Core energy state depleted!`).
*   **Purpose**: Exposes what the background AI/LLM or system daemon is contemplating.
*   **Behaviors & Actions**:
    *   **Livelier Ticker Hook**: During `thinking` or `connecting` states, a background polling loop triggers every 1.0 seconds to dynamically synthesize cute kaomojis and technical processes (e.g., `[◉_◉] ┊ wardriving c2c routing table...` or `(⚙_⚙) ┊ inferencing synaptic coefficients...`).
    *. **SPINNER** Add an active spinner if the gotchi is being active


    ### 4. Active Tools Bar
*A golden-bordered telemetry bar displaying current process bindings.*

*   **Design**: Solid dark card backing with contrasting neon gold headers.
    *   **Header**: `ACTIVE TOOLS:`
    *   **Tools List**: Comma-separated active script bindings (e.g., `battery_hibernation, low_power_sleep`).
*   **Purpose**: Lists the exact TOOLS, TOOL_CALLS, TOOL_LOOPS etc loaded or executed live or in the latest transaction cycle (e.g., `wifi_scan`, `espnow_broadcast`, `intel_db_sync`).
*   **Behaviors & Actions**:
    *   Refreshes dynamically on every telemetry event pulse.


### 5. Diagnostic Event Output Logger (Terminal Console)
*A full-width terminal logger positioned at the bottom of the HUD.*

*   **Design**: High-contrast monospace log feed with window control buttons (`CLEAR CONSOLE`, minimize, maximize).
*   **Purpose**: Logs real-time events, network synchronizations, tool calls, prompt success, gotchi messages, system warnings etc in a chronological debug ledger. (most recent/latest on top)
*   **Behaviors & Actions**:
    *   **Clipboard Copy**: Clicking any log entry copies the plain text to the clipboard and shows a toast notification.

    