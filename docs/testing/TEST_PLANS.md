# OpenClawGotchi: Comprehensive Test Plan
This document outlines the systematic procedures required to validate the newly implemented "Split-Brain" Pwnagotchi architecture on live Raspberry Pi hardware.

## Phase 1: Environment & Dependency Validation
**Objective:** Ensure all prerequisites and daemons boot correctly.
1. [ ] **System Dependencies:** Bettercap is a compiled Go binary, not a Python package. Install it and `airmon-ng` via `apt`:
    - `sudo apt update`
    - `sudo apt install bettercap aircrack-ng`
2. [ ] **Python Dependencies:** Run `pip install -r requirements.txt --break-system-packages` (or create a virtual environment) and verify `websockets`, `qrcode`, and `dpkt` install without errors.
3. [ ] **Bettercap API & Monitor Mode:** Bettercap requires a wireless interface in Monitor Mode. Because the Pi Zero only has one Wi-Fi chip, putting it into Monitor Mode will kill your internet connection. 
    - First, follow the instructions in `BTPAN_SETUP.md` to bridge your internet connection over Bluetooth to your phone.
    - Once Bluetooth is tethered, enable Monitor Mode manually (do NOT use `airmon-ng check kill` as it kills Bluetooth too!):
      ```bash
      sudo ip link set wlan0 down
      sudo iw dev wlan0 set type monitor
      sudo ip link set wlan0 up
      ```
    - Launch Bettercap with API bindings: `sudo bettercap -iface wlan0 -api-rest -api-websocket`
4. [ ] **Daemon Boot:** Open a *second* SSH terminal. Start OpenClawGotchi (`python3 src/main.py`). Verify in the logs that both `SubconsciousPwn` and `NervousSystem` threads start successfully without crashing.

## Phase 2: The Subconscious Daemon (`subconscious_pwn.py`)
**Objective:** Validate that the bot autonomously attacks targets.
1. [ ] **Recon Initialization:** Verify the daemon runs `wifi.recon on` and `ble.recon on`.
2. [ ] **Target Selection:** Monitor logs to ensure the bot ignores `OPEN` networks and identifies WPA networks with active clients.
3. [ ] **Deauth Execution:** Verify the bot fires `wifi.deauth <mac>` up to 3 times per target before moving on.
4. [ ] **Channel Hopping:** Ensure the daemon periodically hops channels (`wifi.recon.channel <ch>`).

## Phase 3: The Nervous System (`bettercap_listener.py`)
**Objective:** Validate that hardware events trigger E-Ink reflexes and memory storage.
1. [ ] **Handshake Capture (`wifi.client.handshake`):** 
    - Trigger a fake capture (or capture a real one). 
    - *Expected:* E-Ink screen flashes the `hunting` face. LLM memory logs: "My subconscious daemon captured a WPA handshake..."
2. [ ] **BLE High-Value Target (`ble.device.new`):**
    - Walk near the bot with an Apple device or a Flipper Zero with Bluetooth enabled.
    - *Expected:* E-Ink screen flashes `tracking` face. Log outputs "High-value device detected".
3. [ ] **Auto-Detection Reflex (`wifi.ap.new`):**
    - Manually create `/root/handshakes/wpa-sec.cracked.potfile` with dummy data matching your home network SSID.
    - *Expected:* E-Ink footer updates to `[STATUS: Pass: <your_password>]` and face changes to `excited`.

## Phase 4: Daemon Control IPC Bridge (LLM Tools)
**Objective:** Test the Discord bot's ability to issue commands to the background thread.
1. [ ] **`pwn_status`:** Message the bot: *"What is your hacking status?"* -> *Expected:* Bot replies with active AP count, clients, and handshakes captured.
2. [ ] **`pwn_pause(minutes)`:** Message the bot: *"Pause hacking for 2 minutes."* -> *Expected:* `/tmp/pwn_pause` is created. Logs show "Daemon paused. Sleeping..."
3. [ ] **`pwn_lock_target(bssid)`:** Message the bot: *"Focus all attacks on 11:22:33:44:55."* -> *Expected:* `/tmp/pwn_target` is created. Daemon immediately locks onto that target's channel and stops hopping.
4. [ ] **`pwn_whitelist(mac)`:** Message the bot: *"Whitelist the MAC aa:bb:cc:dd:ee."* -> *Expected:* MAC is appended to `.env`. The daemon dynamically reloads the list and ignores the AP.

## Phase 5: Cloud Cracking (WPA-Sec)
**Objective:** Verify `.pcap` hash conversion and password retrieval.
1. [ ] **`pwn_crack(pcap)`:** Message the bot: *"Upload my handshake to wpa-sec."* -> *Expected:* API Key from `.env` is read. File is successfully HTTP POSTed.
2. [ ] **`pwn_check_cracks()`:** Message the bot: *"Check if any passwords cracked."* -> *Expected:* HTTP GET to wpa-sec. Downloaded `potfile` is parsed. A `.pcap.cracked` file is generated locally, and the LLM repeats the password to you in Discord.

