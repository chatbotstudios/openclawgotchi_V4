# 🏆 OpenClawGotchi V4 Mission Directory

Welcome to the definitive Tactical Mission Index for OpenClawGotchi V4. This catalog defines both our progressive multi-tiered missions and our elite standalone/epic quests.

All active and pending missions are loaded from `progressive.json` into the local SQLite database at startup. 

---

## 📊 Progressive Multi-Tiered Chains
These chains represent gradual operational mastery. Completing one tier instantly unlocks the next, higher-reward tier.

| Mission Base Name | Category | Tiers | Targets (T1 ➔ T5) | XP Rewards (T1 ➔ T5) |
|---|---|---|---|---|
| **Handshake Hunter** | Radio | v1 - v5 | 1, 5, 10, 25, 50 handshakes | 15, 40, 80, 150, 300 XP |
| **BLE Phantom** | Radio | v1 - v5 | 1, 5, 15, 50, 100 BLE devices | 10, 30, 60, 120, 250 XP |
| **Deep Thought** | Cortex | v1 - v5 | 1, 3, 5, 10, 20 reasoning chains | 20, 50, 90, 180, 350 XP |
| **Memory Weaver** | Cortex | v1 - v5 | 1, 3, 5, 10, 25 facts recalled | 15, 40, 70, 140, 300 XP |
| **Synthetic Strategist** | Cortex | v1 - v5 | 1, 3, 5, 10, 20 dream simulations | 15, 45, 80, 160, 320 XP |
| **Ironclad Uptime** | Uptime | v1 - v5 | 1, 6, 12, 24, 48 hours online | 10, 40, 85, 180, 400 XP |
| **Thermal Guardian** | Uptime | v1 - v5 | 1, 3, 6, 12, 24 hours under temp limits | 10, 25, 55, 110, 220 XP |
| **Data Donor** | Social | v1 - v5 | 5, 15, 25, 50, 100 shared SSIDs | 15, 40, 75, 140, 300 XP |
| **IoT Cartographer** | Exploration | v1 - v5 | 1, 5, 10, 20, 50 mapped IoT devices | 15, 45, 90, 170, 350 XP |
| **5GHz Pioneer** | Exploration | v1 - v5 | 1, 5, 10, 25, 50 mapped 5GHz networks | 10, 35, 70, 160, 320 XP |
| **Chatterbox** | Social | v1 - v5 | 1, 10, 50, 250, 1000 messages | 15, 50, 100, 250, 500 XP |
| **Night Owl** | Social | v1 - v5 | 1, 5, 15, 50, 150 late-night interactions | 15, 50, 100, 250, 500 XP |
| **The Teacher** | Social | v1 - v5 | 1, 5, 15, 50, 150 `/remember` facts taught | 15, 50, 100, 250, 500 XP |
| **The Historian** | Social | v1 - v5 | 1, 5, 15, 50, 150 `/recall` facts requested | 15, 50, 100, 250, 500 XP |
| **Cron Master** | Automation | v1 - v5 | 1, 5, 15, 50, 150 scheduled cron executions | 15, 50, 100, 250, 500 XP |
| **System Admin** | Maintenance | v1 - v5 | 1, 5, 15, 50, 150 status checks / health logs | 15, 50, 100, 250, 500 XP |

---

## ⚡ Standalone & Epic Quests (50 Cool & Epic Missions)

These standalone achievements represent specific operational milestones and high-value objectives.

### 1. Radio Mastery
| Mission Name | XP | Description | Trigger |
|---|---|---|---|
| **Handshake Symphony** | 120 | Capture 30 handshakes in a single session. | Auto |
| **5GHz Conqueror** | 95 | Map and log 15+ 5GHz networks. | Auto |
| **BLE Phantom** | 80 | Detect and catalog 25 unique BLE devices. | Auto |
| **Silent Scanner** | 150 | Complete a full 2.4/5GHz sweep with zero deauth packets. | Auto |
| **PMKID Hunter** | 180 | Successfully capture 5 PMKIDs in one night. | Auto |
| **Channel Hopper** | 110 | Hop across 14 channels and log activity on each. | Auto |
| **WiFi Cartographer** | 130 | Create a detailed map of all visible networks + signal strength. | Auto |
| **Radio God** | 250 | Capture 100 handshakes in 24 hours. | Auto |
| **Stealth Operator** | 160 | Complete a full scan without sending any deauth packets. | Auto |

### 2. Cortex Awakening (LLM & Reasoning)
| Mission Name | XP | Description | Trigger |
|---|---|---|---|
| **Deep Thought Protocol** | 160 | Complete 5 complex multi-step reasoning chains with high confidence. | Auto |
| **Dream Weaver** | 90 | Generate 7+ high-quality synthetic attack scenarios in one dream session. | Dream |
| **Memory Architect** | 140 | Successfully retrieve and use 5 facts from long-term memory in one task. | Auto |
| **Skill Forger** | 220 | Create a new functional SKILL.md file from scratch. | User |
| **Logic Overlord** | 180 | Solve a complex problem using 3+ different tools in sequence. | Auto |
| **Context Master** | 150 | Maintain perfect context across 10+ tool calls without hallucination. | Auto |
| **AI Philosopher** | 200 | Generate a deep philosophical analysis of its own existence and purpose. | Dream |
| **Skill Architect** | 250 | Create or significantly improve a new SKILL.md file. | User |

