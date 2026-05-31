# Gotchi Interactive Dashboard: Implementation Plan

## 1. Feature Overview & Goals
**Purpose**: The `gotchi dashboard` command will transform the OpenClawGotchi V3 CLI from a standard logging interface into a dynamic, interactive tactical command center. It will provide the human operator with a unified view of both the LLM "Soul" (mood, context, recent messages) and the Python "Body" (system thermals, RAM, Bettercap scan state, BLE).

**Success Criteria**:
- Must render smoothly on standard SSH terminals.
- Must not consume more than 25MB of RAM or spike the Pi Zero 2W CPU above 15% during steady-state polling.
- Fully keyboard-navigable without reliance on a mouse.
- Provide a faithful ASCII simulation of the current E-Ink display buffer.

## 2. User Interface Design
The dashboard will use a tiled, responsive grid layout.

```text
╭────────────────────────────────────────────────────────────────────────────╮
│ 🦋 OPENCLAWGOTCHI V3  |  MODE: Pro 🧠  |  UPTIME: 14h 23m  |  [LIVE 🔴]      │
├───────────────────────┬─────────────────────────┬──────────────────────────┤
│ 🤖 E-INK SIMULATOR    │ 📊 SYSTEM VITALS        │ 📡 RADIO & PWN           │
│                       │                         │                          │
│     (✜‿‿✜)          │ CPU:  [||||      ] 35%  │ WiFi: RUNNING (wlan0mon) │
│                       │ RAM:  [||||||||  ] 75%  │ APs:  42 tracking        │
│ SAY: Target locked!   │ TEMP: 62.4°C ⚠️         │ BLE:  15 devices         │
│ STATUS: Hunting...    │ SWAP: [||        ] 20%  │ Target: None             │
├───────────────────────┴─────────────────────────┴──────────────────────────┤
│ 🧠 MEMORY & BRAIN (Soul)                                                   │
│ • History: 8/12 msgs | Facts: 142                                          │
│ • Last Msg: "Deploying deauth on target network..." (2m ago)               │
├────────────────────────────────────────────────────────────────────────────┤
│ 📜 RECENT ACTIVITY LOG                                                     │
│ [14:22:01] 📡 Captured WPA handshake for BSSID AA:BB:CC...                 │
│ [14:21:45] 🤖 Mode switched to Lite ⚡                                     │
│ [14:20:11] 🧠 Heartbeat: Reflection summarized 4 messages.                 │
├────────────────────────────────────────────────────────────────────────────┤
│ [Q]uit  |  [R]efresh  |  [P]ause Pwn  |  [M]ood Menu  |  [S]ettings        │
╰────────────────────────────────────────────────────────────────────────────╯
```

**Mood Visualization**:
The E-Ink simulator will pull the active face from `faces.json` based on the current state. Red text for errors, cyan for system nominal, and yellow for warnings.

## 3. Technical Architecture
**Recommended Library**: **Rich** + **Textual** (or just `rich.live` + `rich.layout`).
*Justification*: `Textual` provides an excellent TUI framework with async support natively, but it can be heavy. Given the 512MB RAM constraint, using pure `rich.layout.Layout` combined with `rich.live.Live` running in a dedicated `asyncio` loop is the safest, most performant choice. It avoids the overhead of a full DOM while still providing beautiful borders, tables, and colors.

**Data Sources**:
- **System**: `src/hardware/system.py` (CPU, RAM, Temp). *Optimization: Use direct `/proc` reads, NOT subprocesses.*
- **E-Ink/Mood**: Read the last drawn state from a cached `/tmp/gotchi_ui_state.json` written by the E-Ink daemon.
- **Pwn State**: Make a fast HTTP GET to Bettercap's `localhost:8081/api/session` and read `src/utils/ipc.py` (`DaemonStateManager`).
- **Memory**: Read `messages` table row count and recent logs via `db/memory.py`.

**Live Update Mechanism**:
A master `asyncio` loop that spins every 2.0 seconds. It fetches data concurrently via `asyncio.gather()` to prevent blocking, updates the Rich Layout objects, and lets `Live` render the delta to the terminal.

## 4. Command Design
**Signature**: `gotchi dashboard [OPTIONS]`

**Options**:
- `--refresh-rate <seconds>`: Set polling interval (Default: 2. Min: 1. Max: 60).
- `--compact`: Hides the E-Ink simulator and activity log for tiny SSH windows.
- `--no-color`: Disables ANSI colors (useful for logging or legacy terminals).

