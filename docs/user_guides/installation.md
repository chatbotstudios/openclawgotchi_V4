# OpenClawGotchi Installation Guide

This guide will walk you through setting up OpenClawGotchi on a Raspberry Pi from scratch.

## Prerequisites
- **Hardware:** Raspberry Pi Zero 2W (recommended), a display (e.g., Waveshare 2.13" E-Ink), and a power source.
- **OS:** Raspberry Pi OS Lite (64-bit). No desktop.

> **Note:** Ensure your Pi is connected to the internet and you can SSH into it before proceeding.

---

## 1. Initial Setup

1. **Update your system:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Enable SPI (required for E-Ink display):**
   ```bash
   sudo raspi-config
   ```
   Navigate to **Interface Options** -> **SPI** -> select **Yes**.

3. **Install System Dependencies:**
   ```bash
   sudo apt install -y python3-pip python3-venv git libopenjp2-7 libtiff5 python3-dev python3-rpi.gpio fonts-noto-cjk fonts-dejavu nodejs npm
   ```

---

## 2. Installation

Clone the repository and run the setup script.

```bash
git clone https://github.com/chatbotstudios/openclawgotchi_V4.git
cd openclawgotchi_V4
./setup.sh
```

**The `setup.sh` script will automatically:**
- Verify Python and system dependencies.
- Prompt you for your Discord/Telegram API Tokens and User IDs to generate your `.env` file securely.
- Install all necessary Python libraries inside a virtual environment.
- Create your `.workspace` directory to hold the bot's "soul" and memory.
- Create and enable the `gotchi.service` so it boots on startup.
- Offer to run the `harden.sh` script to optimize the Pi Zero's memory usage and disable unnecessary radios (like Bluetooth) to save RAM.

---

## 3. Configuration & Boot

If you need to manually edit your keys later, simply run:
```bash
nano .env
```

To manage the background service manually:
- **Start:** `sudo systemctl start gotchi`
- **Stop:** `sudo systemctl stop gotchi`
- **Status:** `sudo systemctl status gotchi`
- **Logs:** `gotchi logs` or `journalctl -u gotchi -f`

Once the service is started, the OpenClawGotchi will initialize its E-Ink display, ping your Discord/Telegram channel, and begin its autonomous loop!

---

## 4. Updating OpenClawGotchi

To update your bot with the latest features, bug fixes, and CLI tools, pull the latest code from GitHub and restart the daemon:

```bash
cd ~/openclawgotchi_V4
git pull
sudo systemctl restart gotchi
```
*(If dependencies changed significantly, you may also need to re-run `./setup.sh` to update your Python environment.)*

---

## 5. Troubleshooting / Common Pi Issues

If your bot crashes or the screen remains blank, run `gotchi logs` to monitor the system.

### Advanced Setup
For tactical iPhone tethering, see the [BTPAN Setup Guide](docs/BTPAN_SETUP.md).

### 1. "pam_unix(sudo:auth): conversation failed"
This means the bot tried to update the screen or restart itself but lacked passwordless `sudo` privileges. Run:
```bash
echo "$USER ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/$USER
```

### 2. Missing Discord or LLM Dependencies
If you see `ModuleNotFoundError: No module named 'discord'`, it means your environment is missing the core bot libraries. Run:
```bash
pip3 install discord.py psutil litellm --break-system-packages
```

### 3. E-Paper Screen Stays Blank (Missing PIL/spidev)
If the screen never updates, the `root` user might be missing the imaging libraries. Install them globally:
```bash
sudo pip3 install Pillow RPi.GPIO spidev --break-system-packages
```

### 4. Manually Debugging the Screen
To force the screen to refresh and see raw Python error tracebacks (bypassing the silent daemon), run the UI script directly:
```bash
sudo python3 ~/openclawgotchi_V4/src/ui/gotchi_ui.py --mood hacker --text "SAY: Debugging..." --full
```
