"""
game_engine/vitals.py — AIPET vitals & XP system.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Single source of truth for XP lives in `db/stats.py` (gotchi_stats SQLite table).
This module is the canonical entry point for all game-engine code — it proxies
all XP writes to db.stats and re-exports the read helpers so callers don't need
to know which module owns the data.

Architecture:
    All writes:  add_xp() → db.stats.add_xp() → gotchi_stats table
    All reads:   get_level_progress() → db.stats.get_level_progress()
    Mirror:      AIPET_STATE.json kept in sync for legacy readers
    Audit log:   aipet_vitals_log SQLite table (append-only, never read for level)
"""

import sqlite3
import logging
from datetime import datetime, timezone

from config import DB_PATH
from src.game_engine.state import load_state, save_state

# ── Re-export canonical read helpers so game-engine callers import from here ─
from db.stats import (                          # noqa: F401  (intentional re-exports)
    get_level_for_xp,
    get_level_progress,
    get_stats_summary,
    LEVEL_THRESHOLDS,
    LEVEL_TITLES,
    add_xp as _stats_add_xp,
)

log = logging.getLogger(__name__)


# ── HP calculation (hardware vitals — unrelated to XP) ───────────────────────

def calculate_hp(cpu: float, mem: float, uptime_hours: float, battery: float = 100.0) -> float:
    """Calculate the HP of the AIPET based on hardware vitals."""
    hp = (uptime_hours * 1.5) + ((100 - cpu) * 0.4) + ((100 - mem) * 0.3) + (battery * 0.2)
    return max(0.0, min(100.0, hp))


# ── Canonical XP write path ───────────────────────────────────────────────────

def add_xp(amount: int, source: str = "mission", event=None) -> int:
    """
    Award XP to the AIPET.

    Delegates to db.stats.add_xp() (canonical store), then:
      - Mirrors the new values into AIPET_STATE.json
      - Appends a row to the aipet_vitals_log audit table
      - Fires a level-up message/display if the level changed

    Returns the new total XP.
    """
    state = load_state()
    old_level = state.level

    # ── Write to canonical store ─────────────────────────────────────────────
    new_xp = _stats_add_xp(amount, reason=source)

    # ── Derive new level / title from canonical store ─────────────────────────
    prog = get_level_progress()
    new_level = prog["level"]
    new_title = prog["title"]

    # ── Mirror into AIPET_STATE.json ─────────────────────────────────────────
    state.xp          = new_xp
    state.level       = new_level
    state.title       = new_title          # requires models.py title field
    state.last_updated = datetime.now(timezone.utc).isoformat()
    save_state(state)

    # ── Level-up effects ─────────────────────────────────────────────────────
    if new_level > old_level:
        log.info(f"🎉 AIPET LEVELED UP → Level {new_level} ({new_title})")

        if event is not None:
            event.messages.append(
                f"🎉 **LEVEL UP!** Gotchi reached **Level {new_level}** — *{new_title}*! 🚀"
            )

        try:
            from hardware.display import show_face
            show_face(
                "excited",
                f"SAY:Level {new_level}! | STATUS: LEVEL UP",
                full_refresh=False,
            )
        except Exception as e:
            log.warning(f"Failed to flash E-paper on level up: {e}")

    # ── Append to audit log (never used for level reads) ─────────────────────
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.execute(
            """
            INSERT INTO aipet_vitals_log (timestamp, xp, hp, rp, level, source)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (state.last_updated, new_xp, state.hp, state.rp, new_level, source),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        log.error(f"Failed to log vitals to aipet_vitals_log: {e}")

    return new_xp


# ── Backward-compat shim — kept so any stale import of xp_to_reach_level works
def xp_to_reach_level(n: int) -> int:
    """
    DEPRECATED — use db.stats.LEVEL_THRESHOLDS instead.
    Returns the threshold from the canonical 20-level array.
    Kept only to avoid ImportError on stale callers; will be removed in v1.3.
    """
    if n < 1:
        return 0
    idx = min(n, len(LEVEL_THRESHOLDS)) - 1
    return LEVEL_THRESHOLDS[idx]
