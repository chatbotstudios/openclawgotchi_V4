# Plugin Development Guide

> For AI Agents and Developers writing Python plugins for the "Body" (Python layer).

OpenClawGotchi uses an event-driven architecture. Plugins allow you to execute Python code in response to specific system events (e.g., boot, handshake capture, low battery) without modifying core files.

## 1. The `@hook` System

Plugins are located in the `plugins/` directory. The core system discovers and loads them automatically on boot.

A plugin uses the `@hook` decorator to subscribe to an event string.

### Available Core Events
- `system.startup`
- `system.shutdown`
- `pwn.handshake_captured`
- `hardware.low_battery`
- `ui.refresh`

## 2. Generating a Plugin

When an AI is instructed to create a new plugin, follow this template:

```python
# plugins/my_custom_plugin.py

import logging
from src.core.events import hook  # Assumes standard event router location

logger = logging.getLogger(__name__)

@hook("pwn.handshake_captured")
def on_handshake(event_data):
    """
    Triggered whenever the Python layer captures a WPA handshake.
    event_data is a dict containing details like 'bssid', 'essid', 'file_path'.
    """
    essid = event_data.get("essid", "Unknown")
    logger.info(f"[Custom Plugin] We got a handshake for {essid}!")
    
    # Example: You could update an LED, send a custom API request, or 
    # write to a specific workspace memory file here.
```

## 3. Rules for Plugins

1. **Non-Blocking**: The Python brain heartbeat runs continuously. If your plugin does heavy IO (network requests, large file reads), you **must** use `asyncio.create_task` or run it in a separate thread. Synchronous blocks will crash the UI and the heartbeat.
2. **Error Handling**: Wrap plugin logic in `try/except` blocks. A failing plugin should log an error, not crash the main `gotchi` service.
3. **No Direct UI Rendering**: Do not try to write directly to the E-Ink display from a plugin. Instead, emit a new event or update the SQLite database, and let the `gotchi_ui.py` loop pick up the state change.
