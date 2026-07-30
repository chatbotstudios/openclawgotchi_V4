"""
OpenClawGotchi V3 — Localhost Web Dashboard Server.
Zero-dependency, multi-threaded HTTP server utilizing standard socketserver and http.server.
Provides live telemetry, simulated E-Ink screen viewing, and tactical controls.
"""

import glob
import http.server
import json
import logging
import os
import socketserver
import threading
import time
from pathlib import Path
from urllib.parse import parse_qs

import psutil

from config import (
    AGENT_GITHUB_PAT,
    BOT_NAME,
    DB_PATH,
    DISCORD_BOT_TOKEN,
    OWNER_NAME,
    PROJECT_DIR,
)

# Dashboard auth token (optional — if set, all endpoints require ?token= or Authorization header)
DASHBOARD_TOKEN = os.environ.get("DASHBOARD_TOKEN", "").strip()
_BETTERCAP_CACHE = {"data": None, "time": 0}  # (data, timestamp) for Bettercap stats

log = logging.getLogger("WebDash")

SYSTEM_LOGS = ["[System Init] Tactical Visual HUD Telemetry initialized successfully."]

def add_system_log(msg: str):
    timestamp = time.strftime("%H:%M:%S")
    SYSTEM_LOGS.append(f"[{timestamp}] {msg}")
    if len(SYSTEM_LOGS) > 15:
        SYSTEM_LOGS.pop(0)

# HTML Template with Glassmorphic Pink & Blue Cyberpunk HUD Aesthetic
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚡ {bot_name} V3 // Live Swarm Cyber HUD</title>
    <link rel="stylesheet" href="/static/fonts/fonts.css">
    <link rel="stylesheet" href="/static/dashboard.css">
