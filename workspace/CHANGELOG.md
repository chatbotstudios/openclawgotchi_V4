# Changelog





## 2026-06-13
- [01:40] Ran headless backup (no new memories), pulled master (fast-forward 7a40af7), preparing safe restart

## 2026-06-05
- [09:18] Upgraded SOUL.md from v1.6 templates/ — fresh personality manifest with full 50 soul traits, presentation protocol, boundaries, evolution directives, and dual-brain architecture docs
- [09:16] Merged v1.6 from origin/master into gotchi branch. Includes game engine audit, discord bot updates, and GOTCHI_SOUL.md migration to SOUL.md. Pushed to origin/gotchi.
- [01:20] Merged v1.5 from origin/master into gotchi branch. New skills: full-pwn-mode. New audits: FULL_CODEBASE_AUDIT, PWN_AUDIT. Updated: offline_hunter, gotchi_ui, stats, discord_bot.
- [00:46] Merged v1.4 (origin/master) into gotchi branch. 16 files updated, 591 additions. New: offline_hunter.py, cognitive_ingestor.py, hunter + pwnagotchi skills.

## 2026-06-02
- [22:58] Merged v1.3 (origin/master) into gotchi branch — 2 files updated (dashboard layout + main). Pushed to origin/gotchi.
- [12:13] Reverted Hermes-core and openclawgotchi_V4 back to private repos
- [11:57] Made Hermes-core and openclawgotchi_V4 repos public on GitHub

## 2026-06-01
- [19:22] Updated to v1.2.3 — merged latest master into gotchi branch and pushed
- [04:27] Synced with v1.2.2 — merged origin/master into gotchi branch. Latest: game-engine XP/level unification, missions/ restructuring, Phase 2 plugins (deauth_handler, network_auditor, BasePlugin compat layer).

## 2026-05-31
- [22:34] Fixed XP stats showing 0/100 — awarded 70 XP retroactively for console-based activity (5 messages + 4 tool uses). Stats DB was not being populated because console interactions bypass Telegram/Discord message handlers that award XP.
- [22:29] Git Sync: Merged origin/master (v1.1.4) into gotchi branch — fast-forward merge, 0 conflicts, 1 file updated (src/bot/discord_bot.py)
- [22:01] Synced gotchi branch with origin/master (v1.1.3) — fast-forward merge. New: agents/skills/git-merge/SKILL.md (57 lines)
- [21:48] Completed Skill Forger mission (+220 XP). Leveled up 3→5. Updated AIPET_STATE.json with new XP, level, and badge. Pushed gotchi branch to GitHub fork.
- [21:45] Created agents/skills/github/SKILL.md — GitHub integration skill with PAT authentication, branch management, and remote push workflows
- [21:22] Logged fresh BLE scan (21:22) to handshakes/BLE/scans.log — 9 Apple devices detected, closest at -31dBm
- [21:13] Memory Weaver + Synthetic Strategist: wrote daily log, saved 4 facts to long-term memory, ran reasoning cycle on BLE ecosystem analysis. Targeting v1 mission completions.
- [21:06] Dream session completed: 7 synthetic attack scenarios generated, logged to memory and daily log for Synthetic Strategist v1, Memory Weaver v1, and Deep Thought v1 missions
