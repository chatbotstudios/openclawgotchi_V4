# Changelog

All notable changes to OpenClawGotchi V3 will be documented in this file.

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
