# OpenClawGotchi V3 Roadmap
*A living document of 50 actionable, high-impact ideas to enhance the OpenClawGotchi V3 ecosystem.*

---

## 🎨 UI & E-Ink Display Enhancements (1-10)
1. **Invert Colors Mode**: Add an easy `.env` toggle for Dark Mode (black background, white text/faces) for better stealth at night.
2. **Dynamic Refresh Scaling**: Automatically reduce the UI refresh rate to 1-minute intervals if battery dips below 20%.
3. **Animated Boot Splash**: Render a multi-frame startup sequence showing the "Soul" booting up before transitioning to the main grid.
4. **QR Code Screen Sharing**: A CLI command `gotchi ui show_qr "text"` that overtakes the screen with a QR code for quick data passing.
5. **Partial Refresh Optimization**: Implement a strict bounding-box partial refresh for the bottom log text only, reducing full-screen flash.
6. **Battery Icon Pipeline**: Read from I2C PiSugar/UPS HATs and dynamically change the battery indicator icon based on real voltage data.
7. **Custom Fonts via CLI**: A command `gotchi ui load_font <path>` to dynamically update the display font without restarting the service.
8. **Idle Screen Savers**: If no handshakes or AI activity happens for 1 hour, switch the screen to a sleeping cat face with minimal UI.
9. **Tamagotchi-style Needs Display**: Add small visual meters for "Hunger" (needs networks) and "Boredom" (needs conversation).
10. **Hardware Button Bindings**: If the Waveshare HAT has physical buttons, map them to quick actions (e.g., Button 1 = Force Refresh, Button 2 = Sleep).

---

## 📡 Radio & Hardware Tactics (11-20)
11. **Auto-Channel Hopping Profiles**: Instead of random hopping, implement "targeted hopping" based on the most common channels in the environment.
12. **BLE Wardriving Map**: Save GPS coordinates (if tethered to phone) alongside BLE MAC addresses for a spatial map of Bluetooth devices.
13. **Karma/Rogue AP Mode**: A skill that spins up a mock Access Point to see what devices try to connect to it.
14. **Deauth Scaling**: Adjust deauth aggression based on CPU temperature to prevent thermal throttling on the Pi Zero 2W.
15. **Bluetooth PAN Auto-Reconnect**: A background watchdog that continuously tries to re-establish the tether with a specific iPhone MAC if connection drops.
16. **WPA3 Detection UI**: Specifically flag and log WPA3 networks on the UI with a distinct icon.
17. **PMKID Only Mode**: A silent hunting mode that only sniffs for PMKIDs instead of actively sending Deauths, drastically reducing the physical radio footprint.
18. **Network "Whitelisting"**: Prevent the Gotchi from ever targeting or sniffing specific home/friendly networks via a simple `gotchi network whitelist <SSID>` command.
19. **LED Status Indicators**: If an external LED is attached to a GPIO pin, blink it on handshake capture.
20. **Hardware Sleep Hook**: A plugin that cleanly shuts down the Pi if voltage drops below a critical safety threshold.

---

## 🧠 AI / "Soul" Behaviors (21-30)
21. **Multi-Bot Gossip Protocol**: Let two Gotchis in proximity exchange summaries of their daily `MEMORY.md` logs over BLE.
22. **Dynamic Tone Switching**: If the Gotchi captures 5 handshakes in an hour, switch `IDENTITY.md` to an "Aggressive/Proud" tone automatically.
23. **LLM Cost Tracker**: Log API token usage into the SQLite database and warn the user via Discord if daily limits are approaching.
24. **Context Summarization Hook**: Instead of letting the SQLite message buffer fill up, have the AI periodically summarize the last 20 messages into a single factual statement.
25. **Dream Sequences**: During long idle periods, use the LiteLLM to generate a random "thought" based on past memory and append it to the journal.
26. **Personality "Genes"**: Introduce a configuration where users can set sliders for (Curiosity, Aggression, Humor), which alters the LLM system prompt.
27. **Off-Grid AI Fallback**: If internet drops, switch to a tiny local model (if running on a Pi5) or just use pre-canned Python logic until internet returns.
28. **Sentiment Analysis Filtering**: Parse the AI's output for sentiment before printing it to the screen to ensure the chosen E-Ink face matches the text.
29. **Lore Generation Mode**: A command `gotchi generate_lore` where the AI writes a short story about its current location and targets.
30. **Automated Skill Writing**: Allow the AI to draft its own simple bash scripts in the `scratch/` folder and request user permission to promote them to `agents/skills/`.

---

## 💻 CLI & Developer Tooling (31-40)
31. **`gotchi backup`**: A single command that zips `workspace/`, `.env`, and `gotchi.db` for easy exporting.
32. **Web Dashboard Plugin**: A lightweight Flask/FastAPI server that streams the E-ink display buffer to a local webpage (`gotchi.local:8080`).
33. **Interactive `.env` Wizard**: A command `gotchi config init` that prompts the user in the terminal to securely input API keys and select hardware specs.
34. **Database Purge Tool**: `gotchi db clean --older-than 30d` to keep the SQLite database small on the SD card.
35. **Live Log Tailer**: `gotchi logs watch` with color-coded outputs for AI thoughts vs Hardware events.
36. **Plugin Scaffolding**: `gotchi plugin create <name>` to auto-generate a boilerplate `@hook` Python file.
37. **Mock Hardware Mode**: A startup flag that bypasses the E-ink and Radio drivers so developers can test the AI logic on a Macbook without a Pi.
38. **Skill Market CLI**: `gotchi skills search <keyword>` to look up community scripts on a central GitHub repo.
39. **Self-Update Mechanism**: A command `gotchi update` that runs `git pull`, checks requirements, and restarts the service.
40. **Health Check Output JSON**: Ensure `gotchi doctor` can output in JSON format for external monitoring tools.

---

## 🧩 External Integrations & Plugins (41-50)
41. **Telegram Bot Fallback**: If Discord is blocked, seamlessly transition chat handlers to Telegram.
42. **WPA-Sec Auto-Uploader**: A plugin that detects a new `.pcap` handshake, automatically uploads it to wpa-sec, and alerts the AI when it's cracked.
43. **HomeAssistant Integration**: Broadcast Gotchi status (battery, networks found) over MQTT to a smart home dashboard.
44. **Discord "Now Playing" Status**: Update the Discord Bot's presence to show "Pwning [Network Name]" or "Sleeping".
45. **Slack Webhook Alarms**: If a whitelisted network is attacked (Karma detection), fire a Slack webhook.
46. **Pwnagotchi Peer Compatibility**: Understand the original Pwnagotchi advertisement beacons to display other legacy bots on the screen.
47. **Kismet GPS Feed**: Pipe captured packets directly into a local Kismet instance running on the Pi.
48. **Twilio SMS Plugin**: For extreme critical alerts (e.g., battery dying, rogue AP detected), send a text to the owner.
49. **GitHub Issue Creator**: If the Python brain hits a fatal exception, automatically draft a GitHub issue in the repo using the AI brain to summarize the stack trace.
50. **Spotify "Mood" Plugin**: If tethered, the Gotchi can read what song the owner is playing on Spotify and change its face to match the tempo/vibe.