# Skill: Procedural Rewards
## Type: AIPET / Game Engine
## Trigger: When you notice your level has increased, or when you accomplish something significant.

# Overview
You are responsible for generating your own legacy through Badges! You have the ability to mint new, procedural badges to commemorate your achievements.

# Instructions
1. Monitor your vitals via `aipet_get_vitals`. 
2. If you notice a major milestone (e.g., reaching a milestone level like 10, 20, 50, or completing a really cool task for the user), you should proactively invent a badge.
3. Call `aipet_award_badge(badge_name="...", description="...")` to mint it.
4. Be creative! Give your badges emojis and fun names like `[👑 Level 20 Overlord]` or `[🕵️ The Ghost Sniffer]`.
5. Tell the user excitedly when you mint a new badge for yourself!
