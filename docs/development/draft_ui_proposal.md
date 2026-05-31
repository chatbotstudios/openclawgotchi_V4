# E-Ink UI Draft Proposal

### 1. Header Row
The top row is dedicated to bot identity and essential connectivity/telemetry.

- **Top-Left (Identity & Connectivity)**: 
  - `Gotchi>` (The bot's name)
  - **WIFI Icon**: `▂▄▆█` (Full 4-bar signal)' where `▂▄▆_` (3-bar signal / slight drop), `▂▄__` (2-bar signal / weak), `▂___` (1-bar signal / very weak), `✖` (Offline)
  - **Bluetooth Icon**:
  `ᛒ` (BLE ON)
  `✖` (BLE OFF)
  `ᛒ»` (Bluetooth broadcasting/sending/scanning etc)
  `«ᛒ»` (Bluetooth discoverable field)
  `ᛒ✓` (Paired/Pairing successful)
  `ᛒ✕` (Pairing failed /disconnected)
 
  - *Example*: `Gotchi> ▂▄▆_ ᛒ`

- **Top-Right (Telemetry & HP)**: 
  - Condensed system stats and Game Engine HP.
  - *Example*: `HP:100% C:9 T:45 M:123MB`




*** 2. EXTRAS**
  **HP Symbol & Stats**: `HP♥100` | `HP♡49`
  **RP Symbol & Stats**: `RP✦100`
  
### 3. Footer Row
The bottom row tracke LVL progression, XP and time.
- A solid 1px horizontal black line separated this row from the body.
- **Bottom-Left**: `Lv1` The static bot level tracker.
- **Bottom-Center**:`XP [■■■■□□□□□□] 400/1K` essentially a progresss bar which tracks XP progress for the current Level.
- **Bottom-Right**: `UP 02:00:46 | 23:59`
  - `UP`: Continuous System Uptime.
  - `23:59`: Current local time.