# Troubleshooting Guide

This guide covers common issues you might encounter with OpenClawGotchi V3 and how to fix them.

## 1. Blank or Frozen E-Ink Screen

**Symptoms:** The screen doesn't update after boot, stays completely blank, or shows a fragmented image.

**Possible Fixes:**
- **Check Hardware Connections:** Ensure the Waveshare HAT is securely pressed onto the GPIO pins.
- **Check Configuration:** Verify your `.env` file specifies the correct E-Ink display model. By default, V3 targets the `epd2in13_V4`.
- **Restart the Service:** Sometimes the SPI interface hangs. Run:
  ```bash
  sudo systemctl restart gotchi
  ```
- **Force UI Refresh via CLI:**
  ```bash
  gotchi ui refresh
  ```

## 2. Boot Loops or Service Crashing

**Symptoms:** The device restarts repeatedly, or the `gotchi` service keeps failing.

**Possible Fixes:**
- **Check Logs:** The most important step. Run:
  ```bash
  journalctl -u gotchi -n 50 -f
  ```
  Look for Python tracebacks.
- **OOM (Out of Memory):** The Pi Zero 2W has limited RAM (512MB). If you installed heavy dependencies, the kernel might be killing the service. Check `dmesg -T | grep -i oom`.
- **API Keys:** Ensure your `.env` contains valid LLM API keys. If the "Soul" cannot initialize, it may panic and restart.

## 3. Missing Wi-Fi / BLE Interfaces

**Symptoms:** The bot complains it cannot scan networks or capture handshakes. `iwconfig` shows no `mon0` interface.

**Possible Fixes:**
- **Check Bettercap / Nexmon:** Ensure the setup script (`./setup.sh`) successfully installed the required networking tools.
- **Manual Interface Check:**
  ```bash
  sudo ip link set wlan0 up
  sudo iw dev wlan0 interface add mon0 type monitor
  ```
- **Reboot:** Sometimes the radio chip hangs on the Pi Zero 2W. A full `sudo reboot` often resolves radio state issues.

## 4. AI Brain is Unresponsive

**Symptoms:** The CLI works, but the bot isn't speaking in Discord or updating its thoughts.

**Possible Fixes:**
- **Check LLM API Limits:** You might have hit rate limits or billing limits on your LLM provider.
- **Workspace Corruption:** Check if `workspace/SOUL.md` or `workspace/IDENTITY.md` was accidentally deleted or malformed. Restore from `templates/` if necessary.
