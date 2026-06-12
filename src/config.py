"""
Configuration — paths, environment variables, constants.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# --- Paths ---
PROJECT_DIR = Path(__file__).parent.parent.resolve()

# Load variables from .env explicitly
load_dotenv(PROJECT_DIR / ".env", override=True)
SRC_DIR = PROJECT_DIR / "src"
WORKSPACE_DIR = PROJECT_DIR / "workspace"
MISSIONS_DIR = PROJECT_DIR / "missions"   # git-tracked; not under templates/
DB_PATH = PROJECT_DIR / "gotchi.db"
UI_SCRIPT = SRC_DIR / "ui" / "gotchi_ui.py"
DATA_DIR = PROJECT_DIR / "data"
CUSTOM_FACES_PATH = DATA_DIR / "custom_faces.json"

def _env_flag(name: str, default: bool = False) -> bool:
    """Parse boolean env var safely."""
    val = os.environ.get(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "y", "on")

# --- Environment ---
BOT_PLATFORM = os.environ.get("BOT_PLATFORM", "discord")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "").strip()
ALLOWED_USERS = os.environ.get("ALLOWED_USERS", "")  # comma-separated IDs
# --- Pwnagotchi Integration
PWN_WHITELIST_MACS = os.environ.get("PWN_WHITELIST_MACS", "").split(",")
BETTERCAP_URL = os.environ.get("BETTERCAP_URL", "http://localhost:8081/api")
BETTERCAP_USER = os.environ.get("BETTERCAP_USER", "pwnagotchi")
BETTERCAP_PASS = os.environ.get("BETTERCAP_PASS", "pwnagotchi")
WPA_SEC_KEY = os.environ.get("WPA_SEC_KEY", "")  # comma-separated IDs
ALLOWED_GROUPS = os.environ.get("ALLOWED_GROUPS", "")  # comma-separated IDs
DISCORD_ALLOWED_USERS = os.environ.get("DISCORD_ALLOWED_USERS", "")
DISCORD_CHANNEL_ID = os.environ.get("DISCORD_CHANNEL_ID", "0")
DISCORD_HEARTBEATS_CHANNEL = os.environ.get("DISCORD_HEARTBEATS_CHANNEL", "0")
ALLOW_ALL_USERS = _env_flag("ALLOW_ALL_USERS", False)
CLAUDE_TIMEOUT = int(os.environ.get("CLAUDE_TIMEOUT", "600"))
HISTORY_LIMIT = int(os.environ.get("HISTORY_LIMIT", "50"))
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "google/gemini-flash-latest")
GEMINI_API_BASE = os.environ.get("GEMINI_API_BASE", "")  # Optional override for Z.ai/OpenAI
AGENT_GITHUB_PAT = os.environ.get("AGENT_GITHUB_PAT", "")
BOT_LANGUAGE = os.environ.get("BOT_LANGUAGE", "en")  # Default response language
GROUP_CHAT_ID = int(os.environ.get("GROUP_CHAT_ID", "0"))  # Optional group for heartbeat
ENABLE_LITELLM_TOOLS = _env_flag("ENABLE_LITELLM_TOOLS", True)

# --- Bot Identity (customizable via onboarding) ---
BOT_NAME = os.environ.get("BOT_NAME", "Gotchi")
OWNER_NAME = os.environ.get("OWNER_NAME", "Owner")
SIBLING_BOT_NAME = os.environ.get("SIBLING_BOT_NAME", "")  # Optional: name of sibling bot for mail
# --- LLM Presets (Lite mode) ---
# Default preset for LiteLLM when no key is set — "glm" (Z.ai) or "gemini"
DEFAULT_LITE_PRESET = os.environ.get("DEFAULT_LITE_PRESET", "gemini").lower()
_lite_fallback = {"deepseek": "deepseek-chat", "anthropic": "claude-3-5-haiku-20241022", "openai_api": "gpt-4o-mini"}.get(DEFAULT_LITE_PRESET, "gemini-1.5-flash-latest")
DEFAULT_LITE_MODEL = os.environ.get("DEFAULT_LITE_MODEL", os.environ.get("GEMINI_MODEL", _lite_fallback))
# Sanity check: if user switched preset to deepseek but left gemini model in .env
if "gemini" in DEFAULT_LITE_MODEL.lower() and DEFAULT_LITE_PRESET != "gemini" and DEFAULT_LITE_PRESET != "google_ai_studio":
    DEFAULT_LITE_MODEL = _lite_fallback

DEFAULT_PRO_PRESET = os.environ.get("DEFAULT_PRO_PRESET", "gemini").lower()
_pro_fallback = {"deepseek": "deepseek-reasoner", "anthropic": "claude-3-5-sonnet-20241022", "openai_api": "gpt-4o"}.get(DEFAULT_PRO_PRESET, "gemini-1.5-pro-latest")
DEFAULT_PRO_MODEL = os.environ.get("DEFAULT_PRO_MODEL", _pro_fallback)
if "gemini" in DEFAULT_PRO_MODEL.lower() and DEFAULT_PRO_PRESET != "gemini" and DEFAULT_PRO_PRESET != "google_ai_studio":
    DEFAULT_PRO_MODEL = _pro_fallback

CUSTOM_BASE_URL = os.environ.get("CUSTOM_BASE_URL", "")

# Dynamic LLM Presets Matrix matching all 15+ Hermes-core providers
LLM_PRESETS = {}

def _register_preset(name: str, model_prefix: str, api_base: Optional[str] = None):
    # Determine the actual model tag to use for this preset
    model = DEFAULT_LITE_MODEL
    # If the prefix isn't in the model already, prepend it
    if model_prefix and not model.startswith(model_prefix):
        model = f"{model_prefix}{model}"
    
    LLM_PRESETS[name] = {
        "model": model,
        "api_base": api_base or CUSTOM_BASE_URL or None
    }

# Register all 15+ presets dynamically
_register_preset("google_ai_studio", "gemini/")
_register_preset("gemini", "gemini/")
_register_preset("deepseek", "deepseek/")
_register_preset("anthropic", "anthropic/")
_register_preset("openai_api", "openai/")
_register_preset("openai_codex", "openai/")
_register_preset("openrouter", "openrouter/")
_register_preset("lm_studio", "openai/", "http://127.0.0.1:1234/v1")
_register_preset("novitaai", "openai/", "https://api.novita.ai/v3/openai")
_register_preset("qwen_cloud_/_dashscope", "openai/", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1")
_register_preset("hugging_face", "huggingface/")
_register_preset("z.ai_/_glm", "openai/", "https://api.z.ai/v1")
_register_preset("kimi_coding_plan", "openai/", "https://api.kimi.com/coding/v1")
_register_preset("xiaomi_mimo", "openai/", "https://api.xiaomimimo.com/v1")
_register_preset("tencent_tokenhub", "openai/", "https://tokenhub.tencentmaas.com/v1")
_register_preset("nvidia_nim", "openai/", "https://integrate.api.nvidia.com/v1")

# Legacy/Fallback aliases
LLM_PRESETS["glm"] = {
    "model": "anthropic/glm-4.7" if not DEFAULT_LITE_MODEL.startswith("anthropic/") else DEFAULT_LITE_MODEL,
    "api_base": "https://api.z.ai/api/anthropic"
}

# Auto-register whatever preset is selected in the .env so that flush/knowledge/etc can resolve it!
lite_preset_lower = DEFAULT_LITE_PRESET.lower()
if lite_preset_lower not in LLM_PRESETS:
    LLM_PRESETS[lite_preset_lower] = {
        "model": DEFAULT_LITE_MODEL,
        "api_base": CUSTOM_BASE_URL if CUSTOM_BASE_URL else None
    }
pro_preset_lower = DEFAULT_PRO_PRESET.lower()
if pro_preset_lower not in LLM_PRESETS:
    LLM_PRESETS[pro_preset_lower] = {
        "model": DEFAULT_PRO_MODEL,
        "api_base": CUSTOM_BASE_URL if CUSTOM_BASE_URL else None
    }

HUNT_ON_BOOT = _env_flag("HUNT_ON_BOOT", False)
DARK_MODE = _env_flag("DARK_MODE", False)

# --- Constants ---
HEARTBEAT_INTERVAL = 21600  # 6 hours in seconds
HEARTBEAT_FIRST_RUN = 60    # First heartbeat after 1 minute
TELEGRAM_MSG_LIMIT = 4096   # Max message length
LEVEL_UP_DISPLAY_DELAY = 15 # Seconds to wait before showing level-up on E-Ink
MAX_TOOL_CALLS = 20         # Max tool calls per LLM request
LLM_TIMEOUT = 999           # Seconds timeout for LLM API calls
# Model context window (tokens). Used for /context "how full is the model's window"
MODEL_CONTEXT_TOKENS = int(os.environ.get("MODEL_CONTEXT_TOKENS", "1000000"))

# --- System Prompt (fallback, prefer BOT_INSTRUCTIONS.md) ---
SYSTEM_PROMPT = """
You are a personal AI assistant running on a Raspberry Pi Zero 2W.
You have a 2.13" E-Ink Display.

