# 📡 PWN_AUDIT: OpenClawGotchi Subconscious Security & Auditing Features

## 1. Executive Summary

This audit evaluates the "Pwnagotchi-inspired" features of the OpenClawGotchi V4 architecture. The system successfully abstracts the heavy lifting of RF monitoring, deauthentication, and Bluetooth Low Energy (BLE) tracking into an autonomous background daemon, while allowing the "Ego" (LLM) to interface with it via atomic IPC calls and WebSocket reflexes. 

Overall, the architecture is highly modular and robust, but contains critical areas where state failures could result in the device being stranded completely off-grid.

---

## 2. Component Analysis

### A. Bettercap Integration & The Nervous System (`hardware/bettercap_listener.py`)
- **Architecture**: Maintains a persistent WebSocket (`ws://localhost:8081/api`) to the Bettercap daemon. It uses an asynchronous event loop to map Bettercap event tags (e.g., `wifi.client.handshake`, `ble.device.new`) directly to LLM "Memory Reflexes" and Hardware E-Ink UI updates. Auth is passed via Base64 `extra_headers` header — credentials never appear in the URI, logs, or process listings.
- **Robustness**: High. Because it binds to `localhost`, the listener remains operational even when the external `wlan0` interface drops offline during a hunt.
- **Resolved (P0/P1)**: Hardcoded `123456` fallback credential replaced with `secrets.token_hex(16)` random generation. WebSocket URI no longer embeds `user:pass@`. If `config.py` fails to load, a randomly generated 32-char hex string is used instead of a known default.
- **Recommendation**: Strictly bind the Bettercap API to `127.0.0.1` (not yet enforced in config).

### B. Autonomous Handshake Capture (`hardware/subconscious_pwn.py`)
- **Architecture**: A threaded Automata loop that mirrors original Pwnagotchi logic. It reads `wifi.aps`, iterates through connected clients, and issues `wifi.deauth` commands.
- **Robustness (Spam Prevention)**: Excellent. The `self.history` dictionary caps interactions to `self.max_interactions = 3` per MAC address, preventing the daemon from infinitely jamming a single device.
- **Target Lock (Full Pwn Mode)**: Uses `state_manager` IPC to cleanly lock the radio to a single BSSID.
- **Resolved (P0/P2)**: `.env` whitelist re-read removed from the hot loop — `self._whitelist` is loaded once at init with a `reload_whitelist()` method for on-demand refresh. Custom `random.choice` channel hopping removed — Bettercap's built-in `wifi.recon on` handles channel scanning. `wifi.clear`/`ble.clear` delayed 3s after `recon on` to preserve initial discoveries.

### C. Offline Hunts & Monitor Mode Orchestration (`core/offline_hunter.py`)
- **Architecture**: Orchestrates the drop into monitor mode. Modifies the UI, kills `wpa_supplicant`, invokes the daemon sleep cycle, and eventually restores managed mode.
- **Critical Risk (Stranding)**: The hunt uses a blocking `time.sleep(duration_seconds)` between the `wifi off` and `wifi on` state changes. If the Python process crashes, is OOM-killed, or encounters an unhandled exception during this sleep, **the Gotchi is permanently stranded off-grid in monitor mode** with no way to restore its uplink.
- **Guardrail Recommendation**: Wrap the entire `run_hunt` sequence in a `try...finally` block. Furthermore, implement an independent Bash or `systemd` hardware watchdog that automatically runs `airmon-ng stop wlan0mon` if the main `gotchi` process dies.

### D. Cloud Cracking Offload (`extensions/pwn/wifi.py`)
- **Architecture**: Exposes `pwn_crack` and `pwn_check_cracks` to the LLM, offloading PCAP hashing to `wpa-sec.stanev.org`.
- **Robustness**: Verifies PCAP file sizes before attempting to trigger reflexes, preventing "empty file" spam.
- **Guardrail Recommendation**: Add local rate-limiting to `pwn_check_cracks`. If the LLM loops or panics, it could spam the `wpa-sec` API and result in a permanent IP ban.

### E. BLE Tracking & Proximity (`extensions/pwn/ble.py`)
- **Architecture**: Parses `ble.devices` and maps RSSI values to physical proximity ("HOT/COLD").
- **Robustness (Self-Healing)**: Very high. The script detects if the BLE arrays return empty and automatically injects a `ble.recon on` command into the Bettercap API to kickstart a stalled adapter. Throttled to once per session (`_ble_recon_sent` flag) to avoid redundant API calls.
- **Resolved (P2)**: `BLE_LOG_DIR` now uses `PROJECT_DIR / "handshakes" / "BLE"` absolute path instead of a fragile relative path.

---

## 3. Summary of Suggested Safety Guardrails

1. **Anti-Stranding Try/Finally**: Update `offline_hunter.py` to guarantee network restoration even if the hunter crashes.
```python
try:
    subprocess.run(["python3", "-m", "core.cli.entry", "network", "wifi", "off"])
    time.sleep(duration_seconds)
finally:
    subprocess.run(["python3", "-m", "core.cli.entry", "network", "wifi", "on"])
```
2. **API Binding**: Ensure Bettercap config (`caplets/`) strictly binds the API to `127.0.0.1`.
3. **Cracking Rate Limit**: Implement a cooldown timer dictionary inside `wifi.py` to prevent the LLM from calling `pwn_crack` multiple times on the same `.pcap` file within a 24-hour window.
4. **Thermal Monitoring Trigger**: The LLM should be explicitly prompted to run a `health_check` after returning from a `Full Pwn Mode` target lock, as continuous focused deauth bursts significantly increase the SoC thermal output on a Pi Zero.
