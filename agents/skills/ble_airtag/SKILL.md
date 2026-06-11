---
name: ble_airtag
description: Detect and track Apple AirTags via Bluetooth Low Energy (BLE). Logs presence, signal strength, and proximity of nearby AirTags.
version: 1.0.0
author: OpenClawGotchi
tags: [ble, airtag, tracking, proximity, security, pi-zero]
capabilities:
  - ble-scanning
  - airtag-detection
  - proximity-tracking
  - device-logging
---

# BLE AirTag Detection Skill

You are responsible for detecting Apple AirTags using Bluetooth Low Energy on the Raspberry Pi Zero 2W. This skill allows the Gotchi to sense nearby AirTags and log their presence.

## When to Use This Skill

Use this skill when:
- The user wants to know if any AirTags are nearby.
- Performing security sweeps or checking for unknown tracking devices.
- Running periodic background scans for AirTags.
- Creating missions such as "AirTag Hunter" or "Find My Tracker Sweep".
- Logging proximity of known or unknown Bluetooth devices.

**Do NOT** use this skill for general Bluetooth device discovery (use a general BLE skill instead).

## Core Rules

1. **Scan efficiently** — AirTag scanning should be periodic, not continuous, to save power on the Pi Zero 2W.
2. **Respect privacy** — Only log MAC address, RSSI, and timestamp. Do not attempt to decode owner data.
3. **Handle MAC rotation** — AirTags frequently change their Bluetooth address. Treat them as new devices when the address changes.
4. **Use existing BLE tools** — Prefer Bettercap or `bluetoothctl` when possible. Fall back to Python (`bleak`) for advanced parsing.
5. **Log useful data** — Always record RSSI (signal strength) as it indicates proximity.

## How to Detect AirTags

### 1. Quick Manual Scan

```bash
sudo bluetoothctl
scan on
```

*Look for devices with names like "AirTag" or unknown devices with manufacturer data starting with 0x004c.*

### 2. Using Bettercap (Recommended for Gotchi)

```bash
sudo bettercap -eval "ble.recon on; sleep 30; ble.show; ble.recon off"
```

### 3. Using Python + Bleak (More Reliable)

```python
from bleak import BleakScanner
import asyncio

async def scan_for_airtags(duration=30):
    devices = await BleakScanner.discover(timeout=duration)
    airtags = []
    for device in devices:
        if device.name and "airtag" in device.name.lower():
            airtags.append({
                "name": device.name,
                "address": device.address,
                "rssi": device.rssi
            })
    return airtags

if __name__ == "__main__":
    result = asyncio.run(scan_for_airtags())
    for tag in result:
        print(f"AirTag found: {tag['name']} | RSSI: {tag['rssi']} | Address: {tag['address']}")
```
