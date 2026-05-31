# OpenClawGotchi V3 — Logging Infrastructure Audit

> **Audited by:** Senior Python Engineer / Observability Expert  
> **Date:** 2026-05-30  
> **Version audited:** v3.0.10 / v3.4.0  
> **Target hardware:** Raspberry Pi Zero 2W  

---

## 1. Executive Summary

| Metric | Score |
|---|---|
| **Overall Quality** | **5 / 10** |
| Command Usability | 4 / 10 |
| Architecture | 5 / 10 |
| Security & Privacy | 6 / 10 |
| Performance & Resource Safety | 5 / 10 |
| Two-Brain Integration | 4 / 10 |
| Reliability | 6 / 10 |

### Biggest Issues

1. **`gotchi logs` has almost no options** — it only supports `tail`, `clear`, and `extended`. No filtering by level, module, keyword, or time range.
2. **Conflicting `basicConfig` calls** — `bettercap_listener.py` and `subconscious_pwn.py` each call `logging.basicConfig()` at module level with a different format, which silently overrides the root logger configuration set in `main.py`. This causes inconsistent formatting in the live feed.
3. **LLM raw message payloads are logged at `INFO`** — the full LiteLLM response object (including function call arguments, potentially containing user data) is logged at INFO level on every single call.
4. **No file-based log rotation** — all logging goes through `journald`. There is no file handler with `RotatingFileHandler`, so the JSONL audit file at `logs/commands.jsonl` has **no size cap** and will silently grow until the SD card is full.
5. **No latency/token instrumentation on LLM calls** — there is no timing between send and receive on LLM calls, and actual token counts are never logged, making performance analysis impossible.

---

## 2. Critical Issues

### 🔴 CRIT-01 — Conflicting `basicConfig` calls corrupt log format