## Phase 6: E-Ink QR Connect
**Objective:** Validate visual password display features.
1. [ ] **QR Generation:** Send a command to `pwn_show_qr("Your_SSID")`. 
2. [ ] **Display Override:** *Expected:* The normal E-Ink face disappears, replaced by a scannable QR Code and plaintext credentials on the right side of the screen. Scan it with an iPhone/Android to verify it connects to the network.
3. [ ] **QR Cleanup:** Send `pwn_hide_qr()`. *Expected:* QR code vanishes, and the normal animation engine resumes.

## Phase 7: Dynamic Tool API (SDK) Validation
**Objective:** Verify the bot can successfully write, compile, and reload a new Python tool via the `create_custom_tool` interface without modifying the core codebase.
1. [ ] **Tool Creation:** Message the bot in Discord: *"Use `create_custom_tool` to make a tool called `test_math` that multiplies two numbers."*
2. [ ] **Decorator Injection:** Verify that the file `src/extensions/dynamic/test_math.py` is successfully created and properly imports `@register_tool` from the SDK.
3. [ ] **Syntax Validation:** Message the bot: *"Run `safe_restart()` to reload your engine."*
4. [ ] **Reboot Recovery:** Wait 5 seconds. Send the bot another message: *"Can you test the `test_math` tool with 5 and 6?"*
    - *Expected:* The bot successfully identifies the `test_math` JSON schema injected by the dynamic loader, executes the function, and returns `30` without crashing.

## Phase 8: Vercel Soft Skills Integration
**Objective:** Validate that the system prompt dynamically injects Markdown procedures downloaded via `npx skills add`.
1. [ ] **Package Installation:** Run `npx -y skills add vercel-labs/skills --skill tool-calling` on the Pi terminal and select "OpenClaw (skills)" as the target.
2. [ ] **Directory Validation:** Verify that `skills/tool-calling/SKILL.md` is populated with the correct Markdown content.
3. [ ] **LLM Awareness:** Message the bot in Discord: *"List your current Instructional Skills from Vercel."* 
    - *Expected:* The bot identifies `tool-calling` in its system prompt text block.
4. [ ] **Skill Execution:** Message the bot: *"Use `read_vercel_skill('tool-calling')` and summarize what you learned."* 
    - *Expected:* The bot successfully ingests the markdown procedure and summarizes the concept.

## Phase 9: Hardening & System Integrity
**Objective:** Validate that the system handles IPC, invalid inputs, and malformed hardware data gracefully.

1. [ ] **Atomic IPC Bridge Test:**
    - **Step 1:** While the bot is running, issue a pause command via Discord: `/use pwn_pause minutes=5`
    - **Step 2:** Check the filesystem: `cat /tmp/daemon_control.json`. Verify `paused_until` is set correctly.
    - **Step 3:** Check the Subconscious logs. Verify the daemon reports: "Daemon is paused by LLM. Waking up in..."
    - **Step 4:** Clear the lock via Discord: `/use pwn_lock_target bssid=clear`
    - **Step 5:** Verify JSON `target_lock` is `null`.

2. [ ] **SDK Tool Validation Test:**
    - **Objective:** Test that the AI can self-correct when passing bad data.
    - **Step 1:** Issue a command with a deliberately wrong type: `/use pwn_pause minutes="five minutes"` (passing a string instead of an int).
    - **Expected:** The tool returns: "Error: Parameter 'minutes' must be an integer."
    - **Step 2:** Observe the AI's response. It should recognize the error and re-fire the tool with a valid integer (`5`).

3. [ ] **Handshake Integrity Test:**
    - **Objective:** Ensure the bot doesn't record "ghost" handshakes.
    - **Step 1:** Manually trigger a fake Bettercap event with a non-existent file:
      ```bash
      curl -X POST http://localhost:8081/api/session -u pwnagotchi:pwnagotchi -d '{"cmd": "events.push wifi.client.handshake {\"ap\": \"AA:BB:CC:DD:EE:FF\", \"file\": \"/tmp/fake.pcap\"}"}'
      ```
    - **Expected:** `NervousSystem` logs: "REFLEX BLOCKED: ... file is missing or empty."
    - **Expected:** No E-Ink update, no new fact added to memory.
    - **Step 2:** Create a dummy file: `echo "data" > /tmp/real.pcap`. Re-trigger the event pointing to `/tmp/real.pcap`.
    - **Expected:** "REFLEX TRIGGERED: Valid Handshake captured..." and the `hunting` face appears.

---
*Note: Run all tests in a controlled environment to avoid interfering with neighbor networks.*

