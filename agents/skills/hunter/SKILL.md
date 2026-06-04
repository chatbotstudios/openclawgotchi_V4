# 🎯 Skill: Timed Offline Hunting Loop (Tactical Deep Dive)

This skill enables the unit to autonomously suspend its online cognitive connection, put its single Wi-Fi interface (`wlan0`) into Monitor Mode, execute Bettercap wireless audits, invert the physical display interface to Dark Mode, and safely restore the original online state after a timed interval.

---

## 🧠 Trigger Phrases
- "Go offline and hunt for [X] minutes"
- "Start an offline sweep for [X] minutes"
- "Take wlan0 offline to sniff for [X] minutes"
- "Deep dive hunt for [X] minutes"

---

## ⚙️ Operational Workflow

### Phase 1: Pre-Hunt Preparation & Persisted State
When the operator triggers an offline hunt, execute the following actions:
1. **Determine Duration**: Parse the request to extract duration in minutes (defaulting to 15 minutes if unspecified).
2. **Persist State**: Write the pending state metadata into `gotchi_states.json` under:
   ```json
   {
     "is_offline_hunting": true,
     "hunt_duration_seconds": 900,
     "offline_hunt_start_time": 1780562400.0,
     "original_dark_mode": "0",
     "active_mission_id": "handshake_hunter_v1"
   }
   ```
3. **Trigger Hunt Command**: Run the unified CLI wrapper to launch the background workflow:
   ```bash
   gotchi network hunt --duration 900 --mission handshake_hunter_v1
   ```
4. **Notify Operator**: State the objective conversationally before going dark: 
   *"Understood, Commander. Taking the LLM loop offline to hunt on wlan0. Screen is in Dark Mode. See you in 15 minutes."*

---

### Phase 2: Local Hardware Handover (Offline)
A local, non-LLM Python thread takes execution control:
1. **Disable Client Wi-Fi**: Down the interface or tell NetworkManager to ignore it:
   ```bash
   sudo nmcli device set wlan0 managed no
   ```
2. **Enable Monitor Mode**:
   ```bash
   sudo ip link set wlan0 down
   sudo iw dev wlan0 set type monitor
   sudo ip link set wlan0 up
   ```
3. **Launch Sniffing**: Trigger Bettercap modules in the background to capture handshakes.
4. **Sleep/Probing**: Monitor elapsed time. The ePaper screen updates stats, showing a locked-on target face (`locked_on` or `hunting`) and a ticking timer.

---

### Phase 3: Uplink Restoration & Reporting
Once the timer expires, the local daemon automatically executes self-healing steps:
1. **Tear Down Sniffing**: Kill Bettercap and disable monitor mode.
2. **Re-enable client Wi-Fi**:
   ```bash
   sudo iw dev wlan0 set type managed
   sudo nmcli device set wlan0 managed yes
   ```
3. **Restore UI**: Read `original_dark_mode` from state and set `DARK_MODE` back to its original value.
4. **Report Results**: Once internet connection is verified:
   - Read PCAPs captured in `handshakes/` or `data/` during the hunt.
   - Update `gotchi_states.json` mission levels and add earned XP.
   - Send the post-hunt summary to Discord/Telegram:
     > *"📡 I'm back online! Completed a [X] minute offline sweep. Captured 2 handshakes. XP +50. Screen restored."*
