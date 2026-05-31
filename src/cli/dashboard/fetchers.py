import asyncio
import sys
import os
import requests
from pathlib import Path
from requests.auth import HTTPBasicAuth

# We use asyncio.to_thread to prevent blocking the UI loop with IO operations.

async def fetch_system_stats():
    """Fetch system stats. Native reads to avoid subprocess overhead."""
    def _get():
        from hardware.system import get_stats
        return get_stats()
    return await asyncio.to_thread(_get)

async def fetch_gotchi_stats():
    """Fetch level, XP, etc."""
    def _get():
        try:
            from db.stats import get_stats_summary
            return get_stats_summary()
        except Exception:
            return {"level": "?", "title": "?", "xp": "?", "messages": "?"}
    return await asyncio.to_thread(_get)

async def fetch_pwn_status():
    """Fetch Bettercap/WiFi status via REST API + IPC."""
    def _get():
        try:
            from utils.ipc import state_manager
            state = state_manager.get_state()
            
            from config import BETTERCAP_USER, BETTERCAP_PASS
            auth = HTTPBasicAuth(BETTERCAP_USER, BETTERCAP_PASS)
            
            res = {"state": state, "aps": 0, "ble": 0, "handshakes": 0, "status": "OFFLINE"}
            
            try:
                r = requests.get("http://localhost:8081/api/session", auth=auth, timeout=1.0)
                if r.status_code == 200:
                    session = r.json()
                    res["status"] = "ONLINE"
                    
                    aps = session.get("wifi", {}).get("aps", [])
                    valid_aps = [ap for ap in aps if ap.get('encryption') not in ('', 'OPEN')]
                    res["aps"] = len(valid_aps)
                    res["ble"] = len(session.get("ble", {}).get("devices", []))
            except Exception:
                pass
            
            # Count handshakes
            import glob
            res["handshakes"] = len(glob.glob("/root/handshakes/*.pcap"))
            return res
        except Exception as e:
            return {"state": {}, "aps": 0, "ble": 0, "handshakes": 0, "status": f"ERR: {e}"}
            
    return await asyncio.to_thread(_get)

async def fetch_recent_logs(limit=5):
    """Fetch recent activity logs."""
    def _get():
        logs = []
        try:
            from db.memory import get_history
            from config import get_admin_id
            
            # Attempt to get history from DB
            admin_id = get_admin_id()
            if admin_id:
                history = get_history(admin_id, limit=limit)
                for h in history:
                    role = h.get("role", "?")
                    content = h.get("content", "").replace("\n", " ")[:60]
                    logs.append(f"[{role.upper()}] {content}")
        except Exception as e:
            logs.append(f"[ERR] DB read failed: {e}")
        return logs
    return await asyncio.to_thread(_get)

async def fetch_face():
    """Fetch current mood from face state."""
    def _get():
        try:
            # For this dashboard we simulate the face logic
            # Normally it reads from E-Ink state, we'll just pick a default or use IPC
            from ui.faces import get_all_faces
            import random
            faces = get_all_faces()
            smart = faces.get("smart", ["(✜‿‿✜)"])
            return random.choice(smart) if isinstance(smart, list) else smart
        except Exception:
            return "(✜‿‿✜)"
    return await asyncio.to_thread(_get)
