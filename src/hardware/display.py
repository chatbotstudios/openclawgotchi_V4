"""
E-Ink Display control — Pwnagotchi-style persistent daemon.
Holds the SPI bus open to allow smooth partial updates without flashing.
"""

import logging
import re
import threading
import time
import sys

from config import PROJECT_DIR

log = logging.getLogger(__name__)

# Ghosting & Reliability control
_display_update_count = 0
_consecutive_errors = 0
MAX_CONSECUTIVE_ERRORS = 3
FULL_REFRESH_EVERY = 100

# Global State
_current_mood = "happy"
_current_text = ""
_last_activity_time = time.time()
_animation_enabled = True
_qr_override_image = None

# Threading events
_state_changed_event = threading.Event()
_display_lock = threading.Lock()

# Global EPD hardware instance
_epd = None
_epd_initialized = False
_epd_driver = None

def _init_epd():
    global _epd, _epd_initialized, _epd_driver
    try:
        sys.path.append(str(PROJECT_DIR / "src" / "drivers"))
        import epd2in13_V4 as epd_driver
        _epd_driver = epd_driver
        _epd = epd_driver.EPD()
        _epd.init()
        _epd.Clear(0xFF)
        _epd_initialized = True
        log.info("E-Ink Display Daemon initialized natively.")
    except Exception as e:
        log.warning(f"Failed to load EPD driver (Simulator mode active): {e}")
        _epd_initialized = False

def _render_thread_loop():
    """Persistent background thread that draws the UI and sends partial updates."""
    global _display_update_count, _consecutive_errors, _epd_initialized
    
    _init_epd()
    
    # Import the UI renderer logic (now returning an image)
    from ui.gotchi_ui import generate_canvas
    
    first_frame = True
    
    while True:
        # Dynamic Timeout Logic (Phase 2)
        idle_time = time.time() - _last_activity_time
        
        if _current_mood in ["upload", "upload1", "upload2", "upload3", "calculating", "intense", "friend", "hyper", "pwn", "angry"]:
            sleep_interval = 3.0  # Hyper-active (fast breathing)
        elif _current_mood in ["sleep", "sleep2"] or idle_time > 60:
            sleep_interval = 60.0 # Deep sleep / extended idle
        else:
            sleep_interval = 6.0 # Normal idle breathing
            
        _state_changed_event.wait(timeout=sleep_interval)
        _state_changed_event.clear()
        
        with _display_lock:
            try:
                # Generate the PIL image using the legacy UI logic or QR override
                if _qr_override_image:
                    image = _qr_override_image
                else:
                    image = generate_canvas(mood=_current_mood, status_text=_current_text)
                
                # Canvas Hashing Optimization
                current_hash = hash(image.tobytes())
                if not first_frame and hasattr(_render_thread_loop, 'last_hash') and _render_thread_loop.last_hash == current_hash:
                    continue  # Skip SPI write if perfectly identical
                _render_thread_loop.last_hash = current_hash
                
                rotated = image.rotate(180)
                
                _display_update_count += 1
                needs_full = first_frame or (_display_update_count % FULL_REFRESH_EVERY == 0)
                
                if _epd_initialized:
                    if needs_full:
                        log.debug(f"🖥️  Display: FULL REFRESH (Cycle {_display_update_count})")
                        _epd.init()
                        try:
                            _epd.displayPartBaseImage(_epd.getbuffer(rotated))
                        except AttributeError:
                            _epd.display(_epd.getbuffer(rotated))
                        first_frame = False
                    else:
                        log.debug("🖥️  Display: PARTIAL REFRESH (Animation/Clock tick)")
                        try:
                            _epd.displayPartial(_epd.getbuffer(rotated))
                        except AttributeError:
                            # Fallback if driver doesn't expose displayPartial
                            _epd.display(_epd.getbuffer(rotated))
                    
                    # DO NOT call _epd.sleep() here, as it calls epdconfig.module_exit() 
                    # and completely shuts down the SPI/GPIO pins, crashing subsequent updates!
                else:
                    # Simulator
                    sim_path = PROJECT_DIR / "simulator.png"
                    image.save(sim_path)
                
                # Success - reset error count
                _consecutive_errors = 0

            except Exception as e:
                _consecutive_errors += 1
                log.error(f"Render Daemon error (Attempt {_consecutive_errors}): {e}")
                
                if _consecutive_errors >= MAX_CONSECUTIVE_ERRORS and _epd_initialized:
                    log.critical("🚨 E-Ink Hardware Circuit Breaker Triggered. Switching to Simulator Mode.")
                    _epd_initialized = False

def start_animation_daemon():
    """Start the adaptive hardware renderer daemon."""
    log.info("Starting Persistent E-Ink Renderer Daemon (Adaptive Mode)...")
    threading.Thread(target=_render_thread_loop, daemon=True, name="EinkRenderer").start()

