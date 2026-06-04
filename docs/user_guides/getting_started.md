# Getting Started with OpenClawGotchi V3

Welcome to OpenClawGotchi V3! This guide will walk you through the initial setup, boot sequence, and basic interactions with your new tactical document-driven agent.

## Hardware & Software Requirements

Before you begin, ensure you have the following:

### Hardware Requirements
- **Raspberry Pi Zero 2W** (Highly recommended for optimal balance of power and size)
- **Waveshare E-Ink Display** (Specifically the 2.13-inch V4 variant)
- **MicroSD Card** (8GB or larger, high quality like SanDisk Extreme)
- **Power Supply** (5V/2A minimum, or a high-quality battery pack like a PiSugar)
- **Optional but recommended**: A case that fits the Pi and screen.

### Software Requirements
- **OS**: Raspberry Pi OS (Legacy/Buster or Bullseye Lite recommended for stability)
- **Python**: Python 3.9+
- **OpenClawGotchi V3 Repository**: Cloned to `/home/pi/openclawgotchi`

## Setup Process

1. **Flash your SD Card**: Install Raspberry Pi OS Lite.
2. **Clone the Repo**: SSH into your Pi and clone the repo.
   ```bash
   git clone https://github.com/yourusername/openclawgotchi_V4.git
   cd openclawgotchi_V4
   ```
3. **Run the Setup Script**: The provided setup wizard will install dependencies and configure the environment.
   ```bash
   ./setup.sh
   ```
4. **Configure**: Copy `.env.example` to `.env` and fill in your keys (like OpenAI/Anthropic/Gemini API keys, Discord tokens, etc.).

## Initial Boot Sequence

When you power on the OpenClawGotchi, here is what happens:
1. **OS Boot**: The Raspberry Pi boots up (~30-40 seconds).
2. **Service Start**: The `gotchi` service starts automatically.
3. **E-Ink Initialization**: The screen clears and displays a boot logo or initialization text. Note that E-Ink screens take 2-3 seconds to fully refresh.
4. **Heartbeat**: The Python "Body" starts the heartbeat, ensuring the background tasks are running.
5. **AI "Soul" Awakening**: The LLM brain loads its personality from `workspace/SOUL.md` and begins reasoning about its environment.

## Understanding the E-Ink Screen

The E-Ink display is the primary visual interface for OpenClawGotchi.
- **Faces**: The "Gotchi" face changes dynamically based on its mood, which is determined by the AI brain.
- **Status Bar**: Usually shows WiFi status, Bluetooth status, and battery (if hardware is supported).
- **Activity Log**: Recent actions, like handshakes captured or thoughts the AI is having.

## Basic Interactions

- **The Unified Tactical CLI**: The easiest way to interact is via SSH using the `gotchi` command.
  - Try: `gotchi pwn status` or `gotchi ui refresh`
- **Discord/Chat**: If configured, you can interact with the AI brain directly via chat platforms.
- **Auto-Pwn**: If enabled, the device will automatically start sniffing and capturing handshakes without intervention.
- **Offline Timed Missions**: Trigger offline hunts (e.g., *"Go offline and hunt for 15 minutes"*). The Gotchi will automatically invert the E-Ink screen to Dark Mode, decouple from the LLM endpoint, run a Bettercap sweep, and restore connectivity and original UI settings afterward to report the captured handshakes.

Enjoy your new OpenClawGotchi!
