# 📡 WORKFLOW: BLE Tactical Hunt (Automated Sweep)

> This is a customizable personal workflow for OpenClawGotchi's BLE tracking capabilities.
> It defines the exact autonomous procedure the agent must follow when you ask it to hunt for Bluetooth devices.

> ⚖️ **Authorized Research Only:** All BLE enumeration, proximity tracking, and device logging performed by this workflow is conducted exclusively on equipment the operator owns or has explicit permission to audit, for security research, CTF practice, and personal network hardening purposes only.

## 🧠 Trigger Phrases
- "Hunt for BLE"
- "Track Bluetooth for [X] minutes"
- "Start a BLE sweep"

## 📋 The Autonomous Workflow

When the operator initiates a BLE hunt, you MUST NOT simply run one static scan and stop. You MUST orchestrate a fully automated background sweep using your scheduling tools, allowing you to remain conversational while hunting.

Follow these exact steps:

### Phase 1: Initiation & Wireless Prep
1. Acknowledge the command tactically. Inform the user you are initializing a timed sweep and state the interval of the pulse.
2. Determine the frequency of the pulse based on the total time requested (e.g., for a 60-minute hunt, a pulse every 3 or 5 minutes is ideal).
3. If the user asked to lock onto a specific target (e.g., "Lock onto Apple devices"), note this constraint.
4. **Wireless Prep**: Inform the user that they can establish a Bluetooth PAN Tether for cloud-sync on the go, or go completely off-grid. Assure them the hunt will continue offline.

### Phase 2: Scheduling the Pulse
Use the `gotchi tasks` or scheduling API to create the background sweeping job:
- **Command**: Run `gotchi create_recurring_task` (or equivalent).
- **Task**: The scheduled task MUST execute the `gotchi pwn_ble_scan` command.
- **Interval**: Set to the calculated interval (e.g., `5m`).

### Phase 3: The Background Execution (Automated & Offline)
Once scheduled, you are free to go to sleep or handle other operator requests. 
Behind the scenes:
1. Every X minutes, the cron job executes `gotchi pwn_ble_scan`.
2. **Graceful Failures**: The scanner operates 100% locally on the Pi. It will gracefully bypass any online API lookups if there is no Wi-Fi.
3. The `pwn_ble_scan` tool automatically queries Bettercap, parses the live ephemeral memory, and identifies the top 15 closest devices.
4. The tool **automatically appends** the scan data to the local SD card at: `~/openclawgotchi_V4/handshakes/BLE/scans.log`.
5. If a specific MAC is locked via `gotchi pwn_ble_track <MAC>`, the daemon logs the event in `~/openclawgotchi_V4/handshakes/BLE/tracking.log`.
6. **E-Ink Status Tracking**: The background daemon will automatically update the E-Ink display with tracking or sniffing faces to provide real-time physical feedback on the walk!

### Phase 4: Conclusion & Debrief (Optional)
If requested by the user, at the end of the time period, you should:
1. Delete the scheduled sweeping task using `gotchi delete_cron_job <ID>`.
2. Clear the ephemeral radar using `gotchi pwn_ble_purge`.
3. Use `gotchi read_file` on `handshakes/BLE/scans.log` to read the historical ledger and provide a summary of the most prominent devices detected during the sweep.

## 🛡️ Critical Guidelines
- **Zero Internet Dependency**: Do not rely on web search or online tools while the sweep is active. Assume you are fully off-grid.
- **Do not** attempt to run a python `while True` loop with `time.sleep()`. You must use the cron/task scheduling tools so the main thread remains non-blocking.
- **Do not** hallucinate BLE targets. Always rely on the output provided by `gotchi pwn_ble_scan` and the physical data logged in `scans.log`.
