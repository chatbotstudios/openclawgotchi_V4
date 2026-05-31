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
                name TEXT UNIQUE,
                base_name TEXT,
                category TEXT,
                xp_reward INTEGER,
                target INTEGER DEFAULT 1,
                progress INTEGER DEFAULT 0,
                status TEXT,
                completed_at TEXT,
                source TEXT
            )
        ''')
        
        # Auto-migration for target, progress, and base_name columns
        try:
            conn.execute("SELECT target FROM aipet_missions LIMIT 1")
        except sqlite3.OperationalError:
            try:
                log.info("Auto-migrating aipet_missions table: adding progressive columns...")
                conn.execute("ALTER TABLE aipet_missions ADD COLUMN target INTEGER DEFAULT 1")
                conn.execute("ALTER TABLE aipet_missions ADD COLUMN progress INTEGER DEFAULT 0")
                conn.execute("ALTER TABLE aipet_missions ADD COLUMN base_name TEXT")
                conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_aipet_missions_name ON aipet_missions(name)")
            except Exception as e:
                log.warning(f"Failed to auto-migrate aipet_missions columns: {e}")
        
        conn.commit()
        conn.close()
    except Exception as e:
        log.error(f"Failed to initialize AIPET database tables: {e}")

# Initialize tables when the engine is loaded
init_aipet_tables()
