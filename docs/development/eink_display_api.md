# E-Ink Display API & UI Rendering

The visual interface of OpenClawGotchi V3 is rendered on a Waveshare E-Ink Display HAT (supporting v3 and v4 models, generally the 2.13-inch variants). 

Because E-Ink screens have extremely slow refresh rates (~2-3 seconds for a full update) and are prone to ghosting with partial refreshes, the UI architecture is built around a decoupled "state" loop rather than direct synchronous draw calls.

## 1. The UI Rendering Loop (`src/ui/gotchi_ui.py`)

The `gotchi_ui.py` file is the heart of the visual system. It does not control the physical screen directly; instead, it generates a `PIL` (Python Imaging Library) Image object.

### The State Dictionary
The UI renderer relies on a globally accessible state dictionary that holds the current values for:
- `face`: The string identifier for the current facial expression (e.g., `"(>_<)"`).
- `status`: A short string indicating current action (e.g., `"PWNING"`, `"SLEEPING"`).
- `wifi_count`: Number of networks in range.
- `handshakes`: Total handshakes captured this session.
- `message`: The bottom log line (e.g., the last thought the AI had).

### The Render Cycle
1. **Gather Data**: The loop reads the latest values from the state dictionary.
2. **Draw Base**: It clears the canvas and draws the layout grid (status bar at top, face in middle, log at bottom).
3. **Inject Dynamic Content**: It uses PIL's `ImageDraw` to write the specific text and symbols.
4. **Push Buffer**: It hands the final PIL Image to `src/hardware/display.py`, which executes the SPI commands to refresh the Waveshare screen.

## 2. Supported E-Ink Models

By default, the code targets the 2.13-inch Waveshare HATs. 
- **Waveshare HAT v3 / v4**: Supported natively. You configure the specific driver in the `.env` file (`DISPLAY_MODEL=epd2in13_V4` or `epd2in13_V3`).
- The V4 generally offers slightly faster partial refresh rates, but the driver logic in `src/drivers/` abstracts these differences away from the UI code.

## 3. Adding New "Faces"

The agent's "face" is simply ASCII art rendered using a monospace font (or specifically tailored TrueType fonts loaded by PIL).

To add a new face:
1. Open `src/ui/faces.py` (or the face mapping section in `gotchi_ui.py`).
2. Add your new ASCII sequence to the `FACES` dictionary.

```python
FACES = {
    "happy": "( ^_^ )",
    "sad": "( ;_; )",
    "pawning": "( ⌐■_■)",
    "angry": "( >_< )",
    # Add yours here
    "confused": "( o_O )",
    "surprised": "( O_O )"
}
```

3. **Triggering the Face**: The AI "Soul" updates its mood by editing its `IDENTITY.md` or emitting an event. The Python core parses this mood and updates the UI state dictionary `state['face'] = FACES['confused']`.

## 4. Best Practices for UI Updates

- **Do not block**: Never write a plugin that calls `display.refresh()` synchronously. It will freeze the entire bot heartbeat.
- **Batch Updates**: If multiple things happen at once, update the state dictionary, and let the natural UI tick (usually every 10-30 seconds) handle the visual refresh.