def update_display(mood: str = None, text: str = None, full_refresh: bool = False, is_animation_tick: bool = False):
    global _current_mood, _current_text, _last_activity_time, _display_update_count
    
    if mood:
        _current_mood = mood
    if text is not None:
        _current_text = text
    
    if not is_animation_tick:
        _last_activity_time = time.time()
        log.info(f"Display update: mood={mood}, text={text}")
        
    if full_refresh:
        # Force next update to be full
        _display_update_count = FULL_REFRESH_EVERY - 1
        
    _state_changed_event.set()

def show_face(mood: str, text: str = "", full_refresh: bool = False):
    update_display(mood=mood, text=text, full_refresh=full_refresh)

def show_text(text: str):
    update_display(text=text)

def show_qr_code(ssid: str, passwd: str, mac: str = "", rssi: str = ""):
    global _qr_override_image
    try:
        from hardware.qr_display import generate_qr_image
        _qr_override_image = generate_qr_image(ssid, passwd, mac, rssi)
        _state_changed_event.set()
        log.info(f"Displaying QR code for {ssid}")
    except Exception as e:
        log.error(f"Failed to show QR code: {e}")

def hide_qr_code():
    global _qr_override_image
    _qr_override_image = None
    _state_changed_event.set()
    log.info("Hidden QR code")

def parse_and_execute_commands(response: str) -> tuple[str, dict]:
    lines = response.strip().splitlines()
    clean_lines = []
    commands = {"face": None, "display": None, "dm": None, "group": None, "mail": None}
    has_seen_command = False
    
    for line in lines:
        stripped = line.strip()
        if not stripped: continue
        
        is_command = False
        if stripped.upper().startswith(("FACE:", "DISPLAY:", "SAY:", "DM:", "GROUP:", "STATUS:", "REMEMBER:", "MAIL:")):
            is_command = True
        elif re.match(r"^\s*</?\w+>\s*$", stripped):
            is_command = True
            
        if is_command:
            has_seen_command = True
            if stripped.upper().startswith("FACE:"):
                mood = stripped[5:].strip().lower()
                commands["face"] = mood
                log.info(f"CMD FACE: {mood}")
            elif stripped.upper().startswith("DISPLAY:"):
                text = stripped[8:].strip()
                commands["display"] = text
                log.info(f"CMD DISPLAY: {text}")
            elif stripped.upper().startswith("SAY:"):
                text = stripped[4:].strip()
                commands["display"] = f"SAY:{text}"
                log.info(f"CMD SAY: {text}")
            elif stripped.upper().startswith("DM:"):
                commands["dm"] = stripped[3:].strip()
            elif stripped.upper().startswith("GROUP:"):
                commands["group"] = stripped[6:].strip()
            elif stripped.upper().startswith("STATUS:"):
                continue
            elif stripped.upper().startswith("REMEMBER:"):
                commands["remember"] = stripped[9:].strip()
            elif stripped.upper().startswith("MAIL:"):
                commands["mail"] = stripped[5:].strip()
                log.info(f"CMD MAIL: {commands['mail'][:50]}...")
        else:
            if has_seen_command:
                log.info("Detected second Gotchi block starting. Truncating response.")
                break
            clean_lines.append(stripped)
            
    if commands["face"] or commands["display"]:
        update_display(mood=commands["face"], text=commands["display"])
    
    return "\n".join(clean_lines), commands

def boot_screen():
    pass

def online_screen():
    pass

def error_screen(error_msg: str):
    err_lower = error_msg.lower()
    mood = "dead"
    short_error = "Error"
    jp_msg = "システムエラー発生"
    
    if "ratelimit" in err_lower or "quota" in err_lower:
        mood, short_error, jp_msg = "dizzy", "Quota Full", "レート制限超過!"
    elif "timeout" in err_lower or "connect" in err_lower:
        mood, short_error, jp_msg = "bored", "Timeout", "接続タイムアウト"
    elif "auth" in err_lower or "permission" in err_lower or "denied" in err_lower:
        mood, short_error, jp_msg = "suspicious", "Access Denied", "アクセス拒否!"
    elif "parse" in err_lower or "syntax" in err_lower or "value" in err_lower:
        mood, short_error, jp_msg = "confused", "Bad Syntax", "構文エラー発生"
    elif "llm" in err_lower:
        mood, short_error, jp_msg = "dizzy", "Brain Freeze", "処理不能エラー"

    code_prefix = ""
    code_match = re.search(r'"code":\s*(\d+)', error_msg) or re.search(r'status code:?\s*(\d+)', error_msg, re.IGNORECASE)
    if code_match: code_prefix = f"[{code_match.group(1)}] "
        
    update_display(mood=mood, text=f"SAY: {code_prefix}{jp_msg} | STATUS: ERR: {short_error}", full_refresh=True)

def get_current_face_ascii() -> str:
    """Returns the ASCII Kaomoji of the current hardware face."""
    from ui.faces import get_all_faces
    import random
    faces = get_all_faces()
    mood_faces = faces.get(_current_mood, faces.get("happy", ["(◕‿◕)"]))
    return random.choice(mood_faces) if isinstance(mood_faces, list) else mood_faces

