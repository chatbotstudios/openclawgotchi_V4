"""Seed missions from progressive.json into the database."""
import json
import sqlite3
from pathlib import Path

DB_PATH = Path("/home/gotchi/openclawgotchi_V4/gotchi.db")
WORKSPACE_DIR = Path("/home/gotchi/openclawgotchi_V4/workspace")

conn = sqlite3.connect(str(DB_PATH))

# Init table
conn.execute("""
    CREATE TABLE IF NOT EXISTS missions (
        id TEXT PRIMARY KEY,
        title TEXT,
        description TEXT,
        category TEXT,
        tier TEXT,
        status TEXT DEFAULT 'available',
        progress INTEGER DEFAULT 0,
        target INTEGER,
        reward_xp INTEGER,
        trigger_event TEXT,
        actor TEXT DEFAULT 'any'
    )
""")

# Load progressive.json
prog_path = WORKSPACE_DIR / "missions" / "progressive.json"
with open(prog_path) as f:
    missions = json.load(f)

count = 0
for m in missions:
    name = m["name"]
    cat = m["category"]
    target = m["target"]
    xp = m["xp_reward"]  # key is xp_reward in JSON
    base = m.get("base_name", name)

    tier = "v1"
    if " v" in name:
        tier = "v" + name.split(" v")[1]

    mid = name.lower().replace(" ", "_").replace("'", "")

    conn.execute("""
        INSERT OR IGNORE INTO missions
        (id, title, description, category, tier, target, reward_xp, trigger_event, actor)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        mid,
        name,
        f"Complete {target} milestone(s) in {cat} category",
        cat.lower(),
        tier,
        target,
        xp,
        "auto",
        "any"
    ))
    count += 1

conn.commit()
conn.close()
print(f"Seeded {count} missions into the database!")
