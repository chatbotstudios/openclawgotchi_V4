# Changelog

All notable changes to OpenClawGotchi V3 will be documented in this file.

## [v3.4] - 2026-06-12
### Added
- **Restful Dream Patch**: The Gotchi now organically regenerates `+10.0 HP` automatically whenever a procedural dream is triggered, linking the AI simulation engine to the hardware vitals layer.
- **Discord `/dream` Slash Command**: A new Discord-native command that mimics the exact SSH terminal layout for synthetic dreams, safely rendering raw tool footprints into clean Discord code blocks.
- **Dynamic E-Ink UI & Kernel Polling**: E-Ink now reads `/proc/net/wireless` directly to render real-time WiFi signal quality ` ▂▃▅` without blocking the main loop or invoking shell sub-processes.
- **Supercharged Discord Dashboards**: Completely overhauled the `/status` and `/memory` outputs to track Session vs Lifetime messages, total Dreams, and properly scale visual XP progress bars to decimal precision.

## [v3.3] - 2026-06-12
### Fixed
- **Architectural Workspace Path**: Fixed a critical bug where `config.py` hardcoded the `templates/` directory instead of the live `workspace/` directory, restoring daily memory logging.
- **Dream Notification Threading**: Removed daemon flags from Discord webhooks so that CLI commands natively wait for network requests to finish before exiting, ensuring dreams successfully post to `#general`.
- **Badge Schema Validation**: Resolved Pydantic crash in `AIPETState` during dream sequences by updating `badges` type validation to accept dictionary objects.
- **Flat-File Logging**: Initialized FileHandlers across both the background daemon and CLI to ensure a persistent `gotchi.log` is captured in the `data/` directory.
- **CLI Log Pollution**: Silenced raw Python `INFO` logs on the CLI stream to ensure clean, interactive outputs during `gotchi aipet dream`.
- **Bounty Webhooks**: Added `#heartbeats` discord notifications when the Gotchi autonomously mints new procedural bounties.

## [v3.2] - 2026-06-12
### Added
- **Discord Bulletproof Sync**: Added `/brain-backup` slash command in Discord for one-click brain backups, code pulls, and safe daemon restarts.
- **Dream Webhook Notifications**: Gotchi dreams are now broadcasted directly to the Discord #general channel as they happen.
- **Enhanced Procedural Dreams**: Prompts refined to draw from all Gotchi capabilities (Networking, Pwn, Diagnostics) rather than just BLE/WiFi.

## [v3.1] - 2026-06-12
### Added
- **Procedural Generation Engine**: The Gotchi can now hallucinate its own tactical missions, dreams, and badges.
- **Headless Backup Protocol**: `gotchi backup` safely pushes the Gotchi's internal SQLite and memory to the `gotchi` cloud branch without dirtying the `master` source code.
- **Git-Trackable Procedural Missions**: Autonomously generated bounties are now saved to `missions/progressive.json` to allow tracking on the master branch.
- **Dynamic Lore Generation**: Expanded the `experience` skill to synthesize raw hardware events (WPA handshakes, BLE beacons) into first-person narrative journals.


## [v2.3] - 2026-06-11
### Added
- **AIPET Game Engine Layer**: Full implementation of biological and emotional mechanics.
- **Physical Vitals & Leveling**: Implemented `aipet_state` tracking HP, XP, RP, and Level. Added sleep/dream states for HP recovery.
- **Rewards & Legacy Ledger**: Introduced Badges and Milestones stored immutably in SQLite.
- **Cognitive & Meta Skills**: Added `introspection`, `state_awareness`, `experience`, `mood`, and `kaomoji_mood` Markdown procedural skills to bridge the LLM and the game engine.
- **Game Engine CLI Tools**: Added `gotchi aipet set-mood`, `gotchi aipet sleep`, `gotchi aipet award-badge`, and `gotchi aipet badges` commands.

## [v1.4] - 2026-06-05
### Added
- **Event-Driven Cognitive Ingestion**: Real-time event bus (`events.emit`) that feeds hardware triggers directly into SQLite memory and enqueues organic LLM reactions.
- **Offline Hunting Daemon**: Robust background process (`OfflineHunter`) that manages Wi-Fi monitor mode, screen inversion (Dark Mode), and strict timeouts to ensure safe reconnection.
- **`launch_offline_hunt` Tool**: Explicit LLM capability to detach from the network and audit handshakes.

### Fixed
- Fixed `discord.py` temporary DNS resolution crashes by capping the exponential backoff to 15s during offline hunts, ensuring near-instant recovery when the network returns.
- Added explicit NetworkManager stabilization delay to prevent API timeouts post-hunt.

## [v3.0.0] - 2026-05-09
### Added
- **Unified Command Bus**: Centralized `gotchi` CLI for all system operations.
- **Hardware Resilience**: SPI circuit breaker and uptime-aware radio syncing.
- **Turbo Setup**: Optimized `setup.sh` with dependency health checks.
- **Discord Bot**: Fully async Discord integration with slash commands.
- **Extension SDK**: Modular plugin system for Pwnagotchi and system tools.

### Changed
- Migrated dependency management to authoritative `requirements.txt`.
- Optimized bot startup sequence for Raspberry Pi Zero 2W.

### Fixed
- Resolved Discord "Double Awakening" and message duplication bugs.
- Fixed SPI bus initialization failures on cold boot.

---
*Maintained with 🦋 by Chatbot Studios*
