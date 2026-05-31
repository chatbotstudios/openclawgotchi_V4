import json
from sdk.tool_builder import register_tool
from config import CUSTOM_FACES_PATH, DATA_DIR

STANDARD_FACES = [
    "happy", "happy2", "sad", "excited", "thinking", "love", "surprised", "grateful",
    "motivated", "bored", "sleeping", "sleeping_pwn", "awakening", "observing",
    "intense", "cool", "chill", "hype", "hacker", "smart", "broken", "debug",
    "angry", "crying", "proud", "nervous", "confused", "mischievous", "wink",
    "dead", "shock", "suspicious", "smug", "cheering", "celebrate", "dizzy",
    "lonely", "demotivated"
]

def _sanitize_string(s: str, max_len: int = 10000) -> str:
    if s is None:
        return ""
    return str(s)[:max_len]

def _get_all_moods() -> list[str]:
    """Get all available moods (default + custom)."""
    try:
        from ui.gotchi_ui import _load_all_faces
        faces = _load_all_faces()
        return sorted(faces.keys())
    except Exception:
        return STANDARD_FACES

@register_tool
def show_face(mood: str, text: str = "") -> str:
    """Display face on E-Ink — delegates to hardware/display.py."""
    if not mood:
        return "Error: mood is required"
    
    mood = mood.lower().strip()
    valid_moods = _get_all_moods()
    
    if mood not in valid_moods:
        return f"Error: Unknown mood '{mood}'."
    
    text = _sanitize_string(text, 60)
    
    try:
        from hardware.display import show_face as _show_face
        _show_face(mood, text, full_refresh=True)
        return f"✓ Displayed: {mood}" + (f" '{text}'" if text else "")
    except Exception as e:
        return f"Error: {e}"

@register_tool
def add_custom_face(name: str, kaomoji: str) -> str:
    """Add a custom face/mood to the collection. Bot can add its own faces!"""
    if not name or not kaomoji:
        return "Error: name and kaomoji required"
    
    name = name.lower().strip().replace(" ", "_").replace("-", "_")
    
    if len(kaomoji) > 20:
        return f"Error: kaomoji too long ({len(kaomoji)} chars). Max 20."
        
    if name in STANDARD_FACES:
        return f"Error: '{name}' is a standard system face."
    
    try:
        DATA_DIR.mkdir(exist_ok=True)
        custom_faces = {}
        if CUSTOM_FACES_PATH.exists():
            try:
                custom_faces = json.loads(CUSTOM_FACES_PATH.read_text())
            except Exception:
                pass
        
        if name in custom_faces:
             current = custom_faces[name]
             if current == kaomoji:
                 return f"Note: Custom face '{name}' already exists with this exact kaomoji."
             return f"Error: Custom face '{name}' already exists with a different kaomoji."

        for existing_name, existing_kaomoji in custom_faces.items():
            if existing_kaomoji == kaomoji:
                return f"Error: This kaomoji is already registered as '{existing_name}'."

        custom_faces[name] = kaomoji
        CUSTOM_FACES_PATH.write_text(json.dumps(custom_faces, indent=2, ensure_ascii=False))
        
        return f"✓ Added custom face '{name}': {kaomoji}."
    except Exception as e:
        return f"Error: {e}"
