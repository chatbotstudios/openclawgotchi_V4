import sqlite3
import logging
from config import DB_PATH

log = logging.getLogger(__name__)

def init_aipet_tables():
    """Initialize AIPET Game Engine SQLite tables."""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        
        # Vitals log table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS aipet_vitals_log (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                xp INTEGER,
                hp REAL,
                rp REAL,
                level INTEGER,
                source TEXT
            )
        ''')
        
        # Missions log/bounty table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS aipet_missions (
                id INTEGER PRIMARY KEY,
                name TEXT,
                category TEXT,
                xp_reward INTEGER,
                status TEXT,
                completed_at TEXT,
                source TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    except Exception as e:
        log.error(f"Failed to initialize AIPET database tables: {e}")

# Initialize tables when the engine is loaded
init_aipet_tables()
