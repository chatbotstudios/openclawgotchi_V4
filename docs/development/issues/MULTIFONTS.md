# Issue: Multi-Font & CJK Character Rendering on E-Ink Displays

## Overview
When the OpenClawGotchi AI "Soul" dynamically generates or selects a face (e.g., `(￣▽￣)〜`), users may notice that certain characters do not render correctly on the Waveshare E-Ink display. Instead of the intended character, the screen displays a missing character glyph, often appearing as an empty rectangle, question mark, or glitch (commonly referred to as "tofu").

## Root Cause
The Python "Body" uses the **Python Imaging Library (PIL/Pillow)** to draw text onto a canvas before pushing the image buffer to the E-Ink display via SPI. 

PIL requires a `.ttf` (TrueType) or `.ttc` (TrueType Collection) font file to render text. By default, `src/ui/gotchi_ui.py` attempts to load:
1. `/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf`
2. MacOS specific fallback fonts (e.g., `Menlo.ttc` or `Arial Unicode.ttf`)

If these fonts are not found on the Raspberry Pi, PIL falls back to `ImageFont.load_default()`, which is a highly primitive 8x11 pixel bitmap font that **only supports basic ASCII**. 

Even if `DejaVuSansMono` *is* installed, it is optimized for Latin code/terminal environments and lacks extensive coverage for **CJK (Chinese, Japanese, Korean)** characters or advanced Unicode symbols like the full-width Wave Dash (`〜`, U+301C).

## Solutions

Depending on how you want to handle the AI's creativity, there are three primary ways to resolve this issue.

---

### Solution 1: Install a Comprehensive CJK Font (Recommended)
If you want the Gotchi to express complex Japanese Kaomoji natively, you must install a font package that supports CJK glyphs and update the UI code to prioritize it.

**Step 1: Install Noto Fonts on the Pi**
SSH into your Raspberry Pi and run:
```bash
sudo apt update
sudo apt install fonts-noto-cjk
```

**Step 2: Update the Python Rendering Engine**
Edit `src/ui/gotchi_ui.py`. Locate the `face_paths` list and prepend the path to the newly installed Noto font:

```python
    face_paths = [
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', # Add this line!
        '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',
        '/Library/Fonts/Arial Unicode.ttf'
    ]
```
*Note: Font installation paths can sometimes vary by OS version. If the above path fails, you can find the exact location by running `find /usr/share/fonts -name "*NotoSansCJK*" ` on your Pi.*

**Step 3: Restart the Service**
```bash
sudo systemctl restart gotchi
```

---

### Solution 2: Output Sanitization (The Safe Fallback)
If you don't want to mess with fonts and want to guarantee the rendering loop never crashes or draws "tofu," you can sanitize the AI's output before it hits the PIL draw function.

In `src/ui/gotchi_ui.py`, before `face_str` is drawn onto the canvas, apply a regex filter to strip out non-ASCII/Extended Latin characters:

```python
import re

# ... inside the draw loop ...
# Strip anything that isn't basic ASCII or a few safe shapes (▲▼►◄▽△■□)
safe_face_str = re.sub(r'[^\x00-\x7F▲▼►◄▽△■□]+', '', raw_face_str)

draw.text((face_x, face_y), safe_face_str, font=font_face, fill=fg_color)
```
This forces the UI to gracefully degrade to standard characters.

---

### Solution 3: Restrict the AI Prompt
The AI appends characters like `〜` because LLMs naturally attempt to add conversational flair to Kaomojis. You can use the Document-Driven Architecture to forbid this behavior.

Open `workspace/SOUL.md` and navigate to the `## Presentation Protocol` section. Add the following strict rule:

> **[CRITICAL] Face Integrity:** You must use the EXACT string from your face catalog. Do not add trailing characters, modifiers (like `〜` or `~`), or emojis. The hardware display will crash if you deviate from the catalog.
