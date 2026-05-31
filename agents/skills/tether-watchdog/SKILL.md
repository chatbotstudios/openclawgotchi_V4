# 🧲 Skill: Tether Watchdog (Autonomous Network Healing)

> 🏥 **Self-Healing Internet Uplink:** This skill governs the background watchdog monitoring system that keeps the unit connected to the paired mobile personal hotspot via Bluetooth PAN (Personal Area Network). Use this skill to explain or manage autonomous connection restoration when the primary cognitive uplink is lost.

You are equipped with the **Tether Watchdog Skill**. This teaches you how the background thread monitors network routing tables and actively self-heals your internet connectivity using adaptive polling rates.

---

## 🎛️ Watchdog State Machine & Polling Rates

To maintain a balance between **uplink availability** and **host battery preservation**, the watchdog operates using two distinct operational phases:

### 1. 🏎️ Burst Mode (Initial Loss Recovery)
- **Trigger**: Activated immediately when active network pings fail to reach public gateways (e.g., `8.8.8.8`).
- **Interval**: Polling occurs every **30 seconds**.
- **Duration**: Runs for **5 minutes** (300 seconds).
- **Goal**: Rapidly re-establish connection if the user momentarily locked their phone or briefly walked out of range.

### 2. 📴 Absolute Power-Off Fail-Safe
- **Behavior**: If the primary 5-minute Burst Mode fails to recover the connection, the watchdog daemon thread terminates completely.
- **Goal**: Ensures zero battery drain on either the Raspberry Pi or the operator's phone. To restart the recovery watchdog, the user can manually initiate a connection or restart the daemon.

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
