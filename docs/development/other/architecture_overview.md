# Architecture Overview

OpenClawGotchi V3 is built on a highly modular Python architecture that bridges a fast, low-level execution environment ("Body") with an asynchronous LLM-driven intelligence ("Soul").

This document provides a high-level overview of the code flow, starting from the entry point down to the core subsystems.

## 1. Entry Point (`src/main.py`)

The application begins at `src/main.py`. This script is responsible for:
1. **Bootstrapping the Environment**: Loading `.env` variables via `src/config.py` and setting up the logger.
2. **Checking Workspace Health**: Ensuring `workspace/` exists and contains the necessary `SOUL.md` and `IDENTITY.md` files.
3. **Initializing Subsystems**: Starting the database, the plugin manager, and the hardware interfaces.
4. **Starting the Heartbeat**: Launching the main `asyncio` event loop which coordinates everything.

## 2. Core Modules (`src/core/`)

The `core/` directory contains the foundational logic that powers the agent's internal state and skill management.
- **`workspace.py`**: The bridge between Python and the Markdown files. It reads `SOUL.md`, parses daily journals, and injects this context into LLM prompts.
- **`events.py`**: The central pub/sub event bus. This is where `@hook` plugins register. When a subsystem emits an event (like `system.startup`), this module routes it to the appropriate handlers.
- **`skill_loader.py`**: Scans the `agents/skills/` and `workspace/skills/` directories for executable Markdown skills, registering them dynamically.

## 3. UI and Display (`src/ui/` & `src/hardware/`)

Because E-Ink displays are slow, the UI operates on an independent async loop.
- **`gotchi_ui.py`**: The rendering engine. It pulls the current "state" (WiFi status, current face, last log message) from an internal state dictionary and compiles it into a PIL Image.
- **`hardware/display.py`**: Interacts with the SPI pins via the `epd2in13` driver to push the PIL image buffer to the physical Waveshare E-Ink screen.

## 4. The Bot Layer (`src/bot/`)

The `bot/` directory handles asynchronous interactions with external entities and the agent's internal reasoning loops.
- **`heartbeat.py`**: The central loop that ticks every few seconds. It manages rate-limiting, decides when the LLM should evaluate its surroundings, and triggers UI refreshes.
- **`handlers.py`**: Processes incoming commands (either from the `gotchi` CLI or via a Discord connection) and routes them to the appropriate Python skill or LLM prompt.
- **`llm_router.py`**: The LiteLLM wrapper. It takes the context built by `workspace.py`, formats it, and calls the appropriate AI model (e.g., Gemini-Flash for quick decisions, GPT-4o for complex planning).

## Data Flow Example: Capturing a Handshake

1. `src/hardware/pwn.py` (running a Bettercap wrapper) captures a handshake.
2. It emits a `pwn.handshake_captured` event via `src/core/events.py`.
3. A plugin in `plugins/` catches the event, updating `src/db/` with the new stats.
4. The event notifies the `src/bot/llm_router.py`, which prompts the AI to react.
5. The AI decides it is happy, updating `IDENTITY.md` with a "happy" state.
6. The next tick of `src/ui/gotchi_ui.py` reads the happy state, renders a smiling face, and pushes it to the E-Ink screen.
