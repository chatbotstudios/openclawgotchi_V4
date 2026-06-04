# Changelog

All notable changes to OpenClawGotchi V3 will be documented in this file.

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
