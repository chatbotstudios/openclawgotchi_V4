# 📶 Skill: Bluetooth Tethering (PANU)

This skill enables the unit to maintain a low-bandwidth, high-reliability internet uplink using a mobile phone's Personal Hotspot via Bluetooth PAN (Personal Area Network).

## 🎯 Tactical Purpose
Bluetooth tethering is the preferred method for remote agent connectivity because:
1.  **Radio Isolation**: It leaves the `wlan0` interface completely free for Monitor Mode / Subconscious auditing.
2.  **Low Profile**: Bluetooth signals are less conspicuous than Wi-Fi AP associations in some environments.
3.  **Battery Efficient**: PAN connections are generally less power-intensive for the host phone than Wi-Fi Hotspots.

## 🛠️ Procedural Knowledge

### 1. The "Hotspot Screen" Paradox
**CRITICAL**: iOS and many Android versions only broadcast their tethering availability while the **Settings > Personal Hotspot** screen is actively open. 
*   **Action**: If a connection fails, the agent must prompt the user to "Wake the Hotspot".

### 2. Connection Orchestration
The agent should follow this sequence for a successful link:
1.  **Verify Bond**: Ensure the device is trusted via `gotchi tether pair`.
2.  **Pulse Connect**: Always issue a Bluetooth `connect` command *before* attempting to bring up the NetworkManager profile. This "wakes" the iPhone's listener.
3.  **Activate Tunnel**: Use `gotchi tether up` which leverages the `panu` (Personal Area Network User) protocol.

### 3. Interface Awareness
Successful tethering creates the **`bnep0`** interface.
*   **IP Range**: Usually `172.20.10.x` (iOS) or `192.168.44.x` (Android).
*   **Throughput**: 1–2 Mbps (Standard).

### 3. Magnetic Watchdog (Autonomous Recovery)
The unit features a background pulse that monitors internet connectivity:
*   **Burst Mode**: For the first 5 minutes of disconnection, it pulses every 30 seconds.
*   **Stealth Mode**: After 5 minutes, it relaxes to a 5-minute interval to save iPhone battery.
*   **Reflex**: It automatically executes the "Connect -> NM Up" sequence if no internet is detected.

## 🛡️ Service Integrity & Troubleshooting

### 1. The "Phantom Mask" Fix
If `gotchi doctor` or `bluetoothctl` report that the daemon is offline, the service might be masked.
*   **Reflex**: Run `sudo systemctl unmask bluetooth.service` followed by `enable` and `start`.

### 2. Firmware Awareness
The unit requires `pi-bluetooth` and `bluez-firmware` to correctly initialize the radio on boot. If pairing fails consistently despite a powered controller, verify firmware stack integrity.

### 3. Self-Healing
If the bot loses its primary Wi-Fi connection and a paired tethering host is nearby, it should autonomously attempt a `gotchi tether up` to restore its cognitive link to the cloud.
