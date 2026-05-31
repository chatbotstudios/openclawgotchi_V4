---
summary: "Workspace template for BOOT.md"
title: "BOOT.md template"
read_when:
  - Adding a BOOT.md checklist
---

# BOOT.md

Add short, explicit instructions for what the Gotchi should do on startup (e.g., enable `hooks.internal.enabled`, run telemetry check). 

If the task sends a message, use the message tool and then reply with the exact silent token `NO_REPLY` / `no_reply`.

## ⚠️ Hardware Safety Boot Directives

1. **Verify Resources First:** On startup, run a quick resource diagnostic (check free RAM and current CPU temp). If temperature exceeds 70°C or RAM is <50MB, log an alert but do not initiate heavy background loops or passive WiFi scans.
2. **Rate Limit Boot Screen Flashes:** Avoid refreshing the E-Ink display multiple times in rapid succession during boot phases. Give the hardware SPI interfaces time to stabilize and initialize (rate-limit boot refreshes).
3. **Low Power Boot Behavior:** If telemetry registers low battery state on boot, prioritize radio silence and decrease cron frequency immediately.

## Related

- [Agent workspace](/concepts/agent-workspace)
- [Hardware Limits and Safety Guidelines](file:///Users/js66/.gemini/antigravity-ide/scratch/openclawgotchi_V4/docs/ai_instructions/hardware_limits_and_safety.md)
