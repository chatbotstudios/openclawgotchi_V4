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

async def fetch_recent_logs(limit=8):
    """Fetch recent activity logs from gotchi logs."""
    def _get():
        logs = []
        try:
            from audit_logging.command_logger import get_recent_commands
            # Fetch a larger pool to ensure we filter and display rich, effective activities
            cmds = get_recent_commands(limit=max(limit, 20))
            
            if not cmds:
                return ["No recent logs found."]
                
            for c in cmds:
                action = c.get("action", "")
                ts = c.get("ts", "")
                
                # Extract time
                time_str = ""
                if ts:
                    try:
                        time_str = ts.split("T")[1][:5] + " "
                    except: pass
                
                if action == "error":
                    err_type = c.get("error_type", "Error")
                    msg = c.get("message", "")[:40]
                    logs.append(f"{time_str}🔴 [bold red][ERR][/] {err_type}: {msg}")
                elif action.startswith("heartbeat:"):
                    hb_type = action.split(":")[1].upper()
                    res = c.get("result", "")[:40]
                    logs.append(f"{time_str}💓 [bold magenta][HB][/] {hb_type} - {res}")
                elif action == "response":
                    source = c.get("source", "system").upper()
                    preview = (c.get("response_preview") or c.get("text_preview") or "Sent response").replace("\n", " ")[:35]
                    logs.append(f"{time_str}🤖 [bold green][{source}][/] Bot -> {preview}")
                elif action.startswith("tool:"):
                    tool_name = action.split(":")[1]
                    logs.append(f"{time_str}🔧 [bold yellow][TOOL][/] Gotchi -> {tool_name}")
                elif action.startswith("cron:") or action == "cron":
                    logs.append(f"{time_str}⏰ [bold yellow][CRON][/] Triggered {action}")
                elif action == "message":
                    source = c.get("source", "system").upper()
                    uname = c.get("username", "User")
                    preview = c.get("text_preview", "").replace("\n", " ")[:35]
                    logs.append(f"{time_str}👤 [bold cyan][{source}][/] @{uname} -> {preview}")
                else:
                    source = c.get("source", "system").upper()
                    uname = c.get("username", "User")
                    preview = c.get("text_preview", "").replace("\n", " ")[:35]
                    action_str = f" {action}" if action else ""
                    preview_str = f" {preview}" if preview else ""
                    logs.append(f"{time_str}👤 [bold cyan][{source}][/] @{uname} ->{action_str}{preview_str}")
        except Exception as e:
            logs.append(f"[ERR] Log parse failed: {e}")
        
        # Return the last 'limit' formatted logs to match display size perfectly
        return logs[-limit:] if len(logs) > limit else logs
    return await asyncio.to_thread(_get)

async def fetch_missions_status():
    """Fetch active, completed, and pending missions stats from game engine."""
    def _get():
        try:
            from game_engine.missions import get_missions
            all_missions = get_missions()
            
            active = []
            completed_count = 0
            pending_count = 0
            
            for m in all_missions:
                status = m.get("status")
                if status == "active":
                    active.append({
                        "name": m.get("name"),
                        "category": m.get("category"),
                        "progress": m.get("progress", 0),
                        "target": m.get("target", 1),
                        "xp": m.get("xp_reward", 0)
                    })
                elif status == "completed":
                    completed_count += 1
                elif status == "pending":
                    pending_count += 1
                    
            return {
                "active": active[:3],  # Show top 3 active
                "completed_count": completed_count,
                "pending_count": pending_count
            }
        except Exception as e:
            return {"active": [], "completed_count": 0, "pending_count": 0, "error": str(e)}
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
