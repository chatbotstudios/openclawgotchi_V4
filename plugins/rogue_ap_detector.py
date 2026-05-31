"""
rogue_ap_detector.py — OpenClawGotchi V4 Plugin (Phase 1, updated Phase 2)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Active rogue AP scanner using iwlist. Inherits from BasePlugin to remain
compatible with legacy Pwnagotchi callback conventions while running as a
native V4 hook plugin.

Role split (Phase 2):
  - This plugin:  active iwlist scan, per-AP cross-check against known list
  - network_auditor.py: passive evil-twin detection from V4 wifi_update feed

NOTE: iwlist requires a Pi with a wireless interface. On macOS dev environments
the subprocess call gracefully fails and logs a warning.
"""

import time
import subprocess
import re

from pwnagotchi.plugins import BasePlugin

log = None  # assigned in __init__ via PluginLogAdapter


class RogueAPDetector(BasePlugin):
    __author__      = 'Deus Dust / OpenClawGotchi V4'
    __version__     = '1.1.0'
    __license__     = 'MIT'
    __description__ = (
        'Active rogue AP scanner via iwlist. Detects APs present in the '
        'live environment that are NOT in the bettercap-reported known-good '
        'list, flagging potential evil-twins and honeypots.'
    )

    # Minimum interval (seconds) between iwlist scans to avoid hammering the radio
    SCAN_THROTTLE = 60

    def __init__(self):
        super().__init__()  # registers all legacy callbacks as V4 hooks
        self._last_scan: float = 0.0

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def on_loaded(self):
        self.log.info("RogueAPDetector v1.1.0 loaded — active scanner ready.")

    def on_unload(self):
        self.log.info("RogueAPDetector unloaded.")

    # ── Core Callback ────────────────────────────────────────────────────────

    def on_wifi_update(self, agent, access_points):
        """
        Called on every V4 pwn.wifi_update event (via BasePlugin bridge).
        Rate-limited to SCAN_THROTTLE to prevent radio saturation.
        """
        now = time.time()
        if now - self._last_scan < self.SCAN_THROTTLE:
            return
        self._last_scan = now

        scan_raw = self._run_iwlist_scan()
        if not scan_raw:
            return

        rogue_aps = self._cross_check(scan_raw, access_points or [])
        for ap in rogue_aps:
            self.log.warning(
                f"🚨 Rogue AP: SSID={ap['ssid']!r} BSSID={ap['bssid']} ch{ap['channel']}"
            )

    # ── iwlist Scan ──────────────────────────────────────────────────────────

    def _run_iwlist_scan(self) -> str:
        """Execute iwlist scan. Returns raw output string or empty string on failure."""
        try:
            result = subprocess.run(
                ["iwlist", "wlan0", "scan"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            return result.stdout
        except FileNotFoundError:
            self.log.debug("iwlist not found — likely running off-Pi (dev mode).")
        except subprocess.TimeoutExpired:
            self.log.warning("iwlist scan timed out after 15s.")
        except Exception as e:
            self.log.error(f"iwlist scan failed: {e}")
        return ""

    # ── Cross-Check ──────────────────────────────────────────────────────────

    def _cross_check(self, scan_raw: str, known_aps: list) -> list:
        """
        Parse iwlist output and return APs not present in known_aps list.

        Returns list of dicts: [{ssid, bssid, channel}, ...]
        """
        # Build known BSSID set (lowercase) from bettercap known-good list
        known_bssids = {
            ap.get("mac", "").lower()
            for ap in known_aps
            if ap.get("mac")
        }

        # Parse iwlist blocks
        parsed = self._parse_iwlist(scan_raw)
        rogues = [
            ap for ap in parsed
            if ap["bssid"] not in known_bssids
        ]
        return rogues

    @staticmethod
    def _parse_iwlist(raw: str) -> list:
        """
        Parse iwlist scan output into a list of AP dicts.

        Returns: [{ssid, bssid, channel}, ...]
        """
        aps = []
        current: dict = {}

        for line in raw.splitlines():
            line = line.strip()

            # New cell = new AP
            cell_match = re.match(r"Cell \d+ - Address:\s*([0-9A-Fa-f:]{17})", line)
            if cell_match:
                if current.get("bssid"):
                    aps.append(current)
                current = {
                    "bssid":   cell_match.group(1).lower(),
                    "ssid":    "",
                    "channel": 0,
                }
                continue

            if current:
                if line.startswith("ESSID:"):
                    current["ssid"] = line.split("ESSID:", 1)[1].strip().strip('"')
                elif line.startswith("Channel:"):
                    try:
                        current["channel"] = int(line.split("Channel:", 1)[1].strip())
                    except ValueError:
                        pass

        if current.get("bssid"):
            aps.append(current)

        return aps


# ── Plugin Instantiation ─────────────────────────────────────────────────────
# The hook runner discovers this module and executes it at load time.
# Instantiating the plugin here triggers BasePlugin.__init__ which
# auto-registers all on_* callbacks as V4 hooks.
plugin = RogueAPDetector()