**Keyboard Shortcuts** (handled via a background thread reading `sys.stdin` or using the `keyboard` module securely):
- `q`: Quit gracefully.
- `r`: Force immediate refresh.
- `p`: Toggle Pause/Resume on the PwnDaemon.
- `c`: Clear activity log.

## 5. Implementation Steps (Phased)

### Phase 1: Static Layout Foundation
- Install `rich` (if not already in requirements).
- Create the layout grid using `rich.layout.Layout`.
- Populate with dummy data to verify proportions on different terminal sizes.

### Phase 2: Live Data Plumbing
- Implement async fetchers for System, PwnDaemon, and SQLite stats.
- Wire fetchers into a `rich.live.Live(refresh_per_second=1)` context manager.
- Implement the `/proc` native system stat readers to avoid CPU spikes.

### Phase 3: Interactivity
- Implement a non-blocking raw input listener for `q`, `r`, and `p`.
- Wire `p` to `ipc.state_manager.update_key("paused_until", ...)`.

### Phase 4: Polish & Resilience
- Add graceful fallbacks (e.g., if Bettercap is down, the Radio panel shows a gray "OFFLINE").
- Add adaptive refresh rate (slow down if CPU > 80%).

## 6. Folder & File Structure
```text
src/
└── cli/
    └── dashboard/
        ├── __init__.py
        ├── main.py           # Click command entry point & Rich Live loop
        ├── layout.py         # UI definition (Header, Body, Footer)
        ├── fetchers.py       # Async data gatherers (System, Pwn, DB)
        └── keyboard.py       # Non-blocking stdin listener
```
- Integrate into `gotchi` (the main CLI wrapper) by adding `dashboard` to the click group.

## 7. Integration with Two-Brain System
- **The Body (Python)**: Fetches hardware stats directly via `/sys/` and `bettercap` API.
- **The Soul (LLM)**: Reads the latest reflection and memory stats from SQLite. It does *not* query the LLM directly (to avoid triggering a 20s blocking generation).
- **Hooks**: The dashboard will read from the `DATA_DIR / ERROR_LOG.md` and `workspace/memory/` logs to populate the "Recent Activity" feed passively.

## 8. Performance & Resource Considerations
**Pi Zero 2W Constraints**:
- **CPU Budget**: Dashboard must stay under 5-10% CPU use. Frequent `subprocess.Popen` calls are banned. All system stats must be read natively (`/proc/stat`, `/proc/meminfo`).
- **RAM Budget**: Must not exceed 25MB. `rich` is relatively lightweight, but large string buffers (like tailing the full activity log) must be capped (e.g., last 10 lines only).
- **Throttling**: If CPU load average exceeds 2.0, the dashboard should autonomously throttle its refresh rate to 5 seconds.

## 9. Error Handling & Resilience
- **Bettercap Offline**: Radio panel gracefully degrades to `[ API UNREACHABLE ]` without crashing the dashboard.
- **Database Locked**: If `memory.py` throws `sqlite3.OperationalError` (database locked by heartbeat), the dashboard retains the previous memory state and retries on the next tick.
- **Terminal Resize**: `rich.live` handles window resizing naturally, but the layout must be built with relative ratios (e.g., `ratio=2`) rather than fixed character widths.

## 10. Extensibility
- **Widget Registry**: Create a simple base class `DashboardWidget(Protocol)`. If a community plugin (like a GPS tracker) is installed, it can register a widget that the dashboard will append as a new panel in the bottom row.
- **Theming**: Provide `.env` variables like `DASHBOARD_THEME=cyberpunk` (neon pink/cyan) or `DASHBOARD_THEME=tactical` (green/black).

## 11. Testing Strategy
- **Unit Tests**: Mock `psutil` / `/proc` reads and verify `fetchers.py` returns properly formatted dicts.
- **Integration Tests**: Run the dashboard with the mock hardware flag (`HUNT_ON_BOOT=False`) to ensure it doesn't crash when Bettercap is missing.
- **Manual Testing**: SSH from iOS (Termius), macOS (iTerm2), and Windows (PuTTY) to verify ANSI rendering and keyboard responsiveness.

## 12. Potential Challenges & Mitigations
- **Challenge**: SSH latency causing keystroke lag or screen tearing.
  **Mitigation**: Keep the UI delta small. Don't redraw the entire screen, let `rich` optimize the cursor ANSI updates.
- **Challenge**: Reading `/sys/class/thermal/thermal_zone0/temp` requires permissions.
  **Mitigation**: The `gotchi` CLI wrapper uses sudo inherently for certain commands. Ensure the dashboard gracefully handles `PermissionError` by displaying "N/A" instead of crashing.
