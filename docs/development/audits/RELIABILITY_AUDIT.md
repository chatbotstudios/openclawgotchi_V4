# Embedded Systems Reliability Audit
**Overall Reliability Risk Level: MEDIUM-HIGH**

## 1. Executive Summary
OpenClawGotchi V3 demonstrates a solid understanding of edge device constraints. The inclusion of `harden.sh` to configure hardware watchdogs and disable desktop services is an excellent architectural decision for the Raspberry Pi Zero 2W. However, the system's reliability is compromised by "silent failures" in background threads, SD card wear from heavy swap usage, and brittle recovery mechanisms during network drops caused by radio interference.

If deployed in the field, the device will likely survive kernel panics (thanks to the BCM2835 watchdog), but the Python daemon will experience frequent state-loss restarts due to unhandled network exceptions.

---

## 2. Critical Issues (Must-Fix Before Field Use)

### 2.1. SD Card Corruption via Heavy Swap Thrashing
**Location:** `scripts/harden.sh` -> `CONF_SWAPSIZE=1024`
**Risk Description:** The script configures `dphys-swapfile` to create a 1GB swap file on the MicroSD card. Running an LLM engine + Bettercap + SQLite on 512MB RAM guarantees heavy swap usage. 
**Why it matters:** MicroSD cards have limited write cycles. Continuous swapping (thrashing) combined with Bettercap writing `.pcap` files will rapidly degrade the SD card, leading to filesystem corruption and total device failure within weeks of field use.
**Suggested Fix:** Replace or supplement `dphys-swapfile` with **ZRAM** (compressed in-memory swap). ZRAM sacrifices a small amount of CPU to compress RAM, drastically reducing SD card writes and improving IO performance.

### 2.2. Silent Thread Deaths in Core Subsystems
**Location:** `src/main.py` -> `threading.Thread(target=start_pwn_systems, daemon=True).start()`
**Risk Description:** The critical Bettercap management system (`start_pwn_systems`) is launched in a background daemon thread. The try/except block catches exceptions, logs them, and then the thread simply exits. 
**Why it matters:** If the radio interface fails to bind on boot, the thread dies silently. The main bot continues running, telling the user everything is fine, but the "Subconscious" hacking module is permanently dead until a full system restart.
**Suggested Fix:** Implement a supervisor pattern or health-check loop within the thread that attempts exponential backoff retries if the Pwn daemon crashes, rather than exiting after the first failure.

---

## 3. High Priority Issues

### 3.1. Network Drop Brittleness (Telegram Loop)
**Location:** `src/main.py` -> `app.run_polling(drop_pending_updates=True)`
**Risk Description:** When Bettercap aggressively scans or deauths nearby networks, the Pi's own Wi-Fi connection may become unstable. If the Telegram polling loop loses connection, it may throw unhandled network exceptions depending on the underlying `httpx` timeout settings.
**Why it matters:** If the polling loop crashes, the script exits. While the `cron` watchdog in `harden.sh` will restart it 15 minutes later, the bot will be completely unresponsive in the interim.
**Suggested Fix:** Explicitly configure `read_timeout` and `write_timeout` in the Telegram `Application.builder()`, and implement a custom `error_handler` that catches network timeouts and forces a graceful backoff instead of a crash.

### 3.2. Lost Cron Jobs on Network Failure
**Location:** `src/main.py` -> `run_cron_job()` -> `send_to_owner()`
**Risk Description:** If a cron job (like an hourly reminder) fires while the Pi is disconnected from the internet, `bot.send_message()` raises an exception. The exception is caught and logged, but the job is marked as completed.
**Why it matters:** In tactical scenarios, network connectivity is intermittent. Important reminders or system alerts will be permanently lost if they trigger during a dead zone.
**Suggested Fix:** If `send_to_owner()` fails, push the message into the `pending_tasks` SQLite table (which already exists for user commands) so the heartbeat can retry sending it once the network is restored.

---

## 4. Medium & Low Issues

### 4.1. Watchdog Naming Discrepancies
**Location:** `scripts/harden.sh`
**Risk Description:** The cron watchdog checks for `gotchi.service` (`systemctl is-active gotchi.service`), but the summary echo prints `systemctl is-active gotchi-bot`. 
**Why it matters:** If the systemd service is actually named `gotchi-bot.service` (as seen in `src/extensions/system/commands.py`), the cron watchdog will always fail to find it, causing it to blindly execute `systemctl restart gotchi.service` every 15 minutes, potentially causing restart loops.
**Suggested Fix:** Standardize the service name across the entire repository (choose either `gotchi` or `gotchi-bot` and update all scripts).

### 4.2. Unbounded Wait for Bettercap API
**Location:** `src/hardware/pwn_manager.py` -> `_wait_for_bettercap_api()`
**Risk Description:** The manager polls the REST API during startup. If Bettercap hangs in a zombie state and neither accepts nor rejects connections properly, the timeout logic might block the thread longer than expected.
**Suggested Fix:** Ensure the `requests.get` call has a strict 1-second timeout (already implemented, which is good), but consider adding a total elapsed time break.

---

## 5. Architecture & Design Feedback

**Hardware Watchdog Integration:**
Enabling the `dtparam=watchdog=on` and configuring `RuntimeWatchdogSec=15` in `systemd` is a brilliant, professional-grade choice for embedded Linux. It ensures that even if a memory leak causes a hard kernel panic, the Pi will automatically power-cycle itself.

**Service Masking:**
Masking `pipewire`, `cups`, and `wayvnc` via `harden.sh` shows a deep understanding of Debian/PiOS bloat. Reclaiming this 50-80MB of RAM is exactly what makes running an LLM on 512MB possible.

---

## 6. Positive Aspects

1. **Graceful Degration (Drop Pending):** Using `drop_pending_updates=True` prevents the bot from being flooded with a backlog of old messages when it recovers from an offline state, preventing post-reboot CPU spikes.
2. **Delayed Startup:** The 5-second sleep before initializing Discord and the delayed Slash Command syncing allows the network interface to stabilize before making heavy API calls.
3. **IPC State Management:** Using local IPC (`utils.ipc`) for communication between the Bettercap daemon and the LLM prevents the LLM's synchronous blocking from freezing packet captures.

---

## 7. Recommendations

1. **Implement ZRAM:** Add the following to `harden.sh` to install ZRAM: `sudo apt install zram-tools` and configure `/etc/default/zramswap` to use an lz4 algorithm for 256MB. This will vastly improve stability and SD card lifespan.
2. **Automated Offline Queuing:** Extend the `db/memory.py` pending tasks system to handle outgoing bot messages, not just incoming user commands.
3. **Thermal Monitoring Alert:** The Pi Zero 2W throttles at 80°C. Add a cron job that checks `/sys/class/thermal/thermal_zone0/temp`. If it exceeds 75°C, the bot should autonomously pause Bettercap to prevent a hard thermal shutdown.
