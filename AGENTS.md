# AGENTS.md — Project Rules

> This file is for AI agents and developers working on the project.
> For bot personality, see `workspace/SOUL.md` (created from templates/).

## Project Structure

```
openclawgotchi/
├── workspace/           # Bot's live personality (gitignored, visible root folder)
│   ├── AGENTS.md        # This file's copy for the agent's context
│   ├── ARCHITECTURE.md  # System design and logic
│   ├── BOT_INSTRUCTIONS.md # System prompt
│   ├── SOUL.md, IDENTITY.md, USER.md
│   ├── HEARTBEAT.md, MEMORY.md
│   ├── skills/          # Manual Markdown-based skills
│   └── memory/          # Daily logs (YYYY-MM-DD.md)
│
├── agents/              # Visible Skills & Automated Procedures (npx)
│   └── skills/          # Skills installed via CLI tools
│
├── templates/           # Default personality templates
│   ├── BOOTSTRAP.md     # First-run onboarding ritual
│   ├── BOT_INSTRUCTIONS.md  # System prompt
│   ├── SOUL.md, IDENTITY.md, USER.md
│   ├── HEARTBEAT.md, MEMORY.md, AGENTS.md
│   ├── TOOLS.md, BOOT.md, ARCHITECTURE.md
│
├── docs/                # Comprehensive Knowledge Base (Two-Brain concept, guides)
│   ├── user_guides/     # Manuals for human operators
│   ├── ai_instructions/ # Rules and architecture for AI agents
│   └── development/     # Technical specs (E-Ink API, DB Schema)
│
├── src/                 # Python source code
│   ├── main.py          # Entry point
│   ├── config.py        # Paths, env vars
│   ├── core/            # Core logic (workspace, skill loader)
│   ├── bot/             # Discord handlers, heartbeat
│   ├── db/              # SQLite: messages, facts, stats
│   ├── ui/              # E-Ink display (gotchi_ui.py)
│   ├── hardware/        # Display control, auto-mood
│   ├── drivers/         # E-Ink driver (epd2in13_V4)
│   └── utils/           # Doctor, patch_self
│
├── setup.sh             # Interactive setup wizard
├── harden.sh            # Pi hardening (swap, watchdog, RAM)
├── plugins/             # Event-driven Python plugins (hooks)
├── handshakes/          # Saved WPA handshakes and BLE scan logs
├── gotchi               # The Unified Tactical CLI wrapper
├── .env.example         # Configuration template
└── LICENSE              # MIT
```

## Document-Driven Architecture

OpenClawGotchi follows a **Workspace-First** philosophy. The agent's identity, behavior, and skills are defined by the Markdown files in `workspace/`. The core Python code serves as the execution engine for the directives found in these documents.

## Getting Started

1. On Pi: clone repo, run `./setup.sh` (creates `.env`, `workspace/`, installs deps, starts service)
2. Or manually: copy `.env.example` → `.env`, copy `templates/` → `workspace/`, configure, `python3 src/main.py`
3. Service name: `gotchi` (legacy: `gotchi-bot`)

## Code Style

- Python 3.9+
- Keep memory usage low (512MB Pi Zero 2W limit)
- Use `asyncio` and `asyncio.to_thread` for non-blocking tool operations (MANDATORY on Pi Zero 2W to prevent heartbeat crashes)
- E-Ink updates are slow (~2–3s) - avoid rapid flickering
- Use `gotchi dash` for real-time resource monitoring
- **Commit Style**: Use the `git-commit` skill or follow **Conventional Commits** (`feat`, `fix`, `chore`).

## Safety Rules

- **No credentials in code** — Use `.env`
- **No heavy processes** — 512MB RAM limit
- **`trash` > `rm`** — Recoverable deletes
- **Ask before external actions** — Network, installs
- **Do not overwrite or "restore" critical display code** — `src/ui/gotchi_ui.py` and `src/drivers/` are the E-Ink stack. Never replace them with backups or write JSON/other content into them.

## Key Files

| File | Purpose |
|------|---------|
| `src/main.py` | Main entry point |
| `src/core/workspace.py` | Document context injection & skill discovery |
| `src/bot/handlers.py` | Command and message handlers |
| `src/ui/gotchi_ui.py` | E-Ink display rendering and faces catalog |
| `workspace/` | Live bot personality and memory |
| `agents/` | Automated skills and ecosystem tools |
| `templates/` | Default blueprints for new workspaces |

## Adding Features

1. **Bot Behavior**: Edit `workspace/SOUL.md` or `IDENTITY.md`.
2. **New Skills**: 
    - **Workflows (Manual)**: Create a folder in `agents/workflows/` (e.g., `agents/workflows/SENTRY/WORKFLOW.md`).
    - **Automated**: Use `npx skills add <source>`. They will land in `agents/skills/`.
3. **New Plugins**: 
    - Create a Python file in `plugins/` (e.g., `plugins/my_plugin.py`) and use the `@hook` decorator to subscribe to events.
4. **Core Logic**: Edit relevant modules in `src/`.

## Deployment

```bash
# Deploy to Pi
scp -r . pi@raspberrypi:~/openclawgotchi/
ssh pi@raspberrypi "cd openclawgotchi && ./setup.sh"

# Restart service
ssh pi@raspberrypi "sudo systemctl restart gotchi"

# View logs
ssh pi@raspberrypi "journalctl -u gotchi -f"
```

---

### 🛡️ Skill Management Policy
To maintain our **Visible Workspace** philosophy:
1.  **Always use `agents/skills/`** for any automated installations (e.g., `npx skills add`).
2.  If a tool creates a hidden `.agents/` folder, **immediately move its contents** to `agents/` and delete the hidden folder. (The `./setup.sh` script installs a shell wrapper to automate this for you).
3.  Ensure `SKILL.md` files are always readable and located in `agents/skills/<name>/SKILL.md`.
