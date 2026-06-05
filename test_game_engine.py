import sys
from pathlib import Path

# Add src dir to path
src_dir = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(src_dir))

from game_engine.state import load_state, save_state
from game_engine.vitals import calculate_hp, add_xp, regenerate_hp_on_sleep, decay_mood

print("Loading state...")
state = load_state()
print(f"Level: {state.level}, HP: {state.hp}, Mood: {state.current_mood}")

print("Testing HP decay...")
new_hp = calculate_hp(cpu=50.0, mem=50.0, uptime_hours=100.0, battery=50.0)
print(f"Calculated HP (should be exhausted): {new_hp}")

print("Testing sleep HP regen...")
regenerate_hp_on_sleep(hours=8.0)
state = load_state()
print(f"HP after sleep: {state.hp}")

print("Testing mood decay...")
decay_mood()

print("All tests passed!")
