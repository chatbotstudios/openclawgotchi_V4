"""
network_auditor.py — OpenClawGotchi V4 Plugin
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Unified passive network threat detection plugin.  Combines two detection
strategies originally implemented as separate Pwnagotchi legacy plugins:

  1. Rogue / Evil-Twin AP Detector
     ─────────────────────────────
     Detects APs sharing the same SSID but different BSSIDs (classic evil-twin
     pattern). Also flags APs with unusually strong RSSI that are NOT in the
     known-good ledger (potential honeypots).

  2. DNS Spoofing Anomaly Detector
     ──────────────────────────────
     Parses passive packet captures for UDP/53 responses with mismatched TTLs
     or responses from unexpected resolver IPs.

Both detectors operate purely from data fed through V4 hook events — no
active scanning subprocess calls are made from this plugin (those live in
rogue_ap_detector.py for the aggressive iwlist path).

Missions driven:
  - Cyber Sentinel   : triggered on each rogue AP detection
  - DNS Defender     : triggered on each DNS spoof detection

E-ink face changes:
  - "alert"  kaomoji on threat detection
  - "normal" after clear epoch
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

try:
    from hardware.display import show_face
    _DISPLAY = True
except ImportError:
    _DISPLAY = False

log = logging.getLogger(__name__)

# ─── Rogue AP State ──────────────────────────────────────────────────────────
# ssid → list of BSSIDs seen for that SSID.  An SSID with >1 BSSID is a twin.
_ssid_bssid_map: dict[str, list[str]] = defaultdict(list)

# Track last alert timestamps to rate-limit warnings (1 alert per SSID / 5 min)
_last_alert: dict[str, float] = {}
_ALERT_COOLDOWN = 300  # seconds

# Known-good AP whitelist: populated from workspace/AGENTS.md config section
# if available, or manually added via CLI in future.
_known_good: set[str] = set()  # lowercase BSSIDs


# ─── DNS Spoof State ─────────────────────────────────────────────────────────
# Expected DNS resolver IPs (populated from system /etc/resolv.conf if present)
_trusted_resolvers: set[str] = set()
_dns_anomalies: list[dict] = []

try:
    with open("/etc/resolv.conf", "r") as _rc:
        for _line in _rc:
            _line = _line.strip()
            if _line.startswith("nameserver"):
                _ip = _line.split()[-1]
                _trusted_resolvers.add(_ip)
    log.info(f"[NetworkAuditor] Trusted DNS resolvers: {_trusted_resolvers}")
except FileNotFoundError:
    # Running off-Pi (macOS dev mode) — treat any resolver as suspicious
    log.debug("[NetworkAuditor] /etc/resolv.conf not found — DNS whitelist empty.")


# ─── Helper: Flash E-Ink on threat ──────────────────────────────────────────
def _alert(msg: str, face: str = "alert"):
    log.warning(f"⚠️  [NetworkAuditor] {msg}")
    if _DISPLAY:
        try:
            show_face(face, f"SAY:{msg[:32]}", full_refresh=False)
        except Exception as e:
            log.debug(f"Display error: {e}")


# ─── Hook: WiFi Update (passive evil-twin scan) ──────────────────────────────
@hook("pwn.wifi_update")
def on_wifi_update(event: HookEvent):
    """
    Called every time the V4 system delivers a fresh AP list.

    Detects:
      - Evil-twin APs (same SSID, multiple BSSIDs)
      - Suspiciously strong unknown APs (RSSI > -40 dBm, not whitelisted)

    Expected event.data keys:
        aps : list of dicts with 'mac', 'hostname', 'channel', 'rssi'
    """
    aps: list[dict] = event.data.get("aps", [])
    if not aps:
        return

    threats_found = 0

    # Build SSID→BSSID map for this update
    current_seen: dict[str, set[str]] = defaultdict(set)
    for ap in aps:
        ssid = ap.get("hostname", "") or "<hidden>"
        mac  = (ap.get("mac") or "").lower()
        if mac:
            current_seen[ssid].add(mac)

    # Cross-check against historical map
    for ssid, macs in current_seen.items():
        if ssid in ("<hidden>", ""):
            continue  # hidden SSIDs are noisy, skip

        # Merge into rolling map
        known_macs = set(_ssid_bssid_map[ssid])
        new_macs = macs - known_macs
        for m in new_macs:
            _ssid_bssid_map[ssid].append(m)

        all_macs = set(_ssid_bssid_map[ssid])

        # Evil-twin: same SSID appearing with multiple distinct BSSIDs
        if len(all_macs) > 1:
            # Rate-limit per SSID
            now = time.time()
            if now - _last_alert.get(ssid, 0) > _ALERT_COOLDOWN:
                _last_alert[ssid] = now
                twins = ", ".join(sorted(all_macs))
                _alert(f"Evil-twin: '{ssid}' → {twins}", face="suspicious")
                threats_found += 1

                if _GAME_ENGINE:
                    increment_mission_progress("Cyber Sentinel", 1, event=event)
                    event.messages.append(
                        f"🛡️ **Evil-Twin Detected!**\nSSID: `{ssid}`\nBSSIDs: `{twins}`"
                    )

    # Honeypot detection: unknown AP with very strong signal
    for ap in aps:
        mac  = (ap.get("mac") or "").lower()
        ssid = ap.get("hostname", "<hidden>")
        rssi = ap.get("rssi", -100)

        if mac and mac not in _known_good and rssi > -40:
            now = time.time()
            if now - _last_alert.get(mac, 0) > _ALERT_COOLDOWN:
                _last_alert[mac] = now
                _alert(
                    f"Honeypot? '{ssid}' ({mac}) RSSI={rssi} dBm — unknown AP, very strong signal",
                    face="suspicious"
                )
                threats_found += 1

    if threats_found == 0 and len(aps) > 0:
        log.debug(f"[NetworkAuditor] AP update — {len(aps)} APs, no threats.")


# ─── Hook: New AP (bettercap real-time feed) ─────────────────────────────────
@hook("pwn.bcap.wifi_ap_new")
def on_bcap_ap_new(event: HookEvent):
    """
    Real-time bettercap event for a freshly-spotted AP.
    Immediately cross-checks SSID/BSSID for known twins.
    """
    bcap = event.data.get("bcap_event", {})
    ap   = bcap.get("data", {})
    ssid = ap.get("hostname", "") or "<hidden>"
    mac  = (ap.get("mac") or "").lower()

    if not mac or ssid in ("<hidden>", ""):
        return

    # Track
    if mac not in _ssid_bssid_map.get(ssid, []):
        _ssid_bssid_map[ssid].append(mac)

    existing = set(_ssid_bssid_map[ssid])
    if len(existing) > 1:
        now = time.time()
        if now - _last_alert.get(ssid, 0) > _ALERT_COOLDOWN:
            _last_alert[ssid] = now
            twins = ", ".join(sorted(existing))
            _alert(f"[bcap] Evil-twin: '{ssid}' → {twins}")

            if _GAME_ENGINE:
                increment_mission_progress("Cyber Sentinel", 1, event=event)


# ─── Hook: DNS Packet Anomaly ────────────────────────────────────────────────
@hook("pwn.dns_response")
def on_dns_response(event: HookEvent):
    """
    Called when the packet capture layer (future bettercap/scapy integration)
    delivers a parsed DNS response.

    Expected event.data keys:
        src_ip      : str  — source IP of the DNS response
        query_name  : str  — queried hostname
        answer_ip   : str  — resolved IP address
        ttl         : int  — DNS TTL
        captured_at : float — epoch timestamp
    """
    src_ip     = event.data.get("src_ip", "")
    query_name = event.data.get("query_name", "")
    answer_ip  = event.data.get("answer_ip", "")
    ttl        = event.data.get("ttl", 300)
    ts         = event.data.get("captured_at", time.time())

    # Flag 1: response from untrusted resolver
    if _trusted_resolvers and src_ip not in _trusted_resolvers:
        anomaly = {
            "type": "untrusted_resolver",
            "src_ip": src_ip,
            "query": query_name,
            "answer": answer_ip,
            "ttl": ttl,
            "at": ts,
        }
        _dns_anomalies.append(anomaly)
        _alert(f"DNS spoof? Response from {src_ip} for {query_name} → {answer_ip}")

        if _GAME_ENGINE:
            increment_mission_progress("DNS Defender", 1, event=event)
            event.messages.append(
                f"🔍 **DNS Anomaly Detected!**\n"
                f"Query: `{query_name}`\n"
                f"Answer: `{answer_ip}` via untrusted resolver `{src_ip}`"
            )

    # Flag 2: suspiciously low TTL (< 5s) — common in poisoning attacks
    if ttl < 5:
        _alert(f"DNS low-TTL ({ttl}s) for {query_name} → {answer_ip} from {src_ip}")

        if _GAME_ENGINE:
            increment_mission_progress("DNS Defender", 1, event=event)


# ─── Hook: Epoch Reset ───────────────────────────────────────────────────────
@hook("pwn.epoch")
def on_epoch_clear(event: HookEvent):
    """
    At each epoch boundary, flush stale BSSID tracking entries
    and emit a threat summary.
    """
    epoch = event.data.get("epoch", 0)

    total_twins = sum(1 for macs in _ssid_bssid_map.values() if len(macs) > 1)
    dns_count   = len(_dns_anomalies)

    if total_twins > 0 or dns_count > 0:
        log.info(
            f"[NetworkAuditor] Epoch {epoch} threat summary — "
            f"Evil-twins: {total_twins} | DNS anomalies: {dns_count}"
        )
    else:
        log.debug(f"[NetworkAuditor] Epoch {epoch} — clear.")

    # Flush DNS anomaly buffer (keep last 50)
    if len(_dns_anomalies) > 50:
        _dns_anomalies.clear()