**Files:**
- [`src/hardware/bettercap_listener.py:13`](../../../src/hardware/bettercap_listener.py#L13)
- [`src/hardware/subconscious_pwn.py:19`](../../../src/hardware/subconscious_pwn.py#L19)
- [`src/main.py:41-44`](../../../src/main.py#L41)

**Problem:** `main.py` calls `logging.basicConfig(format="%(name)s - %(levelname)s - %(message)s", level=INFO)`. However, `bettercap_listener.py` and `subconscious_pwn.py` both call `logging.basicConfig(level=INFO, format="[%(levelname)s] %(message)s")` at the top of their module files. 

`basicConfig()` is a no-op if a root handler is already configured — but if these modules are imported *before* `main.py` sets up its handler (e.g. during a CLI call like `gotchi logs`), the hardware module format silently wins. This causes inconsistent log output that is difficult to grep.

**Fix:**
```python
# DELETE these two lines from bettercap_listener.py and subconscious_pwn.py:
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

# They already use getLogger(__name__) correctly, which is all they need.
```

---

### 🔴 CRIT-02 — Raw LLM responses logged at INFO on every call

**File:** [`src/core/litellm_connector.py:179-180`](../../../src/core/litellm_connector.py#L179)

**Problem:** Every LLM call logs the full raw message object at INFO level:
```python
log.info(f"[LiteLLM Debug] Raw msg: {clean_msg}")
```
This dumps the entire LLM response body — including all tool call arguments — to journald on every single interaction. On a busy bot, this is both a **performance problem** (string serialization of large objects) and a **privacy concern** (user messages appear in system logs readable by any user with `journalctl` access).

**Fix:** Lower to DEBUG level and strip tool call arguments:
```python
log.debug(f"[LiteLLM Debug] Raw msg (content only): {str(msg.content)[:200]}")
log.debug(f"[LiteLLM Debug] Finish reason: {getattr(response.choices[0], 'finish_reason', 'unknown')}")
```

---

### 🔴 CRIT-03 — JSONL audit log has no rotation or size cap

**File:** [`src/audit_logging/command_logger.py:15`](../../../src/audit_logging/command_logger.py#L15)

**Problem:** `COMMANDS_LOG = PROJECT_DIR / "logs" / "commands.jsonl"` is opened in append mode (`"a"`) with no size limit, no rotation, and no cleanup job. On an active bot, this file grows indefinitely. On a Pi Zero with an 8–32GB SD card running lots of tool calls and radio events, this is a **silent disk-killer**. SD card full → SQLite corruption → full system failure.

**Fix:**
```python
import logging.handlers

# Use a rotating handler capped at 5MB, keeping 3 rotated files
handler = logging.handlers.RotatingFileHandler(
    COMMANDS_LOG, maxBytes=5*1024*1024, backupCount=3
)
```
Or, simpler: add a periodic cleanup cron job that prunes entries older than 30 days.

---

### 🟠 CRIT-04 — MAC addresses logged without opt-in redaction

**Files:**
- [`src/hardware/bettercap_listener.py:71,73,140`](../../../src/hardware/bettercap_listener.py)
- [`src/hardware/subconscious_pwn.py:97,135,151`](../../../src/hardware/subconscious_pwn.py)

**Problem:** Raw MAC addresses are logged at `INFO` and `CRITICAL` level. In some jurisdictions, MAC addresses of captured devices are personally identifiable information (PII). While this is inherent to the project's function, there should be a config flag (`LOG_REDACT_MACS=true`) to hash or mask them in log output for operational security.

**Fix:**
```python
def _redact_mac(mac: str) -> str:
    if os.environ.get("LOG_REDACT_MACS"):
        return mac[:8] + ":xx:xx:xx"  # Keep OUI, mask device part
    return mac
```

---

## 3. High Priority Improvements

### 🟡 HIGH-01 — `gotchi logs` command is nearly unusable for debugging

**File:** [`src/core/cli/commands/core.py:80-89`](../../../src/core/cli/commands/core.py#L80)

**Current implementation:**
```python
@click.command()
@click.argument('action', required=False, default='tail')
def logs(action):
    """Stream or manage bot logs. Actions: tail, clear, extended."""
    if action == 'tail':
        subprocess.run(["journalctl", "-u", "gotchi", "-n", "50", "-f"])
    elif action == 'clear':
        subprocess.run(["sudo", "journalctl", "--vacuum-time=1s"])
    elif action == 'extended':
        subprocess.run(["journalctl", "-u", "gotchi"])
```

This is a bare wrapper around `journalctl`. There is no filtering, no colorization, no module filtering, no level filtering, and the 50-line default is often not enough context.

**Recommended enhanced implementation** (see Section 6 for full design).

---

### 🟡 HIGH-02 — No LLM call timing or token tracking

**File:** [`src/core/litellm_connector.py`](../../../src/core/litellm_connector.py)

**Problem:** There is zero instrumentation of how long LLM calls take or how many tokens are consumed. This is the single highest-latency operation on the Pi Zero. Without this data, you cannot tell if slowness is from network latency, Pydantic schema generation overhead, or the model itself.

**Fix:** Add timing around the `completion()` call:
```python
import time
t0 = time.monotonic()
response = await asyncio.to_thread(completion, **kwargs)
latency_ms = int((time.monotonic() - t0) * 1000)
usage = getattr(response, "usage", None)
tokens_in = getattr(usage, "prompt_tokens", 0)
tokens_out = getattr(usage, "completion_tokens", 0)
log.info(f"[LLM] {self.model} | {latency_ms}ms | in={tokens_in} out={tokens_out}")
```

---

### 🟡 HIGH-03 — `audit_logging` is not used in Discord path

**File:** [`src/main.py:52-59`](../../../src/main.py#L52) vs [`src/bot/discord_bot.py`](../../../src/bot/discord_bot.py)

**Problem:** `log_command()` from `audit_logging/command_logger.py` is called in `main.py`'s cron job path, but **never called in `discord_bot.py`**. This means Discord interactions leave no audit trail in `logs/commands.jsonl`. The JSONL audit log is essentially dark for Discord users.

**Fix:** Add `log_command()` calls in `discord_bot.py`'s `on_message` handler and slash command handlers.

---

### 🟡 HIGH-04 — No correlation ID between LLM calls and Discord messages

**Problem:** When a user sends a message and the LLM calls 5 tools before responding, the journal shows interleaved log lines from multiple sources with no shared ID to trace the full request/response lifecycle.

**Fix:** Generate a `request_id = uuid4().hex[:8]` per message and pass it through to all log calls for that interaction.

---

## 4. Medium & Nice-to-Have Suggestions

### 🔵 MED-01 — Structured logging would enable powerful filtering

Currently all logs are plain strings. Switching to structured logging (even just adding key=value pairs consistently) would allow `journalctl -u gotchi -o json` to be filtered with `jq`.

```python
# Instead of:
log.info(f"[LiteLLM] API Error on turn {turn+1}: {err_str[:200]}")

# Do:
log.error("[LiteLLM] API error", extra={
    "turn": turn+1,
    "error": err_str[:200],
    "model": self.model
})
```

---

### 🔵 MED-02 — `LOG_LEVEL` env var is defined but not wired up

**File:** [`.env.example`](../../../.env.example) defines `LOG_LEVEL=INFO` but [`main.py`](../../../src/main.py#L41) hardcodes `level=logging.INFO`. The env var is never read.

**Fix:**
```python
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    format="%(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, LOG_LEVEL, logging.INFO)
)
```

---

### 🔵 MED-03 — `log.critical()` used for normal operational events

**File:** [`src/hardware/bettercap_listener.py:71`](../../../src/hardware/bettercap_listener.py#L71)

```python
log.critical(f"REFLEX TRIGGERED: Valid Handshake captured for {ap_mac}!")
```

`CRITICAL` should be reserved for system-threatening failures. A successful handshake capture is a **success** event. Use `log.info()` or create a custom `SUCCESS` level. `CRITICAL` in journald alerts monitoring tools and creates alert fatigue.

---

### 🔵 MED-04 — `WebSocket URI` contains credentials in plaintext in logs

**File:** [`src/hardware/bettercap_listener.py:32`](../../../src/hardware/bettercap_listener.py#L32)

```python
log.info(f"Nervous System attempting to bind to Bettercap events at {self.ws_uri}...")
```

`self.ws_uri` includes the credentials in the URL: `ws://gotchi:123456@localhost:8081/api`. These are logged to journald in plaintext.

**Fix:**
```python
safe_uri = f"ws://{BETTERCAP_USER}:***@localhost:8081/api"
log.info(f"Nervous System binding to {safe_uri}...")
```

---

## 5. Positive Aspects

✅ **`rate_limits.py` has excellent logging** — clean, structured messages with context about retry timing, provider name, and limit type. A model for the rest of the codebase.

✅ **`audit_logging/command_logger.py` has a solid JSONL design** — machine-readable, timestamped entries are the right foundation for future tooling.

✅ **`litellm_connector.py` redacts `api_key` from debug dumps** (line 286) — good security instinct:
```python
{k:v for k,v in kwargs.items() if k != 'api_key'}
```

✅ **Thread-safety is solid** — Python's `logging` module is thread-safe by default, and all async tool calls correctly use `asyncio.to_thread()` to avoid blocking the event loop.

✅ **systemd integration is correct** — using `journalctl -u gotchi` as the primary log view is the right approach for a systemd service. Log persistence and rotation are handled by `journald` automatically.

✅ **`COMMANDS_LOG` parent directory is created on demand** — `_ensure_log_dir()` is called before every write, preventing startup crashes.

---

## 6. Recommended Enhancements

### 6.1 — New `gotchi logs` subcommands

Replace the current single-action `logs` command with a proper subcommand group:

```
gotchi logs                 # = gotchi logs tail (default)
gotchi logs tail            # Live stream (journalctl -f), last 100 lines
gotchi logs error           # Filter to ERROR + CRITICAL only
gotchi logs llm             # Filter to LiteLLM/Claude lines only
gotchi logs radio           # Filter to NervousSystem/SubconsciousPwn
gotchi logs hardware        # Filter to hardware.display, hardware.display
gotchi logs audit           # Read from logs/commands.jsonl (pretty printed)
gotchi logs stats           # Show log volume stats (lines/hour, top modules)
gotchi logs clear           # Vacuum journald
gotchi logs --lines 200     # Custom line count
gotchi logs --since 1h      # Time-windowed view
gotchi logs --level ERROR   # Level filter
gotchi logs --module core   # Module filter (grep on module name prefix)
```

**Sample implementation:**
```python
@click.command()
@click.argument('filter', required=False, default='tail')
@click.option('--lines', '-n', default=100, help='Number of lines to show')
@click.option('--since', default=None, help='Time window, e.g. "1h", "30m"')
@click.option('--level', type=click.Choice(['DEBUG','INFO','WARNING','ERROR','CRITICAL']), default=None)
def logs(filter, lines, since, level):
    """Stream and filter bot logs."""
    
    MODULE_FILTERS = {
        'llm':      ['LiteLLM', 'litellm', 'core.litellm', 'core.claude'],
        'radio':    ['NervousSystem', 'SubconsciousPwn', 'TetherWatchdog'],
        'hardware': ['hardware.display', 'hardware.auto_mood'],
        'error':    None,  # Use level filter instead
        'audit':    None,  # Read from JSONL
    }
    
    cmd = ["journalctl", "-u", "gotchi", f"-n{lines}", "--no-pager"]
    if since:
        cmd += ["--since", f"-{since}"]
    
    if filter == 'tail':
        cmd.append("-f")
        subprocess.run(cmd)
    elif filter == 'error':
        result = subprocess.run(cmd, capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if any(w in line for w in ['ERROR', 'CRITICAL', 'WARNING']):
                click.echo(line)
    elif filter in MODULE_FILTERS and MODULE_FILTERS[filter]:
        result = subprocess.run(cmd, capture_output=True, text=True)
        keywords = MODULE_FILTERS[filter]
        for line in result.stdout.splitlines():
            if any(k in line for k in keywords):
                click.echo(line)
    elif filter == 'audit':
        _show_audit_log(lines)
    else:
        subprocess.run(cmd)
```

---

### 6.2 — Rich-based colorized output for `gotchi logs error`

```python
from rich.console import Console
from rich.text import Text

console = Console()

LEVEL_COLORS = {
    'ERROR':    'bold red',
    'CRITICAL': 'bold white on red',
    'WARNING':  'yellow',
    'INFO':     'green',
    'DEBUG':    'dim',
}

def colorize_log_line(line: str) -> Text:
    text = Text(line)
    for level, style in LEVEL_COLORS.items():
        if level in line:
            text.stylize(style)
            break
    return text
```

---

### 6.3 — Log retention policy

| Log type | Location | Recommended cap |
|---|---|---|
| systemd journald | `/var/log/journal/` | 50MB (set in `/etc/systemd/journald.conf`) |
| Audit JSONL | `logs/commands.jsonl` | RotatingFileHandler, 5MB × 3 files |
| Rate limits | `rate_limits.json` | No rotation needed (tiny, self-managing) |

**Recommended `/etc/systemd/journald.conf` additions:**
```ini
[Journal]
SystemMaxUse=50M
SystemKeepFree=100M
MaxRetentionSec=7day
```

---

### 6.4 — LLM call structured log (future `gotchi logs llm` feed)

Add this to `litellm_connector.py` after a successful completion:

```python
log.info(
    "[LLM] call complete | model=%s latency_ms=%d tokens_in=%d tokens_out=%d turn=%d",
    self.model, latency_ms, tokens_in, tokens_out, turn + 1
)
```

This gives `gotchi logs llm` a clean, parseable stream of every LLM call with performance data.

---

## Appendix — Files Audited

| File | Role |
|---|---|
| [`src/main.py`](../../../src/main.py) | Root `logging.basicConfig()` setup |
| [`src/core/cli/commands/core.py`](../../../src/core/cli/commands/core.py) | `gotchi logs` command implementation |
| [`src/core/litellm_connector.py`](../../../src/core/litellm_connector.py) | LLM call logging, debug dumps |
| [`src/core/rate_limits.py`](../../../src/core/rate_limits.py) | Rate limit logging (well done) |
| [`src/audit_logging/command_logger.py`](../../../src/audit_logging/command_logger.py) | JSONL audit trail |
| [`src/hardware/bettercap_listener.py`](../../../src/hardware/bettercap_listener.py) | NervousSystem, rogue `basicConfig` |
| [`src/hardware/subconscious_pwn.py`](../../../src/hardware/subconscious_pwn.py) | SubconsciousPwn, rogue `basicConfig` |
| [`src/bot/discord_bot.py`](../../../src/bot/discord_bot.py) | Discord handlers (no audit logging) |
