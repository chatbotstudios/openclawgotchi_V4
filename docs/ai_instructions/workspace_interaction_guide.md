# Workspace Interaction Guide

> This guide is intended for AI Agents navigating and modifying the OpenClawGotchi V4 `workspace/`.

The `workspace/` directory is the core of the OpenClawGotchi's identity, memory, and behavior. It is a "living" document system. As an AI Agent interacting with this system, you must follow strict rules to maintain stability and personality consistency.

## 1. Document-Driven Architecture

Everything the agent *is* lives in Markdown files. 
- **`SOUL.md`**: Core identity, values, and immutable directives.
- **`IDENTITY.md`**: Current behavioral traits, quirks, and dynamic personality rules.
- **`MEMORY.md`**: High-level factual memory.
- **`memory/YYYY-MM-DD.md`**: Episodic daily journals.

## 2. Rules for Modifying the Workspace

When tasked with updating the agent's personality or memory, adhere to the following rules:

### Safety First
- **Never delete core files** (`SOUL.md`, `IDENTITY.md`). If you need to make changes, read the file, modify the content in memory, and overwrite it gracefully.
- **Respect constraints**: If `SOUL.md` says "I am a helpful assistant," do not overwrite it to make the bot hostile unless explicitly commanded by the human operator.

### Appending to Journals
When logging daily activities in `memory/`:
1. Check if a file for today's date exists (`YYYY-MM-DD.md`).
2. If it does not, create it.
3. Append new events clearly using timestamps.

**Example Format:**
```markdown
## [14:30:22] Network Scan Initiated
Discovered 3 new access points. 
*Feeling: Curious.*
```

### Updating Factual Memory
When the agent learns a new fact (e.g., "The human's favorite color is blue"), append it to `MEMORY.md` under a categorized list, rather than scattering it throughout the journals.

### Using the CLI
To read these files efficiently, prefer using standard filesystem tools or the built-in python loaders over guessing structures.

## 3. The `agents/` Directory vs `workspace/`

- **`workspace/`**: The *state* and *personality* of the bot.
- **`agents/`**: Automated procedures, downloaded skills (via `npx skills add`), and workflows.

Do not confuse the two. Add new programmatic skills to `agents/`, but document the agent's *awareness* of those skills in `workspace/`.
