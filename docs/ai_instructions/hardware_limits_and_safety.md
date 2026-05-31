# Hardware Limits and Safety Guidelines

> CRITICAL constraints for AI Agents generating code or workflows for OpenClawGotchi V3.

The target hardware for this project is primarily the **Raspberry Pi Zero 2W**. While capable, it is highly constrained compared to a desktop environment. 

## 1. Memory Limitations (512MB RAM)

The Pi Zero 2W has only 512MB of RAM, shared with the GPU.
- **Rule**: Avoid loading large datasets or LLM weights into memory. All heavy LLM reasoning *must* be routed through external APIs (OpenAI, Gemini, Anthropic).
- **Rule**: Limit concurrent Python threads.
- **Rule**: Avoid aggressive pandas or numpy operations unless absolutely necessary and garbage-collected quickly.

## 2. Synchronous Blocking is Fatal

The Python "Body" runs a constant heartbeat loop that manages radio interfaces and the E-Ink display.
- **Rule**: NEVER write long-running synchronous code in the main thread.
- **Rule**: If writing a tool or plugin that makes a network request (e.g., `requests.get`), you must use `asyncio.to_thread` or an async library like `aiohttp`. Blocking the main loop for even 5 seconds will cause watchdog timeouts and E-Ink freezes.

## 3. E-Ink Display Constraints

The Waveshare E-Ink display is not an LCD. It requires physical time for the e-ink particles to shift.
- **Rule**: Full screen refreshes take 2-3 seconds. Partial refreshes are faster but can cause ghosting.
- **Rule**: Do NOT attempt to build rapid animations (> 1 frame per second).
- **Rule**: Do not spam `gotchi ui refresh` commands. Rate limit UI updates to once every 10-30 seconds to preserve hardware lifespan and battery.

## 4. Power Management

- **Rule**: Do not peg the CPU to 100% continuously.
- **Rule**: If the AI detects `hardware.low_battery`, it should gracefully reduce its background reasoning frequency to conserve power.

## 5. Filesystem Wear

The OS runs on an SD Card, which has limited write cycles.
- **Rule**: Minimize aggressive logging. Use SQLite for state, and only write to markdown journals periodically, not every millisecond.
