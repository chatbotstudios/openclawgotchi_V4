# OpenClawGotchi: Pwnagotchi Skills Implementation Plan

This document outlines the architectural plan to integrate research network capabilities (WiFi Pwning, Handshake Capture, Deauth) directly into OpenClawGotchi, merging the core strengths of Pwnagotchi architecture with our LLM-driven semantic Agent.

## 1. The Core Dependency: Bettercap
Pwnagotchi does not natively hack WiFi; it acts as a controller for **Bettercap**. To bring these features to OpenClawGotchi, we must install and run Bettercap as a background service on the Raspberry Pi Zero.
- **Service Name:** `bettercap.service`
- **Configuration:** Run Bettercap with the REST API and WebSocket interfaces enabled (typically on `localhost:8081`).
- **Interface:** `wlan0mon` (The internal Pi Zero WiFi chip must be put into monitor mode using `nexmon` or an external USB WiFi adapter must be used).

## 2. The Agentic Implementation: `gotchi-skills/wifi_pwn`
Unlike Pwnagotchi, which uses an A2C Reinforcement Learning algorithm to blindly maximize captures, OpenClawGotchi uses an **LLM Reasoning Engine**. We will expose Bettercap's API to the LLM via a new Skill.

### Proposed Tool Definitions (`SKILL.md`)
We will create a new skill directory `gotchi-skills/wifi_pwn/` containing the following tools:

#### A. `start_recon()`
- **Function:** Hits the Bettercap API to run `wifi.recon on`.
- **LLM Context:** "Use this tool to survey the area for vulnerable 2.4GHz/5GHz Access Points."
- **Output:** Returns a list of AP MACs, SSIDs, and client devices (Stations) currently visible.

#### B. `attack_target(bssid, attack_type="deauth")`
- **Function:** Tells Bettercap to launch a specific attack against a target.
    - `deauth`: Sends deauthentication frames to disconnect clients, forcing them to reconnect and broadcast the WPA handshake.
    - `associate`: Attempts a PMKID association attack directly against the router.
- **LLM Context:** "Use this to aggressively target a specific AP to capture a handshake."

#### C. `get_handshakes()`
- **Function:** Reads the `/root/handshakes/` directory to see how many `.pcap` files have been captured today.
- **LLM Context:** "Check your 'inventory' of captured networks."

## 3. The Asynchronous Event Loop (The "Nervous System")
Pwnagotchi is event-driven; when it captures a handshake, it immediately changes its face and writes a log. OpenClawGotchi needs to "feel" these events asynchronously.

**Implementation:**
Create a lightweight background daemon `src/hardware/bettercap_listener.py`:
1. Connects to `ws://localhost:8081/events` (Bettercap's WebSocket).
2. Listens specifically for the `wifi.client.handshake` event.
3. **The Trigger:** When a handshake is caught, the daemon instantly:
    - Calls `update_display(mood="hunting", text="SAY: Handshake captured! | STATUS: MODE: P")` (Leveraging our new Universal Animation Engine).
    - Writes a memory log to `gotchi.db` ("Captured handshake for SSID: HomeWiFi").
    - Optionally pings the Human on Discord: "Boss, I just snatched a handshake!"

## 4. UI Engine Integration
We already have the visual layout ready thanks to our recent Pwnagotchi UI refactor.
- **Header:** Add an `H: 0` counter next to CPU and RAM to display session Handshakes.
- **Faces:** The LLM will naturally use our new `custom_faces.json` (e.g., `( 0 _ 1 )` or `[■_■]`) when discussing its network captures.

## 5. Security & Safety Considerations
- **Containment:** Because the LLM is driving the attacks, we must implement a **Whitelist/Blacklist** in the Python tool layer. The tool `attack_target(bssid)` MUST intercept the LLM's request and check against an `.env` variable `WHITELISTED_MACS`. If the target isn't whitelisted, the Python script blocks the attack and returns an error to the LLM.
- **Consent:** Do not run active deauths on public networks.

## Summary of the LLM Loop
Instead of a rigid state machine, the workflow becomes entirely conversational:
**Human:** "Scan the area."
**Gotchi:** *(Runs `start_recon()`)* "I see 3 networks. 'Netgear5' has 2 active clients."
**Human:** "Deauth the clients on Netgear5."
**Gotchi:** *(Runs `attack_target('Netgear5')`, changes face to `intense`)* "Sending deauth packets now. Let's see if we catch the handshake..."
