# Database Schema Documentation

OpenClawGotchi V3 uses a lightweight SQLite database (`src/db/gotchi.db`) to manage short-term state, runtime statistics, and structured memory that is inefficient to store in plain Markdown files.

This document outlines the core tables and their purposes.

## Database Location and Connection
- **Path**: The database is typically stored in `src/db/gotchi.db` (or overridden via `.env`).
- **Connection**: Managed by `src/db/connection.py`, using standard `sqlite3` built-in libraries with connection pooling.

---

## 1. The `stats` Table

This table tracks the tactical "Body" metrics across reboots.

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER | Primary Key (Always 1, we use an upsert pattern for a single row of global stats) |
| `boot_count` | INTEGER | Total number of times the device has been powered on |
| `total_uptime` | INTEGER | Cumulative uptime in seconds |
| `networks_discovered` | INTEGER | Lifetime count of unique BSSIDs seen |
| `handshakes_captured`| INTEGER | Lifetime count of WPA handshakes successfully recorded |
| `pwn_score` | INTEGER | An arbitrary score calculated based on activity, used by the AI to determine "hunger" or "satisfaction" |

---

## 2. The `facts` Table

Used by the "Soul" (AI Brain) to store structured, long-term memory about entities (users, networks, devices). When the AI learns something, it queries or updates this table rather than cluttering `MEMORY.md` with structured data.

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER | Primary Key, Auto-increment |
| `entity_type` | TEXT | E.g., 'user', 'network', 'location' |
| `entity_id` | TEXT | E.g., a Discord User ID, or a WiFi BSSID |
| `attribute` | TEXT | E.g., 'favorite_color', 'encryption_type' |
| `value` | TEXT | The actual data (e.g., 'blue', 'WPA2') |
| `learned_at`| DATETIME| When the agent acquired this fact |

---

## 3. The `messages` Table

Acts as a short-term buffer for incoming/outgoing chat messages (like Discord) and system alerts. This allows the AI Brain to read the "recent history" context when evaluating how to respond.

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER | Primary Key, Auto-increment |
| `timestamp` | DATETIME| When the message occurred |
| `source` | TEXT | Where it came from (e.g., 'discord_channel_123', 'system_event', 'cli') |
| `role` | TEXT | 'user', 'agent', 'system' (Maps nicely to LLM prompt structures) |
| `content` | TEXT | The body of the message |
| `is_read` | BOOLEAN | Whether the LLM has processed this message yet |

---

## Interaction Rules for Developers

1. **Do not use heavy ORMs**: Stick to standard SQL queries via the wrapper functions provided in `src/db/`. The Pi Zero 2W struggles with the overhead of large libraries like SQLAlchemy.
2. **Always close connections**: If writing custom SQL outside of the provided context managers, ensure connections are closed to avoid `database is locked` errors.
3. **Backup**: The database is excluded from version control via `.gitignore`. If you need to back it up, copy `gotchi.db` manually.
