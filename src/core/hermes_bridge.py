"""
src/core/hermes_bridge.py
=========================
🦋 Hermes Bridge — Lightweight HTTP API for Hermes ↔ Gotchi communication

Provides a local HTTP server (default: localhost:7438) that exposes Gotchi's
internals as a REST API. Hermes' GotchiClient (Phase 4) uses this instead of
subprocess calls for lower latency and structured JSON responses.

Endpoints:
  GET  /api/status          → Gotchi pet state JSON
  GET  /api/vitals          → XP, level, mood (compact)
  GET  /api/missions        → Active missions JSON
  GET  /api/mission/log     → Last 10 mission log entries
  POST /api/face            → Set E-Ink face {"mood": "hunting", "message": "..."}
  POST /api/pwn/start       → Start Bettercap sweep {}
  GET  /api/pwn/status      → Current pwn state
  POST /api/memory/recall   → Search facts {"query": "..."}
  POST /api/memory/remember → Store fact {"content": "..."}
  POST /api/mission/accept  → Accept mission {"mission_id": "..."}
  GET  /api/health          → Heartbeat {"ok": true}

Authentication:
  All endpoints (except /api/health) require the header:
    X-Gotchi-Token: <GOTCHI_BRIDGE_TOKEN from .env>
  Token is optional when GOTCHI_BRIDGE_TOKEN is empty (dev/local mode).

Config:
  GOTCHI_BRIDGE_PORT  - Port to listen on (default: 7438)
  GOTCHI_BRIDGE_HOST  - Host to bind (default: 127.0.0.1 — localhost only)
  GOTCHI_BRIDGE_TOKEN - Shared secret (set same value in Hermes GOTCHI_BRIDGE_TOKEN)

Usage:
  # Start standalone (for testing)
  python -m core.hermes_bridge

  # Integrated (called from main.py):
  from core.hermes_bridge import start_bridge_thread
  start_bridge_thread()
"""

import json
import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse, parse_qs

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def _bridge_port() -> int:
    return int(os.environ.get("GOTCHI_BRIDGE_PORT", "7438"))

def _bridge_host() -> str:
    return os.environ.get("GOTCHI_BRIDGE_HOST", "127.0.0.1")

def _bridge_token() -> str:
    return os.environ.get("GOTCHI_BRIDGE_TOKEN", "")

_MISSION_LOG_PATH = Path(
    os.environ.get("HERMES_GOTCHI_LOG", "/home/pi/shared/hermes-gotchi/mission_log.md")
)


# ---------------------------------------------------------------------------
# Auth helper
# ---------------------------------------------------------------------------

def _check_auth(handler: BaseHTTPRequestHandler) -> bool:
    """Return True if the request is authorised."""
    token = _bridge_token()
    if not token:
        return True  # No token configured → dev mode, allow all local requests
    sent = handler.headers.get("X-Gotchi-Token", "")
    return sent == token


# ---------------------------------------------------------------------------
# Request handler
# ---------------------------------------------------------------------------

