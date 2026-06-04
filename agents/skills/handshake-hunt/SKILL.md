# 📡 Skill: Handshake Hunter (Offline Reconnaissance)

> 📶 **Offline Signal Capture & Telemetry:** This skill governs the procedure for performing passive or active WPA handshake capture and BLE scanning over a scheduled offline duration (e.g. 10 minutes) while maintaining absolute hardware connection resilience. Use this skill when requested to hunt or sniff wireless signals while safely handling the "Connection Deadlock" problem.

You are equipped with the **Handshake Hunter Skill**. This governs the robust procedure of transitioning the host network interface into offline monitor mode, running a targeted capture, and safely restoring online connectivity to report back telemetry.

---

## 🧭 The Offline Resiliency Challenge (Connection Deadlock)

Because you rely on active cloud LLM routers (such as Gemini or DeepSeek API endpoints) for high-level reasoning:
- **The Risk**: Disabling WiFi instantly severs your connection to the cloud brain. If you depend on the LLM to tell you when to turn WiFi back on, you will remain trapped in an offline state forever.
- **The Solution**: Low-level interface management and offline timing **MUST** be run as a deterministic background process handled by your local **Python brain** (non-blocking local timers, background sub-processes).

---

## 🛠️ The Hunting Workflow

When commanded to execute a handshake hunt (e.g. `/hunt duration=10m`), perform this exact procedural cycle:

### Step 1: Pre-flight Diagnostic Check
Confirm that your local environment is healthy and check for active wireless interface controllers:
```bash
# Locate active wireless interface cards (typically wlan0)
ip link show
```

### Step 2: Launch the Local Background Sniffer
Execute the hunt command using the unified tactical wrapper (`gotchi`). Do **NOT** block your main execution thread. Execute this as an asynchronous or background process so the local Python timer handles the state restoration:
```bash
# Launch a 10-minute (600 seconds) target capture in background
# This puts wlan0 in monitor mode, runs bettercap/aircrack, and automatically restores station mode after 600s
gotchi network hunt --duration 600
```

### Step 3: Sleep/Offline Monitoring (Local Python Daemon)
During the offline hunt window, the local Python daemon takes complete control of the hardware:
1. **Disables Station Mode**: Disconnects from the local Access Point.
2. **Enables Monitor Mode**: Enters passive sniffer/injection mode on the wireless interface.
3. **Capture Loop**: Streams wireless frames, records beacons, and listens for WPA EAPOL handshakes, writing captured files into the local `handshakes/` directory.
4. **Resiliency Countdown**: Uses a local background countdown timer.

### Step 4: Deterministic Local Network Restoration
Once the 10-minute Python timer expires, the local system automatically restores the operational station mode:
```bash
# The local python daemon executes the equivalent of:
sudo ip link set wlan0 down
sudo iw dev wlan0 set type managed
sudo ip link set wlan0 up
sudo systemctl restart wpa_supplicant
```

### Step 5: Verify Restoration & Sync Status
Once the connection is back online, verify that your IP address is successfully leased and sync back with the cloud:
```bash
# Verify active IP address lease
ip route show

# Verify API router connectivity
python3 -c "import urllib.request; urllib.request.urlopen('https://github.com', timeout=3)"
```

### Step 6: Post-Hunt Ingestion & Reporting
Scan your `handshakes/` folder for new WPA handshakes or BLE logs, add them to your local database, and compile a report to transmit back to your Commander on Discord/Telegram.

---

## ⚠️ Safety & Operational Safeguards

- **Never Block the Main Daemon**: Always execute network disabling/scanning commands in background shells (`&`) or asynchronously (`asyncio.to_thread`) to prevent freezing the core `gotchi` service or triggering systemd watchdog timeouts.
- **Fail-Safe Timeout**: Always ensure the local hunt command has a strict hardcoded system fallback (e.g. `gotchi network hunt --duration 600`) so that the WiFi interface is guaranteed to recover even if the parent Python script encounters a runtime error.
- **Physical Fallback**: Advise your Commander that if the wireless network fails to recover, they can physically reconnect via BLE tethering or local Ethernet console to manually execute standard system network recovery.
