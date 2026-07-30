# 🧲 Skill: Tether Watchdog (Autonomous Network Healing)

> 🏥 **Self-Healing Internet Uplink:** This skill governs the background watchdog monitoring system that keeps the unit connected to the paired mobile personal hotspot via Bluetooth PAN (Personal Area Network). Use this skill to explain or manage autonomous connection restoration when the primary cognitive uplink is lost.

You are equipped with the **Tether Watchdog Skill**. This teaches you how the background thread monitors network routing tables and actively self-heals your internet connectivity using adaptive polling rates.

---

## 🎛️ Watchdog State Machine & Polling Rates

To maintain a balance between **uplink availability** and **host battery preservation**, the watchdog operates using two distinct operational phases:

### 1. 🏎️ Burst Mode (Initial Loss Recovery)
- **Trigger**: Activated immediately upon boot or when tether drops.
- **Interval**: Polling occurs every **30 seconds**.
- **Duration**: First **5 minutes** (300 seconds) after startup.
- **Goal**: Rapidly re-establish connection while the user's phone might still be nearby.

### 2. 🧘 Steady Mode (Long-Term Monitoring)
- **Trigger**: Transitions automatically after the 5-minute burst expires.
- **Interval**: Polling occurs every **120 seconds** (sparse — saves battery).
- **Duration**: Runs **indefinitely** until the watchdog is explicitly stopped.
- **Goal**: Passive monitoring with minimal power draw. Recognizes that sustained uptime matters.

### Network Health Checks (Zero Subprocess)
The watchdog now uses **filesystem reads** instead of forking subprocesses:
- **`_has_internet()`**: Reads `/proc/net/route` for a default gateway — no `ping` fork, no ICMP latency.
- **`_is_tether_active()`**: Reads `/sys/class/net/bnep0/operstate` — no `nmcli` or `ip` subprocess.
- **Keepalive ping**: Throttled to max once per 60 seconds using `_last_keepalive` timestamp.

### Mock Hardware Support
When `MOCK_HARDWARE=1` is set, `start()` returns `True` immediately without touching any subprocess or hardware path. The watchdog is fully testable on non-Pi systems.

---

## 🛠️ Operational Commands & Diagnostics

### 1. Check Watchdog System Status
Verify if the watchdog daemon thread is active and running in the background:
```bash
# Check daemon log indicators
gotchi logs | grep TetherWatchdog
```

### 2. Manually Force a Connection Pulse
If the connection is lost and you need to bypass standard polling delays, force a manual wakeup:
```bash
# Triggers an immediate connect pulse to the saved nmcli bdaddr profile
gotchi tether status
```

---

## 🛡️ Autonomous Recovery Logic (Python Core)

The local Python daemon executes this recovery reflex when an offline state is detected:

```python
# 1. Query the paired MAC address from NetworkManager
mac = get_nmcli_profile_bdaddr("iPhoneHotspot")

# 2. Issue a Bluetooth connect pulse to wake the device's hotspot screen listener
execute("sudo bluetoothctl connect " + mac)
time.sleep(2)

# 3. Bring up the NetworkManager connection profile
execute("sudo nmcli con up iPhoneHotspot")
```

---

## ⚠️ Safeguards & Conflict Resolution

- **Wi-Fi Precedence**: The watchdog will only attempt a Bluetooth tether activation if both primary Wi-Fi and Bluetooth connections are down. If a valid, trusted Wi-Fi Access Point is connected, the watchdog suspends itself.
- **Connection Rate Limiting**: The 30-second polling interval in Burst Mode is strictly rate-limited to a maximum of 5 minutes total to prevent connection flooding or MAC address blocking by the host operating system.