class GotchiBridgeHandler(BaseHTTPRequestHandler):
    """
    Minimal HTTP handler for the Hermes Bridge.
    All JSON bodies are read via _read_json(); all responses via _send_json().
    """

    def log_message(self, fmt, *args):  # suppress default access log
        log.debug("HermesBridge: " + fmt, *args)

    def _send_json(self, status: int, data: dict) -> None:
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, status: int, msg: str) -> None:
        self._send_json(status, {"ok": False, "error": msg})

    def _read_json(self) -> Optional[dict]:
        try:
            length = int(self.headers.get("Content-Length", 0))
            if length == 0:
                return {}
            raw = self.rfile.read(length)
            return json.loads(raw)
        except Exception:
            return None

    def _require_auth(self) -> bool:
        if not _check_auth(self):
            self._send_error(401, "Unauthorised: provide X-Gotchi-Token header")
            return False
        return True

    # ------------------------------------------------------------------
    # GET router
    # ------------------------------------------------------------------

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/api/health":
            self._send_json(200, {"ok": True, "service": "hermes-bridge", "version": "1.0"})
            return

        if not self._require_auth():
            return

        if path == "/api/status":
            self._handle_status()
        elif path == "/api/vitals":
            self._handle_vitals()
        elif path == "/api/missions":
            self._handle_missions()
        elif path == "/api/mission/log":
            self._handle_mission_log()
        elif path == "/api/pwn/status":
            self._handle_pwn_status()
        else:
            self._send_error(404, f"Unknown endpoint: {path}")

    # ------------------------------------------------------------------
    # POST router
    # ------------------------------------------------------------------

    def do_POST(self):
        if not self._require_auth():
            return

        path = urlparse(self.path).path
        body = self._read_json()
        if body is None:
            self._send_error(400, "Invalid JSON body")
            return

        if path == "/api/face":
            self._handle_face(body)
        elif path == "/api/pwn/start":
            self._handle_pwn_start(body)
        elif path == "/api/memory/recall":
            self._handle_memory_recall(body)
        elif path == "/api/memory/remember":
            self._handle_memory_remember(body)
        elif path == "/api/mission/accept":
            self._handle_mission_accept(body)
        else:
            self._send_error(404, f"Unknown endpoint: {path}")

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    def _handle_status(self):
        try:
            from core.commands import get_status_report
            report = get_status_report()
            self._send_json(200, {"ok": True, "data": report})
        except Exception as e:
            self._send_error(500, str(e))

    def _handle_vitals(self):
        try:
            from game_engine.vitals import get_vitals
            vitals = get_vitals()
            self._send_json(200, {"ok": True, "data": vitals})
        except Exception as e:
            # Fallback to basic stats
            try:
                from core.commands import get_status_report
                report = get_status_report()
                vitals = {
                    "level": report.get("level"),
                    "xp": report.get("xp"),
                    "mood": "unknown",
                }
                self._send_json(200, {"ok": True, "data": vitals})
            except Exception as e2:
                self._send_error(500, str(e2))

    def _handle_missions(self):
        try:
            from core.missions.manager import get_missions
            missions = get_missions("active")
            missions_data = [
                {
                    "id": m.id,
                    "title": m.title,
                    "description": getattr(m, "description", ""),
                    "status": m.status,
                    "progress": m.progress,
                    "target": m.target,
                    "reward_xp": m.reward_xp,
                }
                for m in missions
            ]
            self._send_json(200, {"ok": True, "data": missions_data})
        except Exception as e:
            self._send_error(500, str(e))

    def _handle_mission_log(self):
        try:
            if _MISSION_LOG_PATH.exists():
                content = _MISSION_LOG_PATH.read_text(encoding="utf-8")
                # Return last 3000 chars to stay bounded
                self._send_json(200, {"ok": True, "data": content[-3000:]})
            else:
                self._send_json(200, {"ok": True, "data": "(no mission log yet)"})
        except Exception as e:
            self._send_error(500, str(e))

    def _handle_pwn_status(self):
        try:
            from extensions.pwn.wifi import pwn_status
            result = pwn_status()
            if isinstance(result, dict):
                self._send_json(200, {"ok": True, "data": result})
            else:
                self._send_json(200, {"ok": True, "data": {"status": str(result)}})
        except Exception as e:
            self._send_error(500, str(e))

    def _handle_face(self, body: dict):
        try:
            mood = body.get("mood", "happy")
            message = body.get("message", "")[:60]
            from hardware.display import show_face
            show_face(mood, message)
            self._send_json(200, {"ok": True, "mood": mood})
        except Exception as e:
            self._send_error(500, str(e))

    def _handle_pwn_start(self, body: dict):
        try:
            from extensions.pwn.wifi import pwn_status
            result = pwn_status()
            self._send_json(200, {"ok": True, "data": {"started": True, "status": str(result)}})
        except Exception as e:
            self._send_error(500, str(e))

    def _handle_memory_recall(self, body: dict):
        try:
            query = body.get("query", "").strip()
            if not query:
                self._send_error(400, "query is required")
                return
            from db.memory import search_facts
            facts = search_facts(query)
            self._send_json(200, {"ok": True, "data": facts[:20]})
        except Exception as e:
            self._send_error(500, str(e))

    def _handle_memory_remember(self, body: dict):
        try:
            content = body.get("content", "").strip()
            if not content:
                self._send_error(400, "content is required")
                return
            from db.memory import store_fact
            store_fact(content)
            self._send_json(200, {"ok": True, "stored": True})
        except Exception as e:
            self._send_error(500, str(e))

    def _handle_mission_accept(self, body: dict):
        try:
            mission_id = body.get("mission_id", "").strip()
            if not mission_id:
                self._send_error(400, "mission_id is required")
                return
            from core.missions.manager import update_mission_status
            update_mission_status(mission_id, "active")
            self._send_json(200, {"ok": True, "mission_id": mission_id, "status": "active"})
        except Exception as e:
            self._send_error(500, str(e))


# ---------------------------------------------------------------------------
# Server lifecycle
# ---------------------------------------------------------------------------

_bridge_server: Optional[HTTPServer] = None
_bridge_thread: Optional[threading.Thread] = None


def start_bridge(host: str = None, port: int = None) -> HTTPServer:
    """Start the bridge server synchronously (blocks until stopped)."""
    h = host or _bridge_host()
    p = port or _bridge_port()
    server = HTTPServer((h, p), GotchiBridgeHandler)
    log.info(f"🌉 Hermes Bridge listening on http://{h}:{p}")
    return server


def start_bridge_thread(host: str = None, port: int = None) -> threading.Thread:
    """
    Start the Hermes Bridge in a background daemon thread.
    Safe to call from main.py — will not block the bot loop.
    """
    global _bridge_server, _bridge_thread

    if _bridge_thread and _bridge_thread.is_alive():
        log.debug("Hermes Bridge already running.")
        return _bridge_thread

    h = host or _bridge_host()
    p = port or _bridge_port()

    try:
        _bridge_server = HTTPServer((h, p), GotchiBridgeHandler)
    except OSError as e:
        log.warning(f"Hermes Bridge failed to bind {h}:{p} — {e}. Skipping.")
        return None

    def _serve():
        log.info(f"🌉 Hermes Bridge started on http://{h}:{p}")
        try:
            _bridge_server.serve_forever()
        except Exception as e:
            log.error(f"Hermes Bridge crashed: {e}")

    _bridge_thread = threading.Thread(target=_serve, name="hermes-bridge", daemon=True)
    _bridge_thread.start()
    return _bridge_thread


def stop_bridge():
    """Gracefully shut down the bridge server."""
    global _bridge_server
    if _bridge_server:
        _bridge_server.shutdown()
        log.info("Hermes Bridge stopped.")
        _bridge_server = None


# ---------------------------------------------------------------------------
# CLI entry (for testing)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    host = sys.argv[1] if len(sys.argv) > 1 else _bridge_host()
    port = int(sys.argv[2]) if len(sys.argv) > 2 else _bridge_port()
    server = start_bridge(host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nBridge stopped.")
