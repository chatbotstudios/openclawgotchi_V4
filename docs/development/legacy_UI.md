# Legacy E-Ink UI Layout Reference

This document serves as a historical reference for the original `openclawgotchi_V3` E-Ink interface layout prior to the Phase 3 Game Engine Gamification overhaul.

## Interface Analysis (`simulator.png`)
The legacy layout adhered to a rigid, three-row grid system on a `250x122` pixel monochrome e-paper display.

### 1. Header Row
The top row was dedicated to bot identity and raw hardware telemetry.

### 2. Main Body (Center)
The central area handled physical expression and status communication.
- **Center-Left**: `( ▢ ‿‿ ▢ )` The Kaomoji Face. This reacted to raw hardware events (e.g., sweating if Temp > 65C). *(Note: The square eyes in the simulator indicated missing unicode glyphs for the `◕` character on the host OS).*
- **Center-Right**: `Ready to roll!` The speech/status bubble. This text wrapped automatically based on the width of the rendered face.

### 3. Footer Row
The bottom row tracked basic progression and time.
- A solid 1px horizontal black line separated this row from the body.
- **Bottom-Left**: `Lv1` The static bot level tracker.
- **Bottom-Right**: `UP 02:00:46 | 03:15`
  - `UP`: Continuous System Uptime.
  - `03:15`: Current local time.

## Transition to Phase 3
To inject Game Engine metrics without visual clutter, this legacy layout will be modified as follows:
1. Hardware telemetry strings will be condensed (removing `%`, `C`, `MB`) to fit the new `HP: 100%` metric in the header.
2. The `Lv1` string will be expanded to include the calculated Rank (e.g., `Lv1 Novice`).
3. The raw Uptime metric will be replaced with real-time `Mission Progress` trackers, as uptime is now mathematically abstracted into the `HP` metric.
