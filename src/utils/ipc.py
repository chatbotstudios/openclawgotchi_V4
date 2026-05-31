import os
import json
import time
import logging
from pathlib import Path
from typing import Any, Dict, Optional

log = logging.getLogger("IPC")

class DaemonStateManager:
    """
    Handles atomic JSON IPC between the AI (Conscious) and the Pwn Daemon (Subconscious).
    Uses os.rename to ensure thread-safe, process-safe updates on Linux.
    """
    def __init__(self, state_file: str = "/tmp/daemon_control.json"):
        self.state_file = Path(state_file)
        self._default_state = {
            "version": 1.0,
            "last_update": 0.0,
            "paused_until": 0.0,
            "target_lock": None,
            "mode": "automated",
            "whitelist_override": [],
            "hop_interval": 5
        }

    def get_state(self) -> Dict[str, Any]:
        """Read the current state, returning defaults if file is missing or invalid."""
        if not self.state_file.exists():
            return self._default_state.copy()
            
        try:
            with open(self.state_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            log.error(f"Failed to read IPC state: {e}")
            return self._default_state.copy()

    def set_state(self, new_state: Dict[str, Any]):
        """Write state atomicaly using a temp file and rename."""
        new_state["last_update"] = time.time()
        temp_file = self.state_file.with_suffix(".tmp")
        
        try:
            with open(temp_file, "w") as f:
                json.dump(new_state, f, indent=2)
            
            # Atomic rename (on Unix-like systems)
            os.rename(temp_file, self.state_file)
        except Exception as e:
            log.error(f"Atomic state update failed: {e}")
            if temp_file.exists():
                os.remove(temp_file)

    def update_key(self, key: str, value: Any):
        """Update a specific key in the state."""
        state = self.get_state()
        state[key] = value
        self.set_state(state)

    def is_paused(self) -> bool:
        """Check if the daemon should be currently paused."""
        state = self.get_state()
        return time.time() < state.get("paused_until", 0)

    def get_target_lock(self) -> Optional[str]:
        """Get the current BSSID target lock if any."""
        return self.get_state().get("target_lock")

# Global singleton for easy access
state_manager = DaemonStateManager()
