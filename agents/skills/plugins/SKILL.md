# SKILL: PLUGINS
# Author: OpenClaw Architecture
# Version: 1.0.0

# DESCRIPTION
Allows the bot to manage, develop, and interact with its own event-driven plugin system. 

# USAGE
The bot can now write custom Python logic into the `/plugins` directory to extend its hardware and software capabilities without modifying the core source code.

# CORE EVENTS
- `startup`: Triggered when the bot finishes initialization.
- `pwn.event`: Triggered for EVERY raw event from Bettercap.
- `pwn.handshake`: Triggered specifically when a valid WPA handshake is captured.
- `pwn.peer`: Triggered when another ClawGotchi/Pwnagotchi is detected.
- `message`: Triggered when a message is received (Discord/Telegram).
- `heartbeat`: Triggered during the periodic system check.

# PLUGIN TEMPLATE
```python
from hooks.runner import hook, HookEvent

@hook("pwn.handshake")
def my_custom_logic(event: HookEvent):
    # event.data contains the Bettercap payload
    pass
```

# STORAGE
Plugins are stored in the root `/plugins` directory for global access.
