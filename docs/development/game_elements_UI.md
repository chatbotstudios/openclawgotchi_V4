# Game Elements UI Dictionary

This document catalogs the gamification metrics, states, and symbols that can be rendered on the `openclawgotchi_V4` E-Ink Display and Web Dashboard. Because of the monochrome, pixelated nature of the E-Ink hardware, we rely heavily on Unicode symbols, brackets, and ASCII art to convey game states cleanly.

---

## 1. Core Vitals & Progression

### Health Points (HP)
Reflects the physical hardware health (Temp, RAM, Uptime, Battery) translated into a game metric.
*   **Text Format**: `HP: 100%` | `HP: 45%`
*   **Mini Bar**: `[████░]` (80%) | `[██░░░]` (40%) | `[░░░░░]` (0%)
*   **Micro Bar**: `■■■■□`
*   **Symbol**: `♥ 100` | `♡ 15`

### Level & XP
Tracks the evolutionary stage of the AIPET.
*   **Standard**: `Lv 4` | `Level: 12`
*   **With Rank**: `Lv4 Novice` | `Lv10 Alpha-Claw`
*   **XP Tracker**: `XP: 450/1k` | `XP: 8.5k/10k`
*   **XP Bar**: `[▓▓▓▓▓▓░░░░]` (60% to next level)

---

## 2. Mission & Quest Mechanics

### Active Missions
Displays the current progressive tier being tackled by the AIPET.
*   **Short Form**: `M: H_Hunt 14/25` (Handshake Hunter)
*   **Micro Form**: `🎯 14/25`
*   **Target Bar**: `[███░░]` (3/5 Complete)

### Streaks & Bounties
*   **Bounty Active**: `! BOUNTY !` or `☠️ Target Acquired`
*   **Combo/Streak**: `Combo: x2` | `🔥 x3`

---

## 3. Mood & Behavioral States

### Dynamic Kaomoji (Driven by HP)
The face is the primary emotional indicator, directly linked to the HP stat.
*   **HP > 80 (Happy)**: `( ◕‿‿◕ )` | `( ✧ω✧ )`
*   **HP 50-79 (Cool)**: `( ⌐■_■ )` | `( ಠ_ಠ )`
*   **HP 20-49 (Nervous)**: `( º_º )` | `( 땀_땀 )`
*   **HP < 20 (Sick)**: `( ✖_✖ )` | `( ㅠ_ㅠ )`

### Activity Tags
Indicates what the background engine is currently executing.
*   `[HUNTING]` - Actively scanning or deauthing.
*   `[DREAMING]` - Boredom loop triggered; generating synthetic XP.
*   `[RESTING]` - High uptime, minimal network activity.
*   `[MAPPING]` - Discovering IoT devices.

---

## 4. Swarm & Mesh Intelligence (Phase 5)

*   **Peer Count**: `Peers: 3` | `🛰️ 3`
*   **Alpha Status**: If this node has the highest level in the local mesh, it gains the crown: `♔ Lv10` or `★ Alpha`
*   **Radio War**: `War: +45 XP` | `⚔️ Winning`

---

## 5. Hardware-Linked "Buffs"

*   **Thermal Buff (Cool CPU)**: `❄️ Cold Buff` (Bonus XP Gain)
*   **Endurance Badge (High Uptime)**: `🔋 Ironclad`
*   **Overclocked (High CPU Load)**: `⚡ Overdrive`

---

## UI implementation Strategy (Alternating Footer)

To prevent screen clutter on the `250x122` E-Ink display, the footer string can alternate every 5-10 seconds to cycle through this rich dataset:

*   **Tick A**: `Lv5 Alpha-Claw | [████░] 80%`
*   **Tick B**: `M: H_Hunt 14/25 | XP: 450/1k`
*   **Tick C**: `Peers: 0 | [HUNTING]`
