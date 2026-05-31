# Configuration Guide

OpenClawGotchi V3 is designed to be highly configurable without requiring you to edit the underlying Python code. Most core settings are managed via the `.env` file located in the root of the project.

## Modifying the `.env` File

The `.env` file is loaded every time the `gotchi` service starts. 

> [!WARNING]
> Never commit your `.env` file to version control. It contains sensitive API keys and tokens.

To edit the file, SSH into your device and run:
```bash
nano /home/pi/openclawgotchi/.env
```

### Key Configuration Sections

#### LLM & AI Settings
- `LLM_PROVIDER`: e.g., `gemini`, `openai`, `anthropic`. Determines which router to use.
- `LLM_MODEL`: The specific model (e.g., `gemini-1.5-flash` for speed, `gpt-4o` for logic).
- `API_KEY_*`: Your respective API keys.

#### Hardware Settings
- `DISPLAY_MODEL`: The exact model of your Waveshare screen (e.g., `epd2in13_V4`).
- `UI_REFRESH_RATE`: How often the screen should update (in seconds). Keep this high (e.g., `30` or `60`) to avoid ghosting and battery drain.

#### Network & Pwning
- `AUTO_PWN_ENABLED`: `true` or `false`. If true, the Python brain will automatically start scanning and capturing handshakes on boot.
- `MONITOR_INTERFACE`: Usually `wlan0` or `mon0`.

#### Discord Integration
- `DISCORD_TOKEN`: If you want the bot to connect to a Discord server.
- `ALLOWED_CHANNEL_IDS`: Comma-separated list of channels the bot is allowed to speak in.

## Applying Changes

After making changes to the `.env` file, save your changes (`Ctrl+O`, `Enter`, `Ctrl+X` in nano), and restart the service to apply them:

```bash
sudo systemctl restart gotchi
```

You can check if the new configuration loaded correctly by viewing the logs:
```bash
journalctl -u gotchi -f
```
