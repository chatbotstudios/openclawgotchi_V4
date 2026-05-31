#!/usr/bin/env python3
"""
OpenClawGotchi UI Renderer
Pwnagotchi-style component grid layout with pure vector fonts.
"""

import os
import json
import datetime
import textwrap
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import sys

UI_DIR = Path(__file__).parent.resolve()
SRC_DIR = UI_DIR.parent
PROJECT_DIR = SRC_DIR.parent

try:
    from config import BOT_NAME
except ImportError:
    BOT_NAME = os.environ.get("BOT_NAME", "Gotchi")

try:
    from db.stats import get_level_progress
except ImportError:
    def get_level_progress():
        return {"level": 1, "title": "Bot", "xp": 0, "xp_in_level": 0, "xp_needed_this_level": 100, "max_level": 20}

def get_system_stats():
    stats = {'load': 0, 'temp': '?', 'mem_avail': '?', 'cpu': '?', 'uptime': '?'}
    try:
        # Load average (Works on most Unix)
        stats['load'] = os.getloadavg()[0]
        
        # Temperature
        try:
            import subprocess
            if sys.platform == "linux":
                try:
                    temp = subprocess.check_output(["vcgencmd", "measure_temp"], text=True, timeout=1).strip()
                    stats['temp'] = temp.replace("temp=", "").replace("'C", "")
                except:
                    with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                        stats['temp'] = f"{int(f.read().strip()) / 1000:.1f}"
        except:
            pass
            
        # Memory
        try:
            import psutil
            mem = psutil.virtual_memory()
            stats['mem_avail'] = int(mem.available / (1024 * 1024))
            stats['mem_total'] = int(mem.total / (1024 * 1024))
        except ImportError:
            try:
                import subprocess
                if sys.platform == "linux":
                    mem_out = subprocess.check_output(["free", "-m"], text=True, timeout=1).splitlines()[1].split()
                    stats['mem_avail'] = mem_out[6] 
                    stats['mem_total'] = mem_out[1]
            except:
                pass
            
        # CPU Usage
        try:
            import psutil
            stats['cpu'] = int(psutil.cpu_percent(interval=None))
        except ImportError:
            try:
                import subprocess
                if sys.platform == "linux":
                    cpu_out = subprocess.check_output("top -bn1 | grep -i 'Cpu(s)'", shell=True, text=True, timeout=1)
                    idle = float(cpu_out.split('id,')[0].split(',')[-1].strip().split()[0])
                    stats['cpu'] = int(100.0 - idle)
            except:
                pass
            
        # Uptime
        try:
            if sys.platform == "linux":
                with open('/proc/uptime', 'r') as f:
                    uptime_seconds = float(f.readline().split()[0])
            else:
                import psutil
                import time
                uptime_seconds = time.time() - psutil.boot_time()
                
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            mins = int((uptime_seconds % 3600) // 60)
            if days > 0:
                stats['uptime'] = f"{days:02d}:{hours:02d}:{mins:02d}"
            else:
                stats['uptime'] = f"{hours:02d}:{mins:02d}"
        except:
            pass
    except Exception:
        pass
    return stats

def _load_all_faces() -> dict:
    try:
        from ui.faces import DEFAULT_FACES as default_faces
    except ImportError:
        default_faces = {"happy": "(◕‿‿◕)"}
    custom_faces = {}
    try:
        from config import CUSTOM_FACES_PATH
        if CUSTOM_FACES_PATH.exists():
            custom_faces = json.loads(CUSTOM_FACES_PATH.read_text())
    except Exception:
        pass
    return {**default_faces, **custom_faces}

_animation_tick = 0

def generate_canvas(mood="happy", status_text="") -> Image:
    stats = get_system_stats()
    
    # Check Dark Mode (Live Toggle)
    from dotenv import load_dotenv
    load_dotenv(PROJECT_DIR / ".env", override=True)
    is_dark = os.environ.get("DARK_MODE", "0") == "1"
    
    bg_color = 0 if is_dark else 255
    fg_color = 255 if is_dark else 0
    
    WIDTH, HEIGHT = 250, 122
    image = Image.new('1', (WIDTH, HEIGHT), bg_color)
    draw = ImageDraw.Draw(image)
    
    is_mac = sys.platform == "darwin"
    
    font_base_paths = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
        '/usr/share/fonts/dejavu/DejaVuSansMono.ttf',
        '/System/Library/Fonts/Menlo.ttc'
    ]
    font_base_path = next((p for p in font_base_paths if os.path.exists(p)), None)

    face_paths = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',
        '/Library/Fonts/Arial Unicode.ttf'
    ]
    face_path = next((p for p in face_paths if os.path.exists(p)), font_base_path)

    try:
        if not font_base_path: raise FileNotFoundError("No DejaVu base font found.")
        font_ui = ImageFont.truetype(font_base_path, 10)
        font_text = ImageFont.truetype(font_base_path, 12)
        font_bold = ImageFont.truetype(font_base_path, 10)
        font_face = ImageFont.truetype(face_path, 26)
    except Exception as e:
        import logging
        logging.error(f"UI Font Loading Failed (Falling back to tiny default font): {e}")
        font_ui = font_text = font_face = font_bold = ImageFont.load_default()

    HEADER_H = 15
    FOOTER_H = 15
    
    # ----------------------------------------------------
    # HEADER (y: 0 to 15)
    # ----------------------------------------------------
    mode_tag = " [L]" if "MODE: L" in status_text else " [P]" if "MODE: P" in status_text else ""
    
    # WIFI & BLE Icons (Mocked for now, can be hooked to actual net stats later)
    # ▂▃▅ is our 3-bar signal, ᛒ)) is our BLE broadcasting icon
    left_header = f"{BOT_NAME}>{mode_tag}  ▂▃▅ ᛒ))"
    draw.text((2, 1), left_header, font=font_bold, fill=fg_color)
    
    # Condensed Stats: C:9 T:45 M:1.7G
    mem_g = round(stats.get('mem_avail', 0) / 1024, 1) if isinstance(stats.get('mem_avail'), int) else "?"
    txt_stats = f"C:{stats['cpu']} T:{stats['temp']} M:{mem_g}G"
    
    bbox = draw.textbbox((0, 0), txt_stats, font=font_ui)
    draw.text((WIDTH - (bbox[2] - bbox[0]) - 2, 2), txt_stats, font=font_ui, fill=fg_color)
    
    draw.line((0, HEADER_H, WIDTH, HEADER_H), fill=fg_color)

    # ----------------------------------------------------
    # EXTRAS (y: 92)
    # ----------------------------------------------------
    try:
        from src.game_engine.state import load_state
        state = load_state()
        extras_str = f"HP♥{int(state.hp)}  RP♦0"
    except Exception:
        extras_str = "HP♥?  RP♦0"
        
    extras_bbox = draw.textbbox((0, 0), extras_str, font=font_ui)
    draw.text((WIDTH - (extras_bbox[2] - extras_bbox[0]) - 2, HEIGHT - FOOTER_H - 14), extras_str, font=font_ui, fill=fg_color)

    # ----------------------------------------------------
    # FOOTER (y: 107 to 122)
    # ----------------------------------------------------
    draw.line((0, HEIGHT - FOOTER_H, WIDTH, HEIGHT - FOOTER_H), fill=fg_color)
    
    try:
        from src.game_engine.state import load_state
        from src.game_engine.vitals import xp_to_reach_level
        state = load_state()
        lv_str = f"Lv{state.level}"
        
        xp_base = xp_to_reach_level(state.level) if state.level > 1 else 0
        xp_needed_total = xp_to_reach_level(state.level + 1)
        xp_in_level = state.xp - xp_base
        xp_needed_this_level = xp_needed_total - xp_base
        
        percent = xp_in_level / xp_needed_this_level if xp_needed_this_level > 0 else 0
        blocks = min(10, int(percent * 10))
        bar_str = f"[{'■'*blocks}{'□'*(10-blocks)}]"
        
        def format_xp(val):
            return f"{val//1000}K" if val >= 1000 else str(val)
            
        xp_str = f"XP{bar_str}{format_xp(xp_in_level)}/{format_xp(xp_needed_this_level)}"
    except Exception as e:
        lv_str = "Lv1"
        xp_str = "XP[□□□□□□□□□□]?/?"

    # Left Anchor (LvX)
    draw.text((2, HEIGHT - FOOTER_H + 2), lv_str, font=font_ui, fill=fg_color)
    lv_bbox = draw.textbbox((0, 0), lv_str, font=font_ui)
    lv_width = lv_bbox[2] - lv_bbox[0]
    
    # Right Anchor (Uptime/Time)
    now = datetime.datetime.now().strftime("%H:%M")
    uptime = f"{stats['uptime']}" if stats['uptime'] != '?' else ""
    footer_right = f"{uptime} | {now}" if uptime else now
    fr_bbox = draw.textbbox((0, 0), footer_right, font=font_ui)
    fr_width = fr_bbox[2] - fr_bbox[0]
    draw.text((WIDTH - fr_width - 2, HEIGHT - FOOTER_H + 2), footer_right, font=font_ui, fill=fg_color)
    
    # Center Anchor (XP Bar) placed right after LvX
    draw.text((2 + lv_width + 5, HEIGHT - FOOTER_H + 2), xp_str, font=font_ui, fill=fg_color)

    # ----------------------------------------------------
    # BODY (y: 16 to 106)
    # ----------------------------------------------------
    speech_text = None
    if "SAY:" in status_text:
        parts = status_text.split("| STATUS:") if "| STATUS:" in status_text else status_text.split("STATUS:") if "STATUS:" in status_text else [status_text, ""]
        speech_text = parts[0].replace("SAY:", "").strip()
    elif status_text:
        speech_text = status_text

    if not speech_text:
        speech_text = "Idle."

    global _animation_tick
    _animation_tick += 1
    
    faces = _load_all_faces()
    face_val = faces.get(mood, faces.get('happy', "(◕‿‿◕)"))
    
    if isinstance(face_val, list) and len(face_val) > 0:
        current_frame_index = _animation_tick % len(face_val)
        face_str = face_val[current_frame_index]
    else:
        face_str = face_val
    
    # Measure face
    bbox_face = draw.textbbox((0, 0), face_str, font=font_face)
    face_w = bbox_face[2] - bbox_face[0]
    face_h = bbox_face[3] - bbox_face[1]
    
    # Anchor face to the middle-left side
    face_x = 5
    face_y = HEADER_H + ((HEIGHT - HEADER_H - FOOTER_H) // 2) - (face_h // 2) - 5
    
    draw.text((face_x, face_y), face_str, font=font_face, fill=fg_color)

    # Draw Word-Wrapped Status Text on the Right
    status_x = face_x + face_w + 10
    max_text_width = WIDTH - status_x - 5
    
    if max_text_width < 50:
        # If the face is way too wide (e.g. giant custom kaomoji), force it to wrap under the face
        status_x = 5
        status_y = face_y + face_h + 5
        max_text_width = WIDTH - 10
    else:
        status_y = HEADER_H + 10
        
    # Calculate average char width to approximate wrap length
    test_char_bbox = draw.textbbox((0,0), "A", font=font_text)
    char_w = test_char_bbox[2] - test_char_bbox[0]
    chars_per_line = max(10, int(max_text_width / char_w))
    
    wrapped_lines = textwrap.wrap(speech_text, width=chars_per_line)
    
    curr_y = status_y
    for line in wrapped_lines[:6]:  # Size 12 allows for around 6 lines
        draw.text((status_x, curr_y), line, font=font_text, fill=fg_color)
        curr_y += 14

    return image
