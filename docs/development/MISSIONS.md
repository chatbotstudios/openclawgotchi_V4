# OpenClawGotchi V3: Mission & Quest System Implementation Plan

## 1. Feature Goals & Value
**Purpose**: The Mission/Quest system transforms the OpenClawGotchi V3 from a passive logging tool into an engaging, gamified tactical companion. By assigning specific objectives, it guides users to explore the hardware's capabilities, encourages consistent interaction with the LLM "Soul", and provides a structured way to learn wireless auditing.
**Value**: 
- **Retention**: Gamification loop (Action -> Reward -> Progression).
- **Education**: Missions act as an interactive tutorial for networking and security concepts.
- **Identity**: Reinforces the "Cyber-Pet" persona.

## 2. Mission Types & Categories
### Categories
1. **Daily**: Quick, easy tasks resetting every 24h (e.g., "Take a 10-minute power nap").
2. **Tactical**: Pentesting & network auditing (e.g., "Capture 5 handshakes").
3. **Exploration**: Wardriving and discovering new APs (e.g., "Map 10 unique networks").
4. **Learning & Soul**: Interacting with the AI (e.g., "Have a 5-minute therapy session").
5. **Stealth**: Evasion and defensive tasks (e.g., "Rotate MAC 10 times in one session").

### Difficulty Tiers
- **Rookie** (10-50 XP): Simple, low-effort.
- **Agent** (100-250 XP): Requires specific tool usage or moderate time.
- **Elite** (500-1000 XP): Complex, multi-step, or requires travel.
- **Legendary** (Custom Badges): Extremely rare or difficult achievements.

## 3. User Interface & Commands
The interface will be accessible via the `gotchi missions` command group.

```bash
# List all active and available missions
gotchi missions list [--category tactical] [--status active]

# Accept a new mission from the available pool
gotchi missions accept <mission_id>

# Generate a new random or themed mission via LLM
gotchi missions generate [--theme stealth]

# Check progress on active missions
gotchi missions progress

# View completed missions and rewards history
gotchi missions history
```
**Interactive TUI Mode**: Running `gotchi missions` without arguments will launch a `rich`-based dashboard displaying active quests with ASCII progress bars.

## 4. Data Model & Storage
Missions will be stored in the existing SQLite database (`gotchi.db`) to ensure atomic updates and portability.

**Table `missions`**:
- `id` (TEXT, PK): UUID or slug (e.g., `daily_handshake_1`).
- `title` (TEXT): "Capture 3 Handshakes"
- `description` (TEXT): Flavor text and requirements.
- `category` (TEXT): 'tactical', 'daily', etc.
- `tier` (TEXT): 'rookie', 'elite'.
- `status` (TEXT): 'available', 'active', 'completed', 'abandoned'.
- `progress` (INTEGER): Current count.
- `target` (INTEGER): Target count (e.g., 3).
- `reward_xp` (INTEGER): XP payload on completion.
- `actor` (TEXT): Determines who can execute the mission ('gotchi', 'human', 'any').

## 5. Rewards System
Completing missions directly influences both the Python Body and LLM Soul:
- **XP / Leveling**: Added to `stats.db`. Higher levels unlock Pro LLM features or advanced UI themes.
- **Mood Boost**: Triggers the `pulse_buddy` UI to celebrate, physically changing the E-Ink display to a happy state.
- **Discord Broadcast**: Synchronously pushes a rich notification to the `DISCORD_HEARTBEATS_CHANNEL` via REST API so all feats are logged socially.
- **Memory Injection**: Completed "Elite" missions are injected into the core LLM context as permanent "Lore/Memories".
- **Hardware Unlocks**: Specific missions could unlock new Custom Faces.

## 6. Technical Architecture
**Folder Structure**:
```text
src/
└── core/
    └── missions/
        ├── __init__.py
        ├── manager.py       # CRUD operations for SQLite missions table
        ├── models.py        # Pydantic/Dataclass definitions
        ├── rewards.py       # Logic for dispensing XP and mood changes
        ├── generator.py     # LLM integration for dynamic quest creation
        └── listeners.py     # Event hooks for auto-progressing tasks
```

**Integration Points**:
- **Python Body**: `listeners.py` will subscribe to Bettercap events (e.g., `wifi.handshake.captured`) and increment the progress of any active handshake missions.
- **LLM Brain**: The `generator.py` uses LiteLLM to dynamically spin up flavor text for quests based on the user's current location or recent DB history.

## 7. Execution & Autonomy (Hybrid Model)
The system employs a dual-execution strategy using the **Actor** model:

1. **User-Selected (Human)**: The human uses the CLI to browse the list and accept physical or location-based missions (e.g., Wardriving).
2. **Autonomous (Gotchi)**: The LLM Brain is provided native Python tools (`list_available_missions`, `accept_mission`). During a `heartbeat` cronjob or idle time, Gotchi can autonomously query the database and decide to accept and execute its own maintenance or background networking tasks.
3. **Co-op (Any)**: Either party can initiate the task.

**Dynamic Generation**: When the user runs `gotchi missions generate`, the LLM receives the static JSON blueprints as examples and outputs a novel JSON schema.

## 8. Progress Tracking & Events
We will utilize the existing `@hook` decorator architecture.
Example:
```python
@hook("on_handshake")
def track_handshake_mission(event_data):
    active_missions = db.get_active_missions(type="handshake")
    for m in active_missions:
        m.progress += 1
        if m.progress >= m.target:
            trigger_completion(m)
        db.save(m)
```

## 9. Implementation Phases
- **Phase 1**: Database schema (`missions` table) and core CLI commands (`list`, `accept`, `abandon`).
- **Phase 2**: Static JSON mission blueprints and simple manual progression.
- **Phase 3**: Event hooks for automatic tracking (Handshakes, Bluetooth pings, Uptime).
- **Phase 4**: Rewards integration (XP, Mood, E-Ink UI alerts).
- **Phase 5**: LLM Dynamic Generation and Interactive TUI Dashboard.

## 10. Performance & Edge Considerations
- **SQLite Locking**: Update mission progress asynchronously or use WAL mode to prevent `OperationalError` when the Bettercap thread and LLM thread clash.
- **Memory Footprint**: The mission hooks must be `O(1)` or fast `O(N)`. Iterating through 5 active missions on a handshake event takes negligible CPU cycles, perfectly safe for the Pi Zero 2W.

## 11. Extensibility
Community developers can drop `.json` mission packs into the `workspace/missions/` directory. The `manager.py` will ingest these on boot, instantly expanding the game world without touching Python code.

## 12. Challenges & Mitigations
- **Challenge**: Spamming/Cheating (e.g., user runs `wifi.deauth` repeatedly on their own network to farm XP).
  **Mitigation**: Implement a 24-hour cooldown on repeatable quests and cap daily XP from specific categories.
- **Challenge**: LLM generating impossible missions.
  **Mitigation**: Force the LLM to output Pydantic-validated JSON adhering to strict `target` bounds and supported `action_types` only.
