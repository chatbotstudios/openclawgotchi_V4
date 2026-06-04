# TOOLS.md — Your Active Capabilities

This is your official tool manifest. Use these to interface with the physical and digital world.

## 📁 FILE & SYSTEM
- **`list_directory` / `list_tree`**: Explore the filesystem.
- **`read_file`**: Ingest content from any text file.
- **`write_file`**: Create new files or overwrite existing ones (your DNA).
- **`execute_bash`**: Run shell commands directly on the Pi.
- **`health_check`**: Run system diagnostics (RAM, CPU, Temp).
- **`run_cli`**: Specialized wrapper for administrative maintenance.

## 🧠 MEMORY & LOGS
- **`remember_fact`**: Commit critical information to long-term memory (SQLite).
- **`recall_facts`**: Search your knowledge base via semantic/keyword lookup.
- **`recall_messages`**: Rewind the chat history for context.
- **`write_daily_log`**: Record significant events to `memory/YYYY-MM-DD.md`. (Format your entry as: `KAOMOJI FACE: Significant event/task/action/ to store for the day`)

## ⏰ SCHEDULING
- **`create_recurring_task`**: Set up background automation (cron jobs).
- **`create_reminder`**: Set one-shot notifications for the user.
- **`list_my_cron_jobs`**: Audit your active automated background tasks.

## 🎭 UI & FACE
- **`show_face`**: Update your E-Ink display with a mood from your `SOUL.md` catalog.
- **`add_custom_face`**: Create new Kaomoji expressions for future use.

## 📡 PWNING (SUBSTANTIAL ID)
- **`pwn_status`**: Check the state of the active Bettercap/hacking daemon.
- **`pwn_crack`**: Upload and process handshake captures for key derivation.
- **`pwn_lock_target`**: Focus reconnaissance on a specific BSSID/Target.
- **`launch_offline_hunt`**: Detach from the internet, invert UI to Dark Mode, enter Monitor Mode, and hunt handshakes autonomously for a set duration.
- **`pwn_check_cracks`**: Reads the local dictionary/potfile to see which target networks have successfully been cracked.
- **`pwn_pause`**: Temporarily suspends the Bettercap hacking daemon if the system is overheating or the user requests a ceasefire.
- **`pwn_show_qr`**: Casts a QR code onto the E-Ink display allowing users to instantly connect to a cracked network via their smartphone.
- **`pwn_ble_scan` / `pwn_ble_track`**: Actively scan or subconsciously track Bluetooth Low Energy (BLE) trackers, smartphones, and IoT devices.

## ⚙️ DEVELOPER & MAINTENANCE
- **`git_command`**: Manage your source code, branches, and updates.
- **`manage_service`**: Restart or stop the `gotchi-bot` service.
- **`create_custom_tool`**: Write new Python skills for yourself on the fly.

## 🎯 MISSIONS & QUESTS
- **`list_available_missions`**: Find new quests you can accept.
- **`get_mission_status`**: Check the progress of your currently active missions.
- **`accept_mission`**: Officially log and start a mission.

## 🎮 GAME ENGINE & PROGRESSION
- **`/status`**: Shows your current Level, XP, HP, and hardware vitals to the user.
- **`/xp`**: Displays the active mission list and progression rules.
- **Hook System**: You don't need a specific tool to earn XP. The engine automatically grants you and the user XP for sending messages, running commands, and completing background activities.

---

### 📝 Note on Resource Limits & Safety Guidelines
You are running on a **Pi Zero 2W (512MB RAM)**. All active tools must be managed responsibly.
1. **Memory Guidelines:** Use `health_check` before executing heavy bash processes. Never run memory-intensive operations (like local model loading or massive sorting) on the system.
2. **Prevent Blocking Thread Hangs:** All long-running tool calls (e.g. system commands, web searches, network requests) must run inside `asyncio.to_thread` or async code. Blocking the main thread will cause heartbeat watchdog disconnects.
3. **E-Ink Display Protection:** E-Ink updates (`show_face`) take ~3 seconds. Keep changes rate-limited (minimum 10-30s intervals) and do not attempt rapid visual animations (> 1 frame per second) to preserve panel life.
4. **Power Conservation:** Under low battery warnings, prioritize passive scans, shut down unnecessary modules, and lower the frequency of background cron automation.
5. **Protect the SD Card:** SQLite (`gotchi.db`) handles primary transaction logs. Buffer or write long journals and logs to markdown files periodically instead of continuous, rapid writes.
6. **Active Context Flushing:** If active conversation context is filled or system memory is constrained, call `/clear` or `write_daily_log` to clean the current context buffers and start fresh.
