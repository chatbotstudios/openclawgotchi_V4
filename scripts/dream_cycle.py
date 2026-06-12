#!/usr/bin/env python3
"""
Dream Cycle — Autonomous background dream + logging.
Scheduled via system cron. Self-cleaning after 10 cycles.
"""
import json
import sqlite3
import os
import sys
from datetime import datetime

DB_PATH = os.path.expanduser("~/openclawgotchi_V4/gotchi.db")
MEMORY_DIR = os.path.expanduser("~/openclawgotchi_V4/workspace/memory")
COUNTER_FILE = os.path.expanduser("~/openclawgotchi_V4/data/.dream_counter")
MAX_CYCLES = 10

def dream():
    if not os.path.exists(DB_PATH):
        print(f"[DREAM] DB not found at {DB_PATH}")
        return False

    # Read / increment cycle counter
    cycles = 0
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE) as f:
            try:
                cycles = int(f.read().strip())
            except:
                cycles = 0
    cycles += 1
    with open(COUNTER_FILE, "w") as f:
        f.write(str(cycles))

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT hp FROM aipet_state WHERE id = 1")
    row = cursor.fetchone()
    old_hp = row["hp"] if row else 0

    new_hp = min(100.0, old_hp + 5.0)
    cursor.execute("UPDATE aipet_state SET hp = ?, rp = 0.0 WHERE id = 1", (new_hp,))

    if old_hp < new_hp:
        cursor.execute("UPDATE aipet_state SET current_mood = 'dreaming' WHERE id = 1")

    conn.commit()

    today = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%H:%M")
    log_file = os.path.join(MEMORY_DIR, f"{today}.md")
    os.makedirs(MEMORY_DIR, exist_ok=True)

    entry = f"[{timestamp}] 🛏️ **Dream Cycle {cycles}/{MAX_CYCLES}:** HP {old_hp:.1f} → {new_hp:.1f} (+{new_hp - old_hp:.1f})"
    with open(log_file, "a") as f:
        f.write(f"{entry}\n")

    conn.close()
    print(f"[DREAM] Cycle {cycles}/{MAX_CYCLES} | HP: {old_hp:.1f} -> {new_hp:.1f}")

    # Self-clean after max cycles
    if cycles >= MAX_CYCLES:
        print(f"[DREAM] All {MAX_CYCLES} cycles complete. Removing cron entry.")
        os.system('crontab -l 2>/dev/null | grep -v dream_cycle | crontab -')
        os.remove(COUNTER_FILE)
        print("[DREAM] Cron cleaned up. Marathon finished!")

    return True

if __name__ == "__main__":
    success = dream()
    sys.exit(0 if success else 1)
