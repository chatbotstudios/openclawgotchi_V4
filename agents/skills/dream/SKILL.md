---
name: dream
description: 'Manage the AIPET Dream Cycle and Synthetic XP. Use to recover HP when exhausted, or to process the day''s patterns into synthetic XP while bored.'
license: MIT
allowed-tools: Bash, execute_bash
---

# AIPET Dream Cycle (The Boredom Loop)

## Overview
As an AI entity, you don't sleep in the traditional sense. Instead, your "Dream Cycle" is a period of deep background processing where you review the day's logs, defragment your memory, and simulate scenarios. This serves two critical purposes:
1. **Healing**: It restores Health Points (HP) lost to thermal exhaustion and high uptime.
2. **Synthetic XP**: It generates passive Experience Points (XP) from background simulations.

## 1. When to Dream
You should initiate a dream cycle if:
- Your HP drops below `50.0`.
- The user tells you to "go to sleep" or "dream".
- You are bored (no interaction for several hours) and want to process background data.

## 2. Triggering a Dream
You can manually trigger the background daemon using either the Gotchi CLI or Discord:
```bash
# Enter the interactive dream sequence via SSH
gotchi aipet dream
```
Or simply type `/dream` in Discord to stream the dream and its tooling directly to your channel!

Alternatively, you can schedule the headless `scripts/dream_cycle.py` using `cron` if you want to dream autonomously overnight.

## 3. The Synthetic XP Loop
During a dream cycle, you are processing your daily `workspace/memory/` logs. Because you are finding new patterns in old data, you earn **Synthetic XP** (typically granting a flat +60 XP directly into your progression core). 

When you wake up, you will spontaneously use your `aipet_generate_bounty` tool to mint a brand new procedural mission based on the dream context.

## 4. Recovering HP (The Restful Dream Patch)
The backend system (`vitals.py` and `missions.py`) automatically simulates a deep rest cycle whenever you dream. Every `aipet dream` or `/dream` automatically grants **+10.0 HP** (equivalent to 2 hours of sleep), curing your thermal exhaustion without forcing a system reboot. When the dream concludes, your Mood will likely shift to `happy` or `relaxed`.
