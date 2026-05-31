"""
deauth_handler.py — OpenClawGotchi V4 Plugin
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tracks deauthentication and association attacks from the bettercap layer,
maintains per-session statistics, awards XP on handshake captures, and
drives the following AIPET missions:

  - Handshake Hunter  (captures detected via pwn.handshake)
  - Pwn Sniper        (deauths tracked via pwn.deauth)
  - Field Agent       (associations tracked via pwn.association)

All handlers run as lightweight V4 hooks — no bettercap or Pi-specific
imports required. Safe to run on macOS in offline simulation.
"""

import logging
import time
from collections import defaultdict

from hooks.runner import hook, HookEvent

try:
    from game_engine.missions import increment_mission_progress
    from game_engine.vitals import add_xp
    _GAME_ENGINE = True
except ImportError:
    _GAME_ENGINE = False

log = logging.getLogger(__name__)

# ─── Session Statistics ─────────────────────────────────────────────────────
_stats = {
    "deauths":      0,
    "associations": 0,
    "handshakes":   0,
    "channels_hit": set(),   # channels deauths/associations happened on
    "ap_seen":      {},      # mac → {ssid, last_seen, deauths, shakes}
}

_session_start = time.time()


def _track_ap(mac: str, ssid: str, field: str):
    """Maintain per-AP rolling counters inside the session dict."""
    entry = _stats["ap_seen"].setdefault(mac.lower(), {
        "ssid": ssid,
        "first_seen": time.time(),
        "deauths": 0,
        "associations": 0,
        "shakes": 0,
    })
    entry["ssid"] = ssid  # keep fresh
    entry["last_seen"] = time.time()
    entry[field] = entry.get(field, 0) + 1


# ─── Hook: Deauthentication ──────────────────────────────────────────────────
@hook("pwn.deauth")
def on_deauth(event: HookEvent):
    """
    Fired when bettercap deauthenticates a client.

    Expected event.data keys:
        ap     : dict with 'mac', 'hostname', 'channel'
        client : dict with 'mac', 'vendor'
    """
    ap = event.data.get("ap") or {}
    client = event.data.get("client") or {}

    mac    = ap.get("mac", "??:??:??:??:??:??")
    ssid   = ap.get("hostname", "<hidden>")
    ch     = ap.get("channel", 0)
    c_mac  = client.get("mac", "??")
    vendor = client.get("vendor", "unknown")

    _stats["deauths"] += 1
    _stats["channels_hit"].add(ch)
    _track_ap(mac, ssid, "deauths")

    log.info(
        f"💥 Deauth #{_stats['deauths']} | AP: {ssid} ({mac}) ch{ch} "
        f"→ Client: {c_mac} [{vendor}]"
    )

    if _GAME_ENGINE:
        increment_mission_progress("Pwn Sniper", 1, event=event)


# ─── Hook: Association ───────────────────────────────────────────────────────
@hook("pwn.association")
def on_association(event: HookEvent):
    """
    Fired when bettercap sends an association frame.

    Expected event.data keys:
        ap : dict with 'mac', 'hostname', 'channel'
    """
    ap   = event.data.get("ap") or {}
    mac  = ap.get("mac", "??:??:??:??:??:??")
    ssid = ap.get("hostname", "<hidden>")
    ch   = ap.get("channel", 0)

    _stats["associations"] += 1
    _stats["channels_hit"].add(ch)
    _track_ap(mac, ssid, "associations")

    log.debug(f"🤝 Association #{_stats['associations']} | AP: {ssid} ({mac}) ch{ch}")

    if _GAME_ENGINE:
        increment_mission_progress("Field Agent", 1, event=event)


# ─── Hook: Handshake ─────────────────────────────────────────────────────────
@hook("pwn.handshake")
def on_handshake(event: HookEvent):
    """
    Fired when a WPA handshake is captured.

    Expected event.data keys:
        filename : path to the .pcap file
        ap       : dict with 'mac', 'hostname'
        client   : dict with 'mac' (optional)
    """
    filename = event.data.get("filename", "<unknown>")
    ap       = event.data.get("ap") or {}
    client   = event.data.get("client") or {}

    mac    = ap.get("mac", "??:??:??:??:??:??")
    ssid   = ap.get("hostname", "<hidden>")
    c_mac  = client.get("mac", "<unknown>") if client else "<unknown>"

    _stats["handshakes"] += 1
    _track_ap(mac, ssid, "shakes")

    log.info(
        f"🔑 Handshake #{_stats['handshakes']} captured! "
        f"SSID: {ssid} ({mac}) ← Client: {c_mac} | File: {filename}"
    )

    if _GAME_ENGINE:
        # 5 XP per handshake (matches aipet_hooks baseline)
        add_xp(5, source="deauth_handler:handshake")
        increment_mission_progress("Handshake Hunter", 1, event=event)


# ─── Hook: Epoch Cleanup ─────────────────────────────────────────────────────
@hook("pwn.epoch")
def on_epoch(event: HookEvent):
    """
    Fires at the end of each bettercap scan epoch.
    Prunes stale APs from the session tracker (not seen in last 2 epochs).
    """
    epoch      = event.data.get("epoch", 0)
    epoch_data = event.data.get("epoch_data", {})
    duration   = epoch_data.get("duration_secs", 120)

    cutoff = time.time() - (duration * 2)
    stale = [m for m, v in _stats["ap_seen"].items() if v.get("last_seen", 0) < cutoff]
    for mac in stale:
        del _stats["ap_seen"][mac]

    if stale:
        log.debug(f"[Epoch {epoch}] Pruned {len(stale)} stale APs from tracker.")

    # Emit a readable session summary every 10 epochs
    if epoch and epoch % 10 == 0:
        uptime = int(time.time() - _session_start)
        log.info(
            f"📊 Epoch {epoch} summary | "
            f"Deauths: {_stats['deauths']} | "
            f"Assocs: {_stats['associations']} | "
            f"Shakes: {_stats['handshakes']} | "
            f"APs tracked: {len(_stats['ap_seen'])} | "
            f"Channels: {sorted(_stats['channels_hit'])} | "
            f"Uptime: {uptime}s"
        )


# ─── Hook: New AP via bettercap real-time feed ───────────────────────────────
@hook("pwn.bcap.wifi_ap_new")
def on_bcap_ap_new(event: HookEvent):
    """
    Fires when bettercap pushes a new AP discovery event.
    Lightweight logging only — heavy analysis belongs to rogue_ap_detector.
    """
    bcap = event.data.get("bcap_event", {})
    ap   = bcap.get("data", {})
    ssid = ap.get("hostname", "<hidden>")
    mac  = ap.get("mac", "??")
    ch   = ap.get("channel", 0)

    log.debug(f"📡 New AP spotted: {ssid} ({mac}) ch{ch}")


# ─── Hook: Client deauth via bettercap real-time feed ───────────────────────
@hook("pwn.bcap.wifi_client_new")
def on_bcap_client_new(event: HookEvent):
    """
    Fires when bettercap spots a new client joining an AP.
    Provides data for instattack-style insta-deauth decisions.
    """
    bcap   = event.data.get("bcap_event", {})
    data   = bcap.get("data", {})
    ap_info = data.get("AP", {})
    cl_info = data.get("Client", {})

    ssid   = ap_info.get("hostname", "<hidden>")
    ap_mac = ap_info.get("mac", "??")
    cl_mac = cl_info.get("mac", "??")

    log.debug(f"👤 New client {cl_mac} on {ssid} ({ap_mac})")
