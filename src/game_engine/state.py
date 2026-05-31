import json
import logging
from pathlib import Path
from config import WORKSPACE_DIR
from src.game_engine.models import AIPETState

log = logging.getLogger(__name__)

STATE_FILE = WORKSPACE_DIR / "AIPET_STATE.json"

def load_state() -> AIPETState:
    """Loads the AIPET state from the workspace JSON file."""
    if not STATE_FILE.exists():
        log.info("AIPET_STATE.json not found. Generating default state.")
        default_state = AIPETState()
        save_state(default_state)
        return default_state

    try:
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
        return AIPETState(**data)
    except Exception as e:
        log.error(f"Failed to load AIPET state: {e}. Returning default state.")
        return AIPETState()

def save_state(state: AIPETState) -> bool:
    """Saves the AIPET state to the workspace JSON file."""
    try:
        # Pydantic v2 support
        if hasattr(state, "model_dump_json"):
            data_str = state.model_dump_json(indent=2)
        else:
            data_str = state.json(indent=2)
            
        with open(STATE_FILE, "w") as f:
            f.write(data_str)
        return True
    except Exception as e:
        log.error(f"Failed to save AIPET state: {e}")
        return False
