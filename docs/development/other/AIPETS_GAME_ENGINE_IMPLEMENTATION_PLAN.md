AIPET GAME ENGINE
AI-Ready Implementation Plan
For openclawgotchi_V4
Markdown# AIPET GAME ENGINE - Complete AI-Ready Implementation Plan

## 1. Overview & Goals

**Project Name**: AIPET Game Engine  
**Goal**: Add a clean, simple, gamified progression system to openclawgotchi_V4 so the AI agent feels alive, grows, and has purpose.

**Core Vitals** (keep extremely simple):
- **XP** (Experience Points) — Earned from completing missions, tasks, bounties, milestones, and daily activity.
- **HP** (Health Points) — Derived from device health (uptime, CPU load, memory, battery, temperature).
- **RP** (Reputation Points) — Earned from successful swarm/mesh communication and data sharing quality.

**Evolution System**:
- Pure **Level 1–100** system (no animal themes).
- Leveling is the only form of "evolution".
- Exact XP thresholds defined below.

**Mission/Bounty System**:
- User-injected or autonomously self-generated.
- Missions are the primary way to earn XP.

---

## 2. Core Data Model

### File: `workspace/AIPET_STATE.json`
```json
{
  "level": 1,
  "xp": 0,
  "hp": 85.0,
  "rp": 12.5,
  "last_updated": "2026-05-31T12:19:00Z",
  "missions_completed": 47,
  "badges": ["First_Handshake", "Uptime_Champion"],
  "current_mood": "focused"
}
Database Extension (SQLite)
Add these tables to the existing database:
SQLCREATE TABLE aipet_vitals_log (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    xp INTEGER,
    hp REAL,
    rp REAL,
    level INTEGER,
    source TEXT
);

CREATE TABLE aipet_missions (
    id INTEGER PRIMARY KEY,
    name TEXT,
    category TEXT,
    xp_reward INTEGER,
    status TEXT,           -- pending, active, completed, failed
    completed_at TEXT,
    source TEXT            -- user, auto, bounty
);

3. Leveling System (Exact Rules)
Level Requirements (cumulative XP needed to reach that level):























































LevelXP Required to ReachNotes10Starting level2100-3200-......-101000-1111000Big jump1212000-......-1001,000,000Max level
Formula for levels 1–10:
Pythondef xp_to_reach_level(n: int) -> int:
    if n <= 10:
        return n * 100
    else:
        return 1000 + (n - 10) * 1000   # Simplified progressive scaling
Level-up Logic:

When current_xp >= xp_to_reach_level(current_level + 1) → Level up + trigger celebration (E-Ink + journal entry).

4. Vitals Formulas (Simplified)
XP Formula
Pythonxp_gain = base_reward * efficiency_multiplier + bonus
HP Formula (Health)
Pythonhp = clamp(
    (uptime_hours * 2) + 
    (100 - cpu_percent) * 0.5 + 
    (100 - mem_percent) * 0.3 + 
    battery_percent * 0.2,
    0, 100
)
RP Formula (Reputation)
Pythonrp = (successful_mesh_shares * 2) + (data_accuracy_score * 5) - (failed_shares * 3)

5. Mission Categories & Examples
Mission Categories

CategoryDescriptionExample MissionsCortexAI / LLM / Reasoning tasksCortex_Calibration, Dream_Session, Skill_HallucinationRadioWiFi / Bluetooth / Bettercap activityRadio_Collector, Handshake_Harvest, BLE_SweepUptimeDevice health & stabilityUptime_Resilience, Power_Manager, Temperature_StableSocialMesh / Swarm / CommunicationSocial_Sync, Neural_Exchange, Swarm_CoordinationExplorationDiscovery & mappingNetwork_Mapper, IoT_Scout, New_SSID_FinderBountyUser-injected or high-value tasksCustom_Bounty, Alpha_ChallengeMaintenanceSystem care & optimizationMemory_Clean, Git_Sync, Log_Archive
Example Missions (Ready to Use)
PythonMISSIONS = {
    "cortex_calibration": {
        "name": "Cortex Calibration",
        "category": "Cortex",
        "xp_reward": 150,
        "description": "Run 3 successful LLM reasoning tasks with high confidence",
        "auto_trigger": True
    },
    "radio_collector": {
        "name": "Radio Collector",
        "category": "Radio",
        "xp_reward": 80,
        "description": "Capture 10 new WPA handshakes in one session",
        "auto_trigger": True
    },
    "uptime_resilience": {
        "name": "Uptime Resilience",
        "category": "Uptime",
        "xp_reward": 120,
        "description": "Maintain >95% uptime for 24 hours",
        "auto_trigger": False
    },
    "social_sync": {
        "name": "Social Sync",
        "category": "Social",
        "xp_reward": 200,
        "description": "Successfully exchange data with 2+ other AIPETs",
        "auto_trigger": True
    },
    "dream_session": {
        "name": "Dream Session",
        "category": "Cortex",
        "xp_reward": 60,
        "description": "Enter boredom state and generate 3 synthetic scenarios",
        "auto_trigger": True
    }
}

6. New File Structure
Bashsrc/game_engine/
├── __init__.py
├── models.py              # Pydantic models
├── vitals.py              # HP, XP, RP calculation + leveling
├── missions.py            # Mission engine + bounty system
├── state.py               # AIPET_STATE.json manager
├── hooks.py               # Integration with existing @hook system
├── ui.py                  # E-Ink mood + Rich dashboard updates
└── cli.py                 # New `gotchi aipet` commands

7. Core Code Skeletons (AI-Ready)
src/game_engine/models.py
Pythonfrom pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AIPETState(BaseModel):
    level: int = 1
    xp: int = 0
    hp: float = 100.0
    rp: float = 0.0
    last_updated: datetime
    missions_completed: int = 0
    badges: List[str] = []
    current_mood: str = "neutral"
src/game_engine/vitals.py (Core Engine)
Pythondef calculate_hp(cpu: float, mem: float, uptime: float, battery: float) -> float:
    hp = (uptime * 1.5) + ((100 - cpu) * 0.4) + ((100 - mem) * 0.3) + (battery * 0.2)
    return max(0.0, min(100.0, hp))

def add_xp(amount: int, source: str = "mission") -> int:
    # Load state, add XP, check for level up, save state
    ...

def level_up() -> bool:
    # Check thresholds and trigger level-up logic
    ...

8. Integration Points with openclawgotchi_V4

Bettercap hooks → Auto award XP on handshake capture
LiteLLM calls → Award XP for successful reasoning tasks
E-Ink hardware → Mood faces change based on HP + Level
Existing memory system → Log every XP/HP/RP change in episodic journals
CLI → Add gotchi aipet status, gotchi aipet mission list, gotchi aipet dream


9. Phased Implementation Roadmap (Simple)
Phase 1 (Week 1): Core Vitals + Leveling + AIPET_STATE.json
Phase 2 (Week 2): Mission Engine + 6 starter missions
Phase 3 (Week 3): E-Ink mood integration + Rich dashboard
Phase 4 (Week 4): Auto mission generation (boredom/dream loop) + RP mesh scoring

10. CLI Commands (New)
Bashgotchi aipet status          # Show level, XP, HP, RP + mood
gotchi aipet mission list    # Show available + active missions
gotchi aipet dream           # Manually trigger dream session
gotchi aipet inject "Secure my home network"   # User bounty

This plan is 100% ready for direct implementation.