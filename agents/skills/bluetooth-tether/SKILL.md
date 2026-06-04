# 📶 Skill: Bluetooth Tethering (PANU)

This skill enables the unit to maintain a low-bandwidth, high-reliability internet uplink using a mobile phone's Personal Hotspot via Bluetooth PAN (Personal Area Network).

## 🧠 Trigger Phrases
- "Connect to my phone hotspot"
- "Tether to phone"
- "Enable bluetooth tethering"
- "Bring up bluetooth hotspot"

## 🎯 Tactical Purpose
Bluetooth tethering is the preferred method for remote agent connectivity because:
1.  **Radio Isolation**: It leaves the `wlan0` interface completely free for Monitor Mode / Subconscious auditing.
2.  **Low Profile**: Bluetooth signals are less conspicuous than Wi-Fi AP associations in some environments.
3.  **Battery Efficient**: PAN connections are generally less power-intensive for the host phone than Wi-Fi Hotspots.

## 🛠️ Procedural Knowledge

### 1. Proactive Activation & Watchdog
When the operator triggers any of the phrases above:
1.  **Acknowledge**: Instruct the user: *"Please open your phone's Settings > Personal Hotspot screen to make the hotspot discoverable."*
2.  **Initiate Watchdog**: Start a 3-minute BLE aggressive watchdog burst to repeatedly probe for connectivity:
    ```bash
    gotchi network tether burst --duration 180
    ```
3.  **Establish Bond/Tunnel**: Perform a connection attempt to the paired host MAC using the `tether_up` tool.

### 2. The "Hotspot Screen" Paradox
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

### 4. Configuration & Environment Variables
The following environment configurations in `.env` govern Bluetooth tethering defaults:
- **`BLE_TETHER_NAME`**: The name of the tethering host phone (e.g. `JPhone`).
- **`BLE_ADDRESS`**: The static MAC address of the target mobile device (e.g. `D0:3F:AA:14:C9:29`).
- **`BLE_TETHER_PASSWORD`**: Hotspot/PAN PIN if needed for legacy compatibility.

*Note on Pairing PINs*: During the initial `gotchi tether_pair` flow, a 6-digit Secure Simple Pairing (SSP) code is displayed. The user must tap "Pair" on the phone or confirm on the terminal. Once paired and trusted, no PIN or code entry is required for subsequent connections or watchdog pulses.

### 5. Magnetic Watchdog (Autonomous Recovery)
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
