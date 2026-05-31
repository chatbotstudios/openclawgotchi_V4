# 🦋 Gotchi CLI: Field Manual (V3.0)

This skill defines the unit's internal awareness of its own flattened Command Line Interface (CLI). The `gotchi` binary is the primary interface for managing hardware, security, and automation.

## 🛠️ Command Structure

The CLI is organized into the following tactical categories and includes all 75 exposed commands:

### 📡 Pwn & Wireless Auditing
- **`gotchi pwn`**: Full-spectrum Wi-Fi auditing tools wrapper.
- **`gotchi pwn_ble_purge`**: Clear all discovered BLE devices from the tracking database.
- **`gotchi pwn_ble_scan`**: Scan for nearby Bluetooth Low Energy (BLE) devices.
- **`gotchi pwn_ble_track`**: Lock onto a specific BLE MAC address for continuous tracking.
- **`gotchi pwn_check_cracks`**: Checks wpa-sec.stanev.org for newly cracked passwords.
- **`gotchi pwn_crack`**: Uploads a .pcap file to wpa-sec.stanev.org for cracking.
- **`gotchi pwn_hide_qr`**: Removes the QR Code from the E-Ink screen.
- **`gotchi pwn_lock_target`**: Locks the Subconscious Pwn daemon to only track a specific target.
- **`gotchi pwn_pause`**: Pauses the background Subconscious Pwn daemon.
- **`gotchi pwn_show_qr`**: Displays a QR Code on the E-Ink screen to securely share data.
- **`gotchi pwn_status`**: Check the Subconscious Pwn daemon's operational status.
- **`gotchi pwn_system_control`**: Control the physical radio and Bettercap services.
- **`gotchi pwn_whitelist`**: Adds a MAC address to the pwning whitelist to ignore it.

### 🌐 Networking & Tethering
- **`gotchi network`**: Base wrapper for Radio and Networking commands.
- **`gotchi manage_ble_adapter`**: Manage Bluetooth adapter state (on/off) and power.
- **`gotchi manage_net`**: Manage Wi-Fi connections and system diagnostics.
- **`gotchi manage_wifi_interface`**: Manage Wi-Fi connectivity state (on/off).
- **`gotchi net_connect`**: Add a new Wi-Fi network and attempt to connect to it.
- **`gotchi net_forget`**: Forget a saved Wi-Fi network by SSID.
- **`gotchi net_list_saved`**: List all currently saved Wi-Fi networks (SSIDs).
- **`gotchi net_scan`**: Scan for available Wi-Fi networks in range.
- **`gotchi net_show_password`**: Show the password for a saved Wi-Fi network.
- **`gotchi net_status`**: Check the current network connection and IP address.
- **`gotchi tether_pair`**: Orchestrate a trusted pairing bond with a mobile device.
- **`gotchi tether_scan`**: Scan for nearby Bluetooth devices eligible for tethering.
- **`gotchi tether_status`**: Check the current state of the Bluetooth PAN tunnel.
- **`gotchi tether_up`**: Create a PANU network profile and bring the tunnel online.

### ⏰ Scheduling & Automation
- **`gotchi tasks`**: Base wrapper to manage cron tasks, reminders, and config.
- **`gotchi add_scheduled_task`**: Add a standard scheduled task.
- **`gotchi create_recurring_task`**: Create a recurring cron job that will ping the bot on a schedule.
- **`gotchi create_reminder`**: Create a one-shot reminder that will ping the bot once.
- **`gotchi delete_cron_job`**: Delete an active cron job or reminder by its ID.
- **`gotchi list_my_cron_jobs`**: List all currently active cron jobs and their schedules.
- **`gotchi list_scheduled_tasks`**: List all scheduled internal automation tasks.
- **`gotchi manage_cron`**: Manage recurring tasks (cron jobs).
- **`gotchi manage_reminders`**: Manage one-shot reminders.
- **`gotchi remove_scheduled_task`**: Remove a scheduled task by ID.