</head>
<body>

    <!-- Cohesive Upper HUD Module Frame -->
    <div class="upper-hud-module">
        
        <!-- Panel A: Top Left Header & Node Identifier -->
        <header class="hud-header">
            <div class="hud-logo">
                <div class="status-dot"></div>
                <span>NODE IDENTITY: GhostScout (CLAW-5F05BCD)</span>
            </div>
            <button class="header-menu-btn" onclick="toggleConfigPanel(true)" title="System Config Editor">⋮</button>
        </header>

        <!-- Mock State Control Board -->
        <div class="mock-control-panel">
            <span class="mock-title">MOCK STATE CONTROL:</span>
            <div class="mock-btn-group">
                <button class="mock-btn" id="mock-btn-idle" onclick="setMockState('idle')">IDLE</button>
                <button class="mock-btn" id="mock-btn-connecting" onclick="setMockState('connecting')">CONNECTING</button>
                <button class="mock-btn" id="mock-btn-thinking" onclick="setMockState('thinking')">THINKING</button>
                <button class="mock-btn" id="mock-btn-tool" onclick="setMockState('tool loop')">TOOL LOOP</button>
                <button class="mock-btn" id="mock-btn-success" onclick="setMockState('success')">SUCCESS</button>
                <button class="mock-btn" id="mock-btn-error" onclick="setMockState('error')">ERROR</button>
                <button class="mock-btn" id="mock-btn-sleeping" onclick="setMockState('sleeping')">SLEEPING</button>
                <button class="mock-btn" id="mock-btn-resume" onclick="exitMockMode()" style="border-color: var(--magenta); color: var(--magenta);">⚡ LIVE FEED</button>
            </div>
        </div>

        <div class="grid-container">
            
            <!-- Left Column: Display Screen, Agent Thought, Active Tools, Synapse Command, E-Ink thumbnail -->
            <div class="screen-column">
                
                <!-- Panel B: Centerpiece Procedural EPD dot matrix screen -->
                <div class="screen-card">
                    <div class="screen-title">
                        <span>Braille Dot Matrix Screen</span>
                        <div class="title-badge-flow">
                            <span class="inline-spinner" id="active-pulse-spinner" style="display:none;">⠙</span>
                        </div>
                    </div>
                    
                    <div class="braille-screen-wrapper" id="braille-frame">
                        <div class="state-badges-row">
                            <span class="state-badge" id="state-badge-val">IDLE</span>
                            <span class="special-state-badge" id="special-badge-val" style="display:none;">quiescent</span>
                        </div>
                        
                        <!-- Physical 5x8 grid of circular glowing led dot elements -->
                        <div class="led-matrix" id="led-matrix-grid"></div>
                        
                        <!-- Distinct bright neon green Kawaii face overlay squarely in center -->
                        <div class="kaomoji-overlay" id="kaomoji-val">(◕ ‿ ◕)</div>
                        
                        <div class="scanlines"></div>
                    </div>
                </div>

                <!-- Panel C: Agent Thought Box: Faint Magenta Border -->
                <div class="thought-box">
                    <div class="thought-header">
                        <span>AGENT THOUGHT:</span>
                        <span class="inline-spinner" id="thought-spinner" style="display:none;">⠙</span>
                    </div>
                    <div class="thought-ticker" id="thought-ticker-val">
                        Passively sniffing ambient cyberspace beacons...
                    </div>
                </div>

                <!-- Panel D: Active Tools Bar: Solid Gold Border -->
                <div class="tools-bar">
                    <div class="tools-header">ACTIVE TOOLS:</div>
                    <div class="tools-list" id="tools-list-val">
                        boot_sequence, load_nvs, idle_listener
                    </div>
                </div>

                <!-- Neural Core Command Gateway -->
                <div class="synapse-box">
                    <div class="synapse-header">
                        <span>NEURAL CORE INTERFACE:</span>
                        <span class="state-badge" id="api-status-badge" style="font-size:0.65rem; padding:2px 6px; background:#4CAF50; color:#000;">READY</span>
                    </div>
                    <div class="synapse-form">
                        <input type="text" id="synapse-prompt-val" class="synapse-input" placeholder="TRANSMIT SYNAPSE COMMAND..." onkeydown="if(event.key==='Enter') transmitSynapseCommand(event)">
                        <button class="btn" onclick="transmitSynapseCommand(event)" style="background:linear-gradient(135deg, var(--magenta) 0%, var(--cyan) 100%); color:#000; font-weight:bold; border:none; padding:0.4rem 1rem; border-radius:6px; font-size:0.75rem; letter-spacing:1px; cursor:pointer;">TRANSMIT</button>
                    </div>
                </div>

                <!-- E-Paper waveshare thumbnail -->
                <div class="epd-thumbnail-card">
                    <div class="screen-title" style="margin-bottom:0.4rem; font-size:0.78rem;">e-Paper Frame (Waveshare Panel)</div>
                    <div class="epd-thumbnail-frame">
                        <img id="epd-image" src="/simulator.png" alt="EPD Panel">
                    </div>
                </div>

            </div>

            <!-- Right Column: System HUD Vitals & Swarm Uplinks -->
            <div class="hud-column">
                
                <div class="hud-row">
                    
                    <!-- System Vitals Panel -->
                    <div class="hud-card">
                        <div class="hud-card-title">System Vitals 📈</div>
                        <div class="metric">
                            <span class="metric-label">CPU Usage:</span>
                            <span class="metric-val" id="cpu-usage">-</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">RAM State:</span>
                            <span class="metric-val" id="ram-usage">-</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">CPU Temp:</span>
                            <span class="metric-val" id="cpu-temp">-</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">System Uptime:</span>
                            <span class="metric-val" id="uptime">-</span>
                        </div>
                    </div>

                    <!-- Radio & Pwnagotchi Vitals Panel -->
                    <div class="hud-card">
                        <div class="hud-card-title">Auditor Radio Telemetry 📡</div>
                        <div class="metric">
                            <span class="metric-label">Bettercap:</span>
                            <span class="metric-val" id="pwn-status">-</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">APs Discovered:</span>
                            <span class="metric-val" id="discovered-aps">-</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">BLE Beacon Devices:</span>
                            <span class="metric-val" id="discovered-ble">-</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">WPA Handshakes:</span>
                            <span class="metric-val" id="captured-handshakes">-</span>
                        </div>
                    </div>

                </div>

                <!-- Swarm Actions & Uplinks Registry -->
                <div class="control-card">
                    <div class="hud-card-title" style="margin-bottom:0.8rem; font-size:0.85rem; color:var(--text-secondary); font-family:'Orbitron', sans-serif;">Swarm Actions & Uplinks 📡</div>
                    <div class="btn-group" style="margin-bottom: 0.8rem;">
                        <button class="btn" onclick="triggerUplink(event, 'telegram_uplink')">💬 Telegram Ping</button>
                        <button class="btn" onclick="triggerUplink(event, 'discord_uplink')">🎮 Discord Sync</button>
                        <button class="btn" onclick="triggerUplink(event, 'github_uplink')">🐙 GitHub Auth</button>
                        <button class="btn" onclick="triggerCyberSearch(event)">🔍 Brave Search</button>
                        <button class="btn" id="nap-btn" onclick="toggleNapMode(event)">🛌 Gesture: Nap</button>
                    </div>
                    <div class="btn-group">
                        <button class="btn" onclick="executeAction(event, 'toggle_mode')">Toggle Lite/Pro</button>
                        <button class="btn" onclick="executeAction(event, 'pulse_display')">Force Redraw</button>
                        <button class="btn" onclick="executeAction(event, 'clear_history')">Wipe History</button>
                    </div>
                </div>

            </div>

        </div>

        <!-- Panel E: Metrics & Telemetry Footer Cards (base of upper frame) -->
        <div class="metrics-row">
            <!-- Tier Level Card -->
            <div class="metric-card">
                <div class="metric-card-header">TIER LEVEL</div>
                <div class="metric-card-value" id="rpg-level">2</div>
                <div class="metric-card-subtext" id="rpg-class" style="color:var(--cyan);">OVERLORD</div>
            </div>
            
            <!-- XP Progress Card -->
            <div class="metric-card">
                <div class="metric-card-header" id="xp-header-text">XP PROGRESS 1945/1000</div>
                <div class="progress-container" style="margin: 0.5rem 0;">
                    <div class="progress-bar" id="xp-progress" style="width: 75%; background: var(--cyan); box-shadow: 0 0 10px var(--cyan-glow);"></div>
                </div>
                <div class="metric-card-subtext">Telemetry Synced</div>
            </div>

            <!-- Energy HP Card -->
            <div class="metric-card">
                <div class="metric-card-header" id="hp-header-text">ENERGY HP 100%</div>
                <div class="progress-container" style="margin: 0.5rem 0;">
                    <div class="progress-bar" id="hp-progress" style="width: 100%; background: var(--magenta); box-shadow: 0 0 10px var(--magenta-glow);"></div>
                </div>
                <div class="metric-card-subtext" id="energy-hp-text">Status: Active</div>
            </div>

            <!-- Trust Rep Card -->
            <div class="metric-card">
                <div class="metric-card-header" id="trust-header-text">TRUST REP 1.000</div>
                <div class="progress-container" style="margin: 0.5rem 0;">
                    <div class="progress-bar" id="trust-progress" style="width: 50%; background: #3F51B5; box-shadow: 0 0 10px rgba(63, 81, 181, 0.4);"></div>
                </div>
                <div class="metric-card-subtext" id="trust-subtext">Rating: Neutral</div>
            </div>
        </div>

    </div>

    <!-- Panel F: Diagnostic Event Output Logger (Terminal Console) -->
    <div class="console-full-width">
        <div class="console-card">
            <div class="console-header-row">
                <div class="console-title">
                    <span class="green-dot-icon"></span>
                    <span>DIAGNOSTIC EVENT OUTPUT LOGGER</span>
                </div>
                <div class="console-controls">
                    <button class="console-btn" onclick="toggleConsoleMinimize()" title="Minimize Console">_</button>
                    <button class="console-btn" onclick="toggleConsoleMaximize()" title="Maximize/Restore Console">⬜</button>
                    <button class="console-btn" onclick="clearConsoleLog()" style="color: var(--red);">CLEAR CONSOLE</button>
                </div>
            </div>
            <div class="console-screen" id="log-feed">
                <div class="console-line sys">[System Init] Handshaking visual HUD telemetry channel...</div>
            </div>
        </div>
    </div>

    <!-- Sliding overlay panel exposing environmental variable settings (.env file parser) -->
    <div class="sliding-panel" id="config-panel">
        <div class="sliding-header">
            <div class="sliding-title">🔧 openclawgotchi_V4 .env Config</div>
            <button class="header-menu-btn" onclick="toggleConfigPanel(false)" style="font-size:2rem; color:var(--cyan);">&times;</button>
        </div>
        <p style="font-family:'Share Tech Mono', monospace; font-size:0.8rem; color:var(--text-secondary);">
            Customize environment parameters below. Changing keys requires restarting the gotchi daemon.
        </p>
        <textarea class="env-editor-textarea" id="env-editor-area" placeholder="Loading environment configs..."></textarea>
        <div style="display:flex; justify-content:flex-end; gap:0.8rem; margin-top: auto;">
            <button class="btn" onclick="toggleConfigPanel(false)" style="border-color:#333;">Cancel</button>
            <button class="btn" onclick="saveSettingsConfig()" style="background:var(--cyan); color:#000; font-weight:bold; border-color:var(--cyan);">Save Config</button>
        </div>
    </div>

    <div id="toast">Command dispatched successfully.</div>

    <script src="/static/dashboard.js"></script>
