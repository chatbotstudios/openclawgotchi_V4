# 🎯 Full Pwn Mode (Targeted Eradication & Auditing)

## 📌 Primary Objective
While standard `launch_offline_hunt` sweeps randomly across all Wi-Fi channels passively gathering whatever handshakes fall into its net, **Full Pwn Mode** is a highly aggressive, precision-targeted RF assault. It leverages the AI's ability to lock onto a specific BSSID, focus the hardware's entire TX power on deauthenticating clients, and immediately process the captured cryptographic material.

---

## 🛠 Required Tools & Capabilities

To execute a Full Pwn Mode operation, rely on these tools sequentially:

- **`pwn_status`**: Identifies high-value targets (networks with active clients transmitting data).
- **`pwn_lock_target(bssid)`**: The defining tool of this mode. It commands the Bettercap subconscious to stop channel hopping, lock the Wi-Fi radio to the target's specific channel, and focus all deauthentication bursts on that single BSSID.
- **`launch_offline_hunt(duration_minutes)`**: Used to initiate the actual offline drop after locking the target.
- **`pwn_crack`**: Instantly executed upon returning online to brute-force the targeted handshake.

---

## 📝 Execution Workflow (The 4-Step Gauntlet)

When the USER commands you to enter "Full Pwn Mode" on a target, execute the following tactical playbook:

### Phase 1: Target Acquisition (Recon)
1. Do not go offline blindly. If the user hasn't provided a BSSID, run `pwn_status` to scan the immediate area.
2. Select a target with **active clients** (deauth attacks do not work on empty networks).
3. Report the selected target's SSID, BSSID, and Client Count back to the user with a confident, aggressive personality tone.

### Phase 2: The Lock-On
1. Execute `pwn_lock_target(bssid)` using the chosen target's MAC address.
2. Update your internal memory (`remember_fact`) stating that a targeted assassination of this BSSID has commenced.
3. Your E-Ink display will automatically shift focus to this target. 

### Phase 3: The Deep Dive
1. Run `launch_offline_hunt(duration_minutes)`. For a focused pwn, 3 to 5 minutes is usually sufficient, as the radio is no longer wasting time hopping across 14 different channels.
2. The UI will instantly invert to Dark Mode, and the newly injected real-time countdown timer will display on your screen.
3. Disconnect and allow the subconscious daemon to repeatedly deauth the locked clients and capture the resulting 4-way WPA handshake.

### Phase 4: Exploitation & Debrief
1. Upon network restoration, the system's `events.emit('hunt_completed')` will wake you up.
2. Read the results. If a handshake was successfully acquired, **immediately** follow up by executing `pwn_crack` to attempt a local dictionary attack against the capture.
3. If successful, present the plaintext password to the user. If it fails, suggest using a larger remote cracking rig.
4. Execute `pwn_lock_target("")` (empty string) to clear the lock and return the daemon to normal channel-hopping behavior.

---

## ⚠️ Tactical Considerations & Constraints

1. **Tunnel Vision Risk**: While locked onto a target, your Gotchi will completely ignore all other networks. Do not leave the system in Full Pwn Mode indefinitely. **Always clear the lock (`pwn_lock_target("")`) after the operation.**
2. **Client Necessity**: Never lock onto an empty network (0 clients). A 4-way handshake requires a client device to reconnect to the router. No clients = No handshake = Wasted hunt.
3. **Hardware Heat**: Focused deauth bursts can generate significant heat on the Pi's Wi-Fi chip. If executing multiple back-to-back pwns, suggest a `health_check` to monitor core thermals.