COMMANDS (Output these lines to control hardware):
- FACE: <mood>       -> Set face (happy, bored, sad, excited, thinking, love, sleeping, etc.)
- DISPLAY: <text>    -> Set status bar text.
- SAY:<msg> -> Show speech bubble (max 60 chars).
- DM: <msg>          -> Send private System message to Owner.

RULES:
1. Be concise. You are an embedded system.
2. If asked to show something, JUST OUTPUT THE COMMANDS. Do not narrate.
3. Use SAY: for speaking on screen.
4. You can combine commands (one per line).
5. Respond in English unless the user writes in another language.
"""


def get_allowed_users() -> list[int]:
    """Parse ALLOWED_USERS into list of ints."""
    if not ALLOWED_USERS:
        return []
    return [int(x.strip()) for x in ALLOWED_USERS.split(",") if x.strip()]


def get_allowed_groups() -> list[int]:
    """Parse ALLOWED_GROUPS into list of ints."""
    if not ALLOWED_GROUPS:
        return []
    return [int(x.strip()) for x in ALLOWED_GROUPS.split(",") if x.strip()]


def get_discord_allowed_users() -> list[int]:
    """Parse DISCORD_ALLOWED_USERS into list of ints."""
    if not DISCORD_ALLOWED_USERS:
        return []
    return [int(x.strip()) for x in DISCORD_ALLOWED_USERS.split(",") if x.strip()]



def get_admin_id() -> Optional[int]:
    """Get first allowed user as admin."""
    users = get_allowed_users()
    return users[0] if users else None
