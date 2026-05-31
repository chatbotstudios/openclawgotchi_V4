# 🦾 Pwnagotchi Plugins Integration: Technical Implementation Plan

This document details the architectural blueprint, integration phases, and design considerations for importing and adapting native Pwnagotchi plugins into the modular, event-driven **OpenClawGotchi V4** codebase.

---

## 🧭 Architectural Strategy

Traditional Pwnagotchi plugins are built around a monolithic class-based lifecycle (`BasePlugin`) that hooks directly into the host system. In contrast, **OpenClawGotchi V4** utilizes a **lightweight, async event-driven plugin system** powered by the `@hook` decorator from the `hooks.runner` module.

To integrate these plugins safely without blocking the core AI daemon or draining the Raspberry Pi Zero 2W's limited 512MB memory, we will translate the legacy lifecycle callbacks into **V4 asynchronous event hooks**:

```mermaid
graph TD
    A[Legacy Pwnagotchi Plugin] -->|Refactor Lifecycle| B[V4 Event Plugin]
    B -->|@hook("startup")| C[System Init & Config Load]
    B -->|@hook("pwn.wifi_update")| D[Bettercap AP Scan Aggregator]
    B -->|@hook("pwn.handshake")| E[Game Engine XP & Mission Progress]
    B -->|@hook("heartbeat")| F[Adaptive Core Diagnostics]
```

---

## 🛠️ Phase-by-Phase Integration Plan

```carousel
# Phase 1: Event Mapping
**Goal**: Build a thin, backward-compatible abstraction layer within the OpenClaw hooks pipeline.
- Implement a class-to-hook wrapper allowing legacy `BasePlugin` definitions to be imported directly.
- Standardize `HookEvent` data footprints to match the arguments expected by standard Pwnagotchi lifecycle callbacks.
<!-- slide -->
# Phase 2: Refactoring Wireless Scanners
**Goal**: Migrate active scanning, rogue AP detection, and deauth hooks to background threads.
- Refactor `rogue_ap_detector.py` and `deauthenticator.py` into async event listeners.
- Replace blocking shell processes with asynchronous subprocess executors featuring strict timeouts (as defined in V4 guidelines).
<!-- slide -->
# Phase 3: Game Engine Integration
**Goal**: Connect plugin telemetry directly to the RPG leveling database and mission indexing system.
- Hook handshake events to `increment_mission_progress("Handshake Hunter")`.
- Tie network anomaly detection (Evil Twins, Spoofs) to custom Kaomoji status displays and alert logs.
```

---

## 1. Phase 1: Event Mapping Abstraction

We will implement an automated wrapper class `LegacyPluginAdapter` within `src/hooks/runner.py` that maps `HookEvent` instances back to standard callback parameters.

### Lifecycle Callback Reference Mapping

| Legacy Callback | V4 Hook Trigger | Action Details |
| :--- | :--- | :--- |
| `on_loaded()` | `@hook("startup")` | Initial plugin state and environment check. |
| `on_ready()` | `@hook("pwn.ready")` | Triggers when Bettercap interface is fully initialized. |
| `on_wifi_update()` | `@hook("pwn.wifi_update")` | Emits active Access Point lists from scans. |
| `on_handshake()` | `@hook("pwn.handshake")` | Triggers when a WPA/WPA2 handshake file is logged. |
| `on_unload()` | `@hook("shutdown")` | Destructors and system state restoration. |

---

## 2. Phase 2: Active & Passive Plugin Integration

We will divide the 13 cloned plugins from `Deus73/pwnagotchi-plugins` into two implementation streams: **Passive Detection** (low risk, high telemetry) and **Active Auditing** (high risk, automated action).

### Stream A: Passive Detection & Intelligence (Low-Resource Hooks)
These plugins run passively during the heartbeat loop and scan updates to update the local database.

#### 1. Rogue AP & Spoofing Diagnostics (`plugins/network_auditor.py`)
Aggregates logic from `rogue_ap_detector.py` and `dns_spoof_detector.py`:
- **Trigger**: `@hook("pwn.wifi_update")`.
- **Logic**: Inspects newly discovered ESSIDs and BSSIDs against the trusted environment ledger. If an ESSID is found on a channel or BSSID that differs from the registered configuration, it raises a system warning.
- **Fail-safe**: Uses asynchronous Scapy sniffers with strict port bounds (`udp port 53` for DNS) to prevent memory allocation crashes.

```python
from hooks.runner import hook, HookEvent
from hardware.display import update_display

@hook("pwn.wifi_update")
def on_wifi_update(event: HookEvent):
    ap_list = event.data.get("aps", [])
    # Parse for matching ESSID duplicate anomalies (Evil Twin / Rogue AP)
    for ap in ap_list:
        if detect_rogue_ap(ap):
            update_display(mood="hardware_panic", text=f"ALERT: Rogue AP {ap['ssid']}")
```

### Stream B: Active Auditing (Subprocess Isolation)
These plugins execute terminal commands and must run in isolated background threads.

#### 2. Deauth Ingestion & Restoration (`plugins/deauth_handler.py`)
Adapts logic from `deauthenticator.py`:
- **Trigger**: `@hook("pwn.handshake")`.
- **Logic**: Leverages the local command runner to execute short deauth verification commands.
- **Resiliency Constraint**: All system calls (`aireplay-ng`) **must** include a maximum execution timeout (e.g. `timeout=10`).

---

## 3. Phase 3: Game Engine & Mission Mapping

To reward operational success, plugin executions will be mapped directly to the **AIPET Game Engine** using `increment_mission_progress` hooks.

### RPG Telemetry Rewards

| Plugin Trigger | Triggered Game Mission | XP Awarded | Status Indicator Face |
| :--- | :--- | :--- | :--- |
| Verified Handshake Capture | `Handshake Hunter` | `+50 XP` | `(✪ ◡ ✪) joyful` |
| Rogue AP Spotting | `Sentinel Shield` | `+100 XP` | `(▨ E ▨) sd_card_fail` |
| Passive BLE MAC Logged | `Silent Scanner` | `+10 XP` | `(๏ ◡ ๏) curious` |

---

## 🧪 Verification & Testing Plan

1. **Static Analysis**: Compile all modified files using `python3 -m py_compile` to verify syntax.
2. **Mock Event Execution**:
   - Run simulation scripts to emit mock `pwn.wifi_update` packets containing duplicate BSSIDs.
   - Verify that the `network_auditor.py` plugin catches the rogue AP anomaly, triggers the target status warning, and increments `Sentinel Shield` mission progress.
3. **Memory Diagnostics**:
   - Run `gotchi dash` before and after loading the `network_auditor.py` plugin to confirm RAM utilization remains within the **400MB threshold** under the Pi Zero 2W limit.
