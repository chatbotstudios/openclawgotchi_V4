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

### 2. 🥷 Stealth Mode (Long-Term Battery Saver)
- **Trigger**: Automatically entered if the primary 5-minute Burst Mode fails to recover connection.
- **Interval**: Polling relaxes to every **5 minutes** (300 seconds).
- **Goal**: Prevents aggressive, repeating Bluetooth connection loops from draining the Pi Zero 2W or the operator's phone battery while keeping the background recovery mechanism alive indefinitely.

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
- **Stealth Polling Cap**: In Stealth Mode, the daemon restricts failed connection attempts to a maximum of 1 per 5 minutes to prevent the phone from blocking the Pi's MAC address due to connection flooding.