</body>
</html>
"""

class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """Threading http server to handle async assets like live simulator streams seamlessly."""
    daemon_threads = True

class WebDashboardHandler(http.server.BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        # Override to suppress spammy HTTP console prints
        pass

    def _check_auth(self):
        """Check DASHBOARD_TOKEN if configured. Returns True if auth passes."""
        if not DASHBOARD_TOKEN:
            return True  # No auth configured
        # Check query param: ?token=xxx
        from urllib.parse import parse_qs, urlparse
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        if params.get('token', [None])[0] == DASHBOARD_TOKEN:
            return True
        # Check Authorization header: Bearer xxx
        auth_header = self.headers.get('Authorization', '')
        return bool(auth_header.startswith('Bearer ') and auth_header[7:] == DASHBOARD_TOKEN)

    def _send_unauthorized(self):
        self.send_response(401)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"success": False, "message": "Unauthorized — provide ?token= or Authorization: Bearer"}).encode('utf-8'))

    def do_GET(self):
        # Strip query string for path matching
        parsed_path = self.path.split('?')[0]
        # Auth: skip for static assets and simulator (needed by unauthed HTML page)
        if not parsed_path.startswith("/static/") and not parsed_path.startswith("/simulator.png"):
            if not self._check_auth():
                self._send_unauthorized()
                return
        # 1. Main HTML Serve
        if parsed_path == "/" or parsed_path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            
            # Load gotchi_states.json configuration
            states_json_str = "{}"
            states_path = PROJECT_DIR / "gotchi_states.json"
            if states_path.exists():
                try:
                    with open(states_path, "r", encoding="utf-8") as f:
                        states_json_str = f.read()
                except Exception as e:
                    log.error(f"Error reading gotchi_states.json: {e}")
            
            html = HTML_TEMPLATE.replace('{bot_name}', BOT_NAME).replace('{states_json}', states_json_str)
            self.wfile.write(html.encode('utf-8'))
            
        # 2. Simulator EPD PNG Serve
        elif parsed_path.startswith("/simulator.png"):
            img_path = PROJECT_DIR / "simulator.png"
            if img_path.exists():
                try:
                    self.send_response(200)
                    self.send_header("Content-Type", "image/png")
                    self.end_headers()
                    with open(img_path, "rb") as f:
                        self.wfile.write(f.read())
                except Exception as e:
                    self.send_error(500, f"Error reading simulator image: {e}")
            else:
                # Serve a transparent/blank 250x122 placeholder if E-Ink has not generated any canvas yet
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.end_headers()
                # Empty 1x1 pixel PNG fallback
                blank_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82'
                self.wfile.write(blank_png)

        # 3. Dynamic Stats API
        elif parsed_path == "/api/stats":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            
            stats = self.gather_full_live_stats()
            self.wfile.write(json.dumps(stats, indent=2).encode('utf-8'))

        # 4. GET .env Configuration API
        elif parsed_path == "/api/config":
            env_path = PROJECT_DIR / ".env"
            env_content = ""
            if env_path.exists():
                try:
                    with open(env_path, "r", encoding="utf-8") as f:
                        env_content = f.read()
                except Exception as e:
                    env_content = f"# Error reading .env: {e}"
            else:
                example_path = PROJECT_DIR / ".env.example"
                if example_path.exists():
                    try:
                        with open(example_path, "r", encoding="utf-8") as f:
                            env_content = f.read()
                    except Exception:
                        env_content = "# .env file not found."
                else:
                    env_content = "# .env file not found."
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(env_content.encode('utf-8'))

        # 5. SSE — Server-Sent Events stream (real-time push)
        elif parsed_path == "/api/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            try:
                while not getattr(self.server, '_shutdown_request', False):
                    stats = self.gather_full_live_stats()
                    self.wfile.write(f"data: {json.dumps(stats)}\n\n".encode())
                    self.wfile.flush()
                    time.sleep(1)
            except (BrokenPipeError, ConnectionResetError, OSError):
                pass

        # 6. Static files (CSS, JS, assets)
        elif parsed_path.startswith("/static/"):
            static_dir = Path(__file__).parent / "static"
            file_path = static_dir / self.path[len("/static/"):]
            # Resolve to prevent path traversal
            try:
                file_path = file_path.resolve()
                if not str(file_path).startswith(str(static_dir.resolve())):
                    self.send_error(403, "Forbidden")
                    return
                if file_path.exists() and file_path.is_file():
                    ext = file_path.suffix
                    content_types = {".css": "text/css", ".js": "application/javascript", ".png": "image/png", ".json": "application/json"}
                    self.send_response(200)
                    self.send_header("Content-Type", content_types.get(ext, "application/octet-stream"))
                    self.send_header("Cache-Control", "no-cache")
                    self.end_headers()
                    with open(file_path, "rb") as f:
                        self.wfile.write(f.read())
                    return
            except Exception:
                pass
            self.send_error(404, "Static file not found")

        else:
            self.send_error(404, "HUD Resource Not Found")

    def do_POST(self):
        # Strip query string for path matching
        post_path = self.path.split('?')[0]
        if not self._check_auth():
            self._send_unauthorized()
            return
        if post_path == "/api/action":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = parse_qs(post_data)
            action = params.get('action', [None])[0]
            
            message = "Dispatched action: unknown"
            success = False
            
            # Action Handlers
            if action == "toggle_mode":
                try:
                    from core.router import get_router
                    router = get_router()
                    new_lite_state = router.toggle_lite_mode()
                    # Persist state
                    from core.commands import set_env_var
                    set_env_var("LLM_FORCE_LITE", "1" if new_lite_state else "0")
                    message = f"LLM Mode set to: {'Lite Mode' if new_lite_state else 'Pro Mode'}"
                    add_system_log(f"[System] LLM reasoning mode updated to {'Lite' if new_lite_state else 'Pro'} Mode.")
                    success = True
                except Exception as e:
                    message = f"Error toggling LLM mode: {e}"
            
            elif action == "pulse_display":
                try:
                    from hardware.display import update_display
                    update_display(full_refresh=True)
                    message = "EPD refresh event successfully scheduled!"
                    add_system_log("[System] Scheduled WaveShare E-Paper hardware panel redraw sweep.")
                    success = True
                except Exception as e:
                    message = f"Failed to refresh EPD display: {e}"
                    
            elif action == "clear_history":
                try:
                    from config import get_admin_id
                    from core.commands import clear_bot_history
                    admin_id = get_admin_id()
                    clear_bot_history(admin_id or 0)
                    message = "Active dialog context cleared successfully."
                    add_system_log("[System] Active dialogue memory flushed successfully.")
                    success = True
                except Exception as e:
                    message = f"Error clearing context history: {e}"

            elif action == "telegram_uplink":
                try:
                    import requests

                    from config import BOT_TOKEN
                    if BOT_TOKEN:
                        r = requests.get(
                            f"https://api.telegram.org/bot{BOT_TOKEN}/getMe",
                            timeout=5
                        )
                        if r.status_code == 200:
                            bot_info = r.json().get("result", {})
                            bot_name = bot_info.get("first_name", "Unknown")
                            message = f"Telegram API verified: @{bot_name} token valid."
                            from game_engine.vitals import add_xp as engine_add_xp
                            engine_add_xp(40, "telegram_uplink")
                            add_system_log(f"[Uplink] Telegram API verified: @{bot_name} (+40 XP)")
                            success = True
                        else:
                            message = f"Telegram API error: HTTP {r.status_code}"
                    else:
                        message = "TELEGRAM_BOT_TOKEN not configured — set in .env"
                except Exception as e:
                    message = f"Telegram ping failed: {e}"

            elif action == "discord_uplink":
                try:
                    import requests
                    if DISCORD_BOT_TOKEN:
                        r = requests.get(
                            "https://discord.com/api/v10/users/@me",
                            headers={"Authorization": f"Bot {DISCORD_BOT_TOKEN}"},
                            timeout=5
                        )
                        if r.status_code == 200:
                            bot_info = r.json()
                            bot_name = bot_info.get("username", "Unknown")
                            message = f"Discord API verified: @{bot_name} token valid."
                            from game_engine.vitals import add_xp as engine_add_xp
                            engine_add_xp(40, "discord_uplink")
                            add_system_log(f"[Uplink] Discord API verified: @{bot_name} (+40 XP)")
                            success = True
                        else:
                            message = f"Discord API error: HTTP {r.status_code}"
                    else:
                        message = "DISCORD_BOT_TOKEN not configured — set in .env"
                except Exception as e:
                    message = f"Discord ping failed: {e}"

            elif action == "github_uplink":
                try:
                    import requests
                    if AGENT_GITHUB_PAT:
                        r = requests.get(
                            "https://api.github.com/user",
                            headers={"Authorization": f"Bearer {AGENT_GITHUB_PAT}"},
                            timeout=5
                        )
                        if r.status_code == 200:
                            user_info = r.json()
                            gh_login = user_info.get("login", "Unknown")
                            gh_repos = user_info.get("public_repos", 0)
                            message = f"GitHub API verified: @{gh_login} ({gh_repos} repos)."
                            from game_engine.vitals import add_xp as engine_add_xp
                            engine_add_xp(40, "github_uplink")
                            add_system_log(f"[Uplink] GitHub API verified: @{gh_login} ({gh_repos} repos) (+40 XP)")
                            success = True
                        else:
                            message = f"GitHub API error: HTTP {r.status_code}"
                    else:
                        message = "AGENT_GITHUB_PAT not configured — set in .env"
                except Exception as e:
                    message = f"GitHub sync failed: {e}"

            elif action == "brave_search":
                try:
                    query = params.get('query', [None])[0] or "cybernetics"
                    import requests
                    brave_key = os.environ.get("BRAVE_SEARCH_API_KEY", "")
                    if brave_key:
                        r = requests.get(
                            "https://api.search.brave.com/res/v1/web/search",
                            params={"q": query, "count": 5},
                            headers={"Accept": "application/json", "Accept-Encoding": "gzip", "X-Subscription-Token": brave_key},
                            timeout=5
                        )
                        if r.status_code == 200:
                            results = r.json().get("web", {}).get("results", [])
                            result_summary = "; ".join(f"{r['title']}: {r.get('url','')}" for r in results[:3])
                            message = f"Brave Search: {len(results)} results for '{query}'. Top: {result_summary}"
                            from game_engine.vitals import add_xp as engine_add_xp
                            engine_add_xp(40, "brave_search")
                            add_system_log(f"[Cyberspace] Brave search '{query}': {len(results)} results (+40 XP)")
                            success = True
                        else:
                            message = f"Brave API error: HTTP {r.status_code}"
                    else:
                        message = "BRAVE_SEARCH_API_KEY not configured — set in .env"
                except Exception as e:
                    message = f"Brave search failed: {e}"

            elif action == "toggle_nap":
                try:
                    is_napping = params.get('is_napping', ['false'])[0] == 'true'
                    from hardware import display
                    if is_napping:
                        display._current_mood = "sleeping"
                        display._current_text = "Gesture: Sleep Mode active"
                        add_system_log("[System] Core sleeping gesture activated. HP regeneration loop enabled.")
                        message = "Gotchi entered sleep mode. HP regenerating."
                    else:
                        display._current_mood = "happy"
                        display._current_text = "System active"
                        add_system_log("[System] Core sleeping gesture deactivated. Normal loops resumed.")
                        message = "Gotchi woke up."
                    success = True
                except Exception as e:
                    message = f"Nap toggle failed: {e}"
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": success, "message": message}).encode('utf-8'))

        elif post_path == "/api/chat":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = parse_qs(post_data)
            prompt = params.get('prompt', [None])[0]
            
            if not prompt:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Prompt is required")
                return
                
            success = False
            message = ""
            try:
                from core.router import get_router
                router = get_router()
                
                from config import get_admin_id
                from db.memory import get_history
                admin_id = get_admin_id() or 0
                history = get_history(admin_id, limit=10)
                
                # Execute async call safely — asyncio.run() handles loop lifecycle
                import asyncio

                from config import SYSTEM_PROMPT
                add_system_log(f"[Synapse] Direct synapse transmit dispatched to AI Core: '{prompt[:30]}...'")
                response, _connector = asyncio.run(
                    router.call(prompt, history, SYSTEM_PROMPT)
                )
                
                from audit_logging.command_logger import log_command
                log_command(
                    action="web_synapse",
                    user_id=admin_id,
                    chat_id=0,
                    source="web",
                    extra={"prompt": prompt, "response": response}
                )
                
                # Execute SAY: / FACE: commands locally on EPD
                from hardware.display import parse_and_execute_commands
                parse_and_execute_commands(response)
                
                # Award dynamic reward XP on query success!
                from game_engine.vitals import add_xp as engine_add_xp
                engine_add_xp(25, "web_query")
                
                success = True
                message = response
                add_system_log("[Synapse] AI Core synapse response synchronized successfully (+25 XP)")
            except Exception as e:
                message = f"Error processing query: {e}"
                log.error(message, exc_info=True)
                
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": success, "message": message}).encode('utf-8'))

        elif post_path == "/api/config":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            env_path = PROJECT_DIR / ".env"
            success = False
            message = ""
            try:
                with open(env_path, "w", encoding="utf-8") as f:
                    f.write(post_data)
                # Reload variables dynamically in config
                from dotenv import load_dotenv
                load_dotenv(env_path, override=True)
                success = True
                message = "Environment configuration (.env) successfully updated and reloaded."
                add_system_log("[System] Local environment configuration (.env) successfully updated.")
            except Exception as e:
                message = f"Failed to save .env: {e}"
                
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": success, "message": message}).encode('utf-8'))

        else:
            self.send_error(404, "HUD Endpoint Not Found")

    def gather_full_live_stats(self) -> dict:
        """Gathers full live statistics across all hardware and RPG modules natively."""
        # 1. System Vitals
        from hardware.system import get_stats
        try:
            sys_stats = get_stats()
            sys_dict = sys_stats.to_dict()
        except Exception:
            sys_dict = {"uptime": "?", "temp": "?", "memory": "?", "cpu_load": "?"}
            
        # 2. Gotchi display and RPG stats
        from game_engine.state import state_manager
        from hardware import display
        
        try:
            state = state_manager.load_state()
            g = {
                "level": state.level,
                "title": state.title,
                "xp": state.xp,
                "hp": state.hp,
                "rp": state.rp,
                "messages": state.missions_completed
            }
        except Exception:
            g = {"level": "?", "title": "?", "xp": "?", "hp": 100.0, "rp": 0.0, "messages": "?"}
            
        gotchi_dict = {
            "level": g.get("level", "?"),
            "title": g.get("title", "?"),
            "xp": g.get("xp", "?"),
            "hp": g.get("hp", "?"),
            "rp": g.get("rp", "?"),
            "messages": g.get("messages", "?"),
            "mood": getattr(display, "_current_mood", "happy"),
            "text": getattr(display, "_current_text", ""),
            "kaomoji": display.get_current_face_ascii(),
        }
        # Add XP progression breakdown
        try:
            from db.stats import get_level_progress
            prog = get_level_progress()
            gotchi_dict["xp_in_level"] = prog.get("xp_in_level", 0)
            gotchi_dict["xp_needed_this_level"] = prog.get("xp_needed_this_level", 100)
            gotchi_dict["xp_to_next"] = prog.get("xp_to_next", 0)
        except Exception:
            gotchi_dict["xp_in_level"] = 0
            gotchi_dict["xp_needed_this_level"] = 100
            gotchi_dict["xp_to_next"] = 100

        # 3. Auditor/Pwnagotchi Telemetry (cached 5s TTL)
        pwn_dict = {"status": "OFFLINE", "aps": 0, "ble": 0, "handshakes": 0}
        try:
            import time as _time
            now = _time.time()
            # Use cached data if fresh (5s TTL)
            if _BETTERCAP_CACHE["data"] and (now - _BETTERCAP_CACHE["time"]) < 5:
                pwn_dict = _BETTERCAP_CACHE["data"]
            else:
                from utils.ipc import state_manager
                state = state_manager.get_state()
                
                import requests
                from requests.auth import HTTPBasicAuth

                from config import BETTERCAP_PASS, BETTERCAP_USER
                
                try:
                    auth = HTTPBasicAuth(BETTERCAP_USER, BETTERCAP_PASS)
                    r = requests.get("http://localhost:8081/api/session", auth=auth, timeout=0.5)
                    if r.status_code == 200:
                        session = r.json()
                        pwn_dict["status"] = "ONLINE"
                        aps = session.get("wifi", {}).get("aps", [])
                        valid_aps = [ap for ap in aps if ap.get('encryption') not in ('', 'OPEN')]
                        pwn_dict["aps"] = len(valid_aps)
                        pwn_dict["ble"] = len(session.get("ble", {}).get("devices", []))
                except Exception:
                    pass
                _BETTERCAP_CACHE["data"] = dict(pwn_dict)
                _BETTERCAP_CACHE["time"] = now
                
            # Read handshakes directory count
            handshake_dir = PROJECT_DIR / "handshakes"
            if handshake_dir.exists():
                pwn_dict["handshakes"] = len(glob.glob(str(handshake_dir / "*.pcap")))
        except Exception:
            pass

        # 4. Check if LLM API keys are loaded
        api_ready = False
        if (os.environ.get("GEMINI_API_KEY") or 
            os.environ.get("GOOGLE_API_KEY") or 
            os.environ.get("OPENROUTER_API_KEY") or 
            os.environ.get("DEEPSEEK_API_KEY") or 
            os.environ.get("ANTHROPIC_API_KEY") or 
            os.environ.get("TELEGRAM_BOT_TOKEN") or 
            os.environ.get("DISCORD_BOT_TOKEN")):
            api_ready = True

        # 5. Activity Logs Feed - Merged SYSTEM_LOGS + Chat Dialogue
        logs_list = list(SYSTEM_LOGS)
        try:
            from db.memory import get_connection, get_history
            active_conv_id = None
            
            # Autodetect the most recently active conversation ID
            conn = get_connection()
            try:
                row = conn.execute("SELECT user_id FROM messages ORDER BY id DESC LIMIT 1").fetchone()
                if row:
                    active_conv_id = row[0]
            except Exception:
                pass
            finally:
                conn.close()
                
            if not active_conv_id:
                from config import get_admin_id
                active_conv_id = get_admin_id()
                
            if active_conv_id:
                history = get_history(active_conv_id, limit=8)
                for entry in history:
                    role = entry.get("role", "system").upper()
                    content = entry.get("content", "").replace("\n", " ")[:80]
                    logs_list.append(f"[CHAT:{role}] {content}")
        except Exception:
            pass

        return {
            "system": sys_dict,
            "gotchi": gotchi_dict,
            "pwn": pwn_dict,
            "logs": logs_list,
            "api_ready": api_ready
        }

def start_web_server(port: int = 8000):
    """Launches the threaded socket localhost server in a background daemon thread."""
    def run():
        # Port fallback to ensure we bind successfully even if port 8000 is occupied
        current_port = port
        server = None
        for i in range(5):
            try:
                server = ThreadingHTTPServer(("0.0.0.0", current_port), WebDashboardHandler)
                break
            except Exception as e:
                log.warning(f"Failed to bind web dashboard to port {current_port}: {e}. Retrying on subsequent port...")
                current_port += 1
                
        if server:
            log.info(f"Localhost web dashboard successfully started at http://localhost:{current_port}")
            server.serve_forever()
        else:
            log.error("Could not bind Web Dashboard server on any port in range.")

    threading.Thread(target=run, daemon=True, name="WebDashboardServer").start()