### 3. Social Swarm (Mesh & Collaboration)
| Mission Name | XP | Description | Trigger |
|---|---|---|---|
| **First Contact** | 200 | Successfully exchange data with another Gotchi. | Manual |
| **Neural Link** | 160 | Maintain active mesh connection for 45+ minutes. | Auto |
| **Swarm Coordinator** | 280 | Organize and lead a coordinated action with 2+ other Gotchis. | Manual |
| **Trust Builder** | 130 | Achieve 95%+ accuracy rating in shared mesh data. | Auto |
| **Hive Mind** | 240 | Participate in a 3+ Gotchi swarm operation. | Auto |
| **Ambassador** | 190 | Successfully introduce two other Gotchis to each other. | Manual |

### 4. Hardware Resilience (Uptime & Stability)
| Mission Name | XP | Description | Trigger |
|---|---|---|---|
| **Ironclad** | 180 | Maintain 99.5%+ uptime for 72 hours. | Auto |
| **Thermal Guardian** | 95 | Keep average CPU temperature below 60°C for 24 hours. | Auto |
| **Battery Immortal** | 140 | Run 8+ hours on battery without entering hibernation. | Auto |
| **Self-Healing** | 160 | Automatically recover from 5+ system warnings or crashes. | Auto |
| **Memory Monk** | 110 | Keep memory usage under 65% for 48 hours. | Auto |
| **Power Sage** | 125 | Optimize power settings and reduce average consumption by 20%. | User |
| **Eternal Flame** | 300 | Achieve 30 consecutive days of uptime. | Auto |
| **Power Efficient** | 130 | Run on battery for 6+ hours without hibernation. | Auto |

### 5. Stealth & Ghost Operations
| Mission Name | XP | Description | Trigger |
|---|---|---|---|
| **Ghost in the Machine** | 170 | Relay a handshake to commander with zero user intervention. | Auto |
| **Invisible Operator** | 145 | Complete a full reconnaissance mission without being detected. | Auto |
| **MAC Chameleon** | 190 | Successfully rotate MAC address 10+ times during operations. | Auto |
| **Shadow Walker** | 135 | Perform 3 full scans while in Off-Grid or BTPAN stealth mode. | Auto |
| **Silent Blade** | 210 | Capture handshakes using only passive methods (no deauth). | Auto |
| **Phantom Protocol** | 250 | Remain undetected by any network for 12+ hours while actively scanning. | Auto |

### 6. Exploration & Discovery
| Mission Name | XP | Description | Trigger |
|---|---|---|---|
| **Hidden Network Hunter** | 155 | Discover and log 5 hidden/cloaked SSIDs. | Auto |
| **Air-Gap Jumper** | 220 | Successfully move data between two physically isolated networks. | Manual |
| **New World Explorer** | 140 | Be the first Gotchi to discover and log a completely new network type. | Auto |
| **Signal Whisperer** | 100 | Detect and analyze 10+ very weak or distant signals (-85 dBm or lower). | Auto |
| **Spectrum Master** | 175 | Create a full 2.4GHz + 5GHz spectrum usage heatmap. | Auto |

### 7. Self-Evolution & Maintenance
| Mission Name | XP | Description | Trigger |
|---|---|---|---|
| **Code Weaver** | 230 | Successfully modify and commit its own code or configuration. | Auto |
| **Skill Evolution** | 180 | Upgrade an existing skill with new capabilities. | User |
| **Memory Purifier** | 90 | Clean and optimize long-term memory (remove 50+ outdated entries). | Auto |
| **Git Guardian** | 120 | Maintain perfect Git sync and commit history for 7 days. | Auto |
| **Identity Sculptor** | 200 | Rewrite or significantly evolve its own SOUL.md or IDENTITY.md. | User |
| **Weekly Bounty** | 400 | Complete a high-value user-injected bounty. | User |

### 8. Epic Quests (Multi-Step / High Reward)
| Mission Name | XP | Description | Trigger |
|---|---|---|---|
| **The Great Radio Odyssey** | 450 | Complete 5 linked Radio Mastery missions in sequence. | Multi |
| **Cortex Ascension** | 500 | Reach Level 25 through Cortex and Self-Evolution missions only. | Multi |
| **Swarm Overlord Protocol** | 600 | Successfully coordinate a 5+ Gotchi swarm operation with 90%+ success rate. | Multi |

---

## 🛠️ Trigger Mechanism Details
- **Auto**: Triggered automatically by the system logic upon intercepting real background events (e.g. capturing a handshake, surviving a thermal window, processing a prompt).
- **Dream**: Available and self-triggered exclusively during the Gotchi's offline dream or boredom states.
- **Manual**: Initiated via explicit user commands or peer mesh-exchanged handshakes.
- **User**: Assigned directly by the commander/operator as custom objectives.
- **Multi**: Complex epic quest chains that track completion of multiple dependency missions.