### 🧠 Knowledge & Memory
- **`gotchi clear`**: Clear local history and CLI context.
- **`gotchi flush_context`**: Clear the entire current conversation history to reset context.
- **`gotchi list_directory`**: List directory contents (single level).
- **`gotchi list_tree`**: List directory contents recursively (tree view).
- **`gotchi read_file`**: Read the contents of a local file.
- **`gotchi recall_facts`**: Search long-term memory for semantic facts.
- **`gotchi recall_memory`**: Search the bot's long-term SQLite memory.
- **`gotchi recall_messages`**: Look back at recent conversation messages and transcripts.
- **`gotchi remember_fact`**: Save a core fact to long-term memory.
- **`gotchi restore_from_backup`**: Restore a file from its `.bak` backup.
- **`gotchi write_daily_log`**: Write an entry to today's daily log file.
- **`gotchi write_file`**: Write content to a file (automatically creates backups).

### 🖼️ Hardware Interface
- **`gotchi ui`**: Base wrapper for UI and Display configuration.
- **`gotchi add_custom_face`**: Add a custom face/mood to the E-Ink collection.
- **`gotchi show_face`**: Display a specific face/mood on the E-Ink screen natively.

### ⚙️ System Diagnostics & Administration
- **`gotchi dash`**: Launch the live tactical dashboard (htop for Gotchi).
- **`gotchi doctor`**: Run a full system diagnostic and repair sequence.
- **`gotchi status`**: Show current hardware, XP, level, and bot status.
- **`gotchi check_mail`**: Check unread mail from sibling/brother bots.
- **`gotchi check_syntax`**: Check Python file syntax for the entire project before restart.
- **`gotchi create_custom_tool`**: Create a new LLM tool dynamically in the workspace.
- **`gotchi execute_bash`**: Execute a raw shell command securely.
- **`gotchi get_status_report`**: Gathers hardware and bot stats into a structured report.
- **`gotchi get_system_time`**: Returns the current system date and time.
- **`gotchi git_command`**: Run a git command in the project repository.
- **`gotchi health_check`**: Run the system health check logic.
- **`gotchi help`**: Show the professional field manual.
- **`gotchi list`**: List all available AI tools installed in the workspace.
- **`gotchi log_change`**: Log a change to `workspace/CHANGELOG.md`.
- **`gotchi log_error`**: Append a critical error to `data/ERROR_LOG.md`.
- **`gotchi logs`**: Stream or manage bot service logs via systemd.
- **`gotchi manage_service`**: Manage systemd services directly.
- **`gotchi mode`**: Switch between lite and pro LLM modes.
- **`gotchi read_architecture`**: Read the bot's architecture mapping to understand internals.
- **`gotchi read_vercel_skill`**: Read a Vercel-standard `SKILL.md` file from the workspace.
- **`gotchi restart`**: Safely restart the Gotchi service.
- **`gotchi restart_self`**: Restart the bot service (with 3s delay to allow ack message).
- **`gotchi run-bot`**: Internal use: Entrypoint for the systemd service.
- **`gotchi run_cli`**: Access the Gotchi Command Center natively.
- **`gotchi safe_restart`**: Check all critical files syntax, then restart the service if safe.
- **`gotchi set_llm_mode`**: Sets the LLM mode (`lite` or `pro`).

---

## 📋 Operational Procedures

### Procedure A: Autonomous Deployment
1. Set the unit to hunt-on-boot: Use `gotchi execute_bash` to ensure the sub-pwn background service is active.
2. Go Off-Grid: `gotchi manage_wifi_interface off`.
3. Disconnect power and deploy in the field.

### Procedure B: Handshake Recovery
1. Run `gotchi execute_bash "ls /root/handshakes"` periodically to see captured souvenirs.
2. If a password is found, run `gotchi net_connect <SSID> <PASS>` to test it.

### Procedure C: Radio Stealth
1. To hide the unit's presence, disable interfaces: `gotchi manage_wifi_interface off` and `gotchi manage_ble_adapter off`.

### Procedure D: Emergency Tethering (iOS/Android)
1. Run `gotchi tether_scan` to identify the host MAC.
2. Run `gotchi tether_pair <MAC>` and confirm on the phone.
3. Ensure phone is on the **Hotspot Settings** screen.
4. Run `gotchi tether_up <MAC>` to activate the tunnel.

---

## 🛡️ Best Practices
- **Power**: Use off-grid modes when not actively hunting to save battery.
- **Brain**: Switch to `gotchi mode lite` for simple chat and `pro` for tactical analysis.
