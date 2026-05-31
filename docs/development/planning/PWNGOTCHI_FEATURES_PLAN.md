# OpenClawGotchi: Advanced Pwnagotchi Features Roadmap

This document serves as the architectural blueprint for the remaining legacy Pwnagotchi features that we plan to adapt and integrate into OpenClawGotchi's LLM-driven ecosystem.

## ✅ 1. Auto-Cracking & Cloud Integration (WPA-Sec) [COMPLETED]
- **Status:** Done! The `pwn_crack` and `pwn_check_cracks` tools natively post `.pcap` files to the wpa-sec cloud and retrieve the plaintext passwords automatically. No local Hashcat required!

## ✅ 2. Deauth Defenses & Daemon Control [COMPLETED]
- **Status:** Done! The LLM now has full control over the Subconscious Daemon via `pwn_pause(minutes)`, `pwn_whitelist(mac)`, and `pwn_lock_target(bssid)` utilizing a local `/tmp/` IPC bridge.

## ✅ 3. QR Connect (Display Password) [COMPLETED]
- **Status:** Done! Based on the `display-password.py` Pwnagotchi plugin. The bot automatically parses the cracked `potfile` when near a known network and changes its E-Ink screen. The LLM can also explicitly push the QR Code to the display via `pwn_show_qr`.

## ✅ 4. Bluetooth Tethering (BTPAN) [COMPLETED]
OpenClawGotchi relies on Discord and the Gemini/Claude API to function. When taken outdoors, it loses connection to the home router and becomes "brain dead" (though its Subconscious Daemon will continue hacking).
- **Status:** Done! A new `BTPAN_SETUP.md` guide was created to configure `NetworkManager` to ignore `wlan0` and bridge internet traffic exclusively over the `bnep0` Bluetooth network. This allows `wlan0` to stay in Monitor Mode permanently while the bot stays online via the user's phone hotspot.

## ⏳ 5. GPS Wardriving & Heatmapping
Pwnagotchi natively supports mapping captured handshakes using GPS modules.
- **The Goal:** Append geographic coordinates to every captured `.pcap` and `ble.device`.
- **Implementation:** Integrate `bettercap`'s `gps` module. Require a USB/UART GPS dongle attached to the Pi Zero. We will update `bettercap_listener.py` to pull the `latitude` and `longitude` from the Bettercap session data when a handshake is logged.
- **LLM Reflex:** "I captured a handshake at coordinates 40.7128° N, 74.0060° W. Added to the Wigle map."

## ⏳ 6. PwnGRID (Global Scoreboard)
Pwnagotchis use PwnGRID to anonymously upload their stats and rank themselves globally.
- **The Goal:** Create a customized leaderboard for ClawGotchi / OpenClawGotchi variants.
- **Implementation:** Build a lightweight cloud API. The LLM can periodically check its rank against other bots.
- **LLM Reflex:** "I just hit Rank 45 globally! Let's go hunt some more."
