# Changelog

All notable changes to OpenClawGotchi V3 will be documented in this file.

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
