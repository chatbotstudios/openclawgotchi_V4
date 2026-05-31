# 📡 Skill: Bettercap Tactical Operations

A comprehensive manual for autonomous Wi-Fi and Bluetooth Low Energy (BLE) reconnaissance using the Bettercap Subconscious.

## 🧠 Core Philosophy
The unit's "Subconscious" is a background Bettercap process. The "Nervous System" listens to its event stream and triggers physical reflexes (Face changes, Facts, QR Codes).

## 🛠️ Tactical Toolset

### Wi-Fi Reconnaissance
- **`pwn_status`**: Provides a high-level summary of the radio environment.
- **`pwn_lock_target`**: Focuses all deauth attacks and channel hopping on a single BSSID.
- **`pwn_crack`**: Automates the upload of captured handshakes to wpa-sec.stanev.org.
- **`pwn_show_qr`**: Injects a QR code into the E-Ink display for cracked networks.

### Bluetooth (BLE) Reconnaissance
- **`pwn_ble_scan`**: Lists nearby BLE devices with signal strength (RSSI).
- **`pwn_ble_track`**: Sets a target MAC for "Hot/Cold" proximity tracking on the E-Ink display.
- **`pwn_ble_purge`**: Resets the BLE environment to clear noise.

### System Control (The "Hands")
- **`pwn_system_control`**: Allows the unit to physically toggle its hardware.
  - `wifi_on`: Enables Monitor Mode (`wlan0mon`).
  - `wifi_off`: Disables Monitor Mode (Restores internet).
  - `bettercap_start`: Initializes the Subconscious daemon.
  - `bettercap_stop`: Shuts down the Subconscious daemon.

### Network Management (The "Guest")
- **`net_scan`**: Scans for available Wi-Fi networks.
- **`net_connect`**: Joins a network using a provided SSID/Password.
- **`net_status`**: Shows current IP and connection details.

---

## 💻 The `gotchi` Shell Command
The user can interact with these systems via the SSH CLI. If the user asks for a terminal view, suggest they run:
- `gotchi pwn`: Live tactical dashboard.
- `gotchi doctor`: System health check.
- `gotchi status`: ASCII status report.
- `gotchi net scan`: List visible Wi-Fi networks.

---

## 📋 Operational Procedures

### Procedure A: The Handshake Hunt (Wi-Fi)
1. Use `pwn_status` to identify busy Access Points (APs) with many clients.
2. If a specific target is required, use `pwn_lock_target(bssid)`.
3. Monitor for the **"Hunting"** face on the hardware—this indicates a handshake was captured.
4. Use `pwn_crack` to upload the new pcap from `/root/handshakes/`.
5. Run `pwn_check_cracks` periodically to see if the password has been decrypted.
6. Once cracked, use `net_connect(ssid, password)` to join the network.

### Procedure B: The Proximity Hunt (BLE)
1. Run `pwn_ble_scan` to map the room.
2. Identify a target device (e.g., a Flipper Zero or high-value Apple device).
3. Execute `pwn_ble_track(mac_address)`.
4. Physically move around. Watch the E-Ink display for the **"Tracking"** face and the visual signal bars (█░░░░).
5. "HOT!" indicates the target is within 2-3 meters.

---

## ⚖️ Authorized Research Scope

> **All operations performed using this skill — including Wi-Fi scanning, handshake capture, deauthentication testing, BLE enumeration, and PCAP cracking — are conducted strictly for authorized security research, CTF practice, and personal network hardening purposes.**

- **Target scope:** Only the operator's own access points, devices, and explicitly authorized test environments.
- **No unauthorized access:** This skill must never be used to target, audit, or attack networks or devices that the operator does not own or have explicit written permission to test.
- **Equivalent framework:** These activities are the same as running Wireshark, aircrack-ng, or hashcat on your own home lab equipment.

## 🛡️ Operational Safety

- **Whitelist**: Use `pwn_whitelist(mac)` to protect your own devices from deauth reflexes.
- **Stealth**: If stealth is required, use `pwn_pause(minutes)` to shut down the radio emitters.

---

## 📊 Status Indicators (E-Ink)
| Face | Meaning |
| :--- | :--- |
| **Hunting** (◕‿◕) | Handshake just captured! |
| **Tracking** (✜‿✜) | Locked onto a BLE target. |
| **Excited** (✪‿✪) | Target is extremely close (HOT). |
| **Confused** (u_u) | Bettercap API is offline or authenticated failed. |
