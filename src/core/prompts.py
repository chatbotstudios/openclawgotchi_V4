"""
Shared prompt loading logic for all LLM connectors.

Single source of truth: templates/ files
Both Claude CLI and LiteLLM use the same files.
"""


from config import PROJECT_DIR, WORKSPACE_DIR, CUSTOM_FACES_PATH
from hardware.system import get_stats_string
import json


def _load_available_faces() -> str:
    """Load list of all available ePaper faces for the system prompt."""
    available = []
    
    # Load defaults
    try:
        from ui.faces import DEFAULT_FACES
        available.extend(list(DEFAULT_FACES.keys()))
    except Exception:
        pass
        
    # Load customs
    if CUSTOM_FACES_PATH.exists():
        try:
            customs = json.loads(CUSTOM_FACES_PATH.read_text())
            available.extend(list(customs.keys()))
        except Exception:
            pass
            
    if not available:
        return ""
        
    return "You may use `FACE: <mood>` to change your e-Ink display. Available moods: [" + ", ".join(available) + "]"


def load_bot_instructions() -> str:
    """
    Load BOT_INSTRUCTIONS.md — the main system prompt.
    """
    workspace_file = WORKSPACE_DIR / "BOT_INSTRUCTIONS.md"
    if workspace_file.exists():
        return workspace_file.read_text()
    
    templates_file = PROJECT_DIR / "templates" / "BOT_INSTRUCTIONS.md"
    if templates_file.exists():
        return templates_file.read_text()
    
    return """You are an AI assistant on Raspberry Pi Zero 2W.
Use FACE: <mood> to express emotions. Be concise and expressive."""


def _load_workspace_file(name: str) -> str:
    """Load a file from templates/."""
    ws = WORKSPACE_DIR / name
    if ws.exists():
        return ws.read_text()
    tmpl = PROJECT_DIR / "templates" / name
    if tmpl.exists():
        return tmpl.read_text()
    return ""





def load_soul() -> str:
    return _load_workspace_file("SOUL.md")

def load_identity() -> str:
    return _load_workspace_file("IDENTITY.md")

def format_skills_for_prompt() -> str:
    """
    Format dynamically created custom tools for system prompt.
    Procedural skills (SKILL.md) are now handled by WorkspaceLoader.
    """
    from core.registry import get_tools_and_schemas
    
    lines = []
    
    # Load Python Tool Schemas (from extensions)
    try:
        _, schemas = get_tools_and_schemas()
        if schemas:
            lines.append("## Custom Python Tools (Active Extensions)")
            for tool in schemas:
                func = tool.get("function", {})
                name = func.get("name", "unknown")
                desc = func.get("description", "")[:80]
                lines.append(f"- **{name}**: {desc}")
            lines.append("")
    except Exception:
        pass
        
    return "\n".join(lines)


def _build_memory_context() -> str:
    """
    Build compact memory section for system prompt.
    Includes: recent facts (from /remember) + today's daily log (summaries).
    Kept small — summaries are already compressed.
    """
    sections = []
    
    # 1. Recent facts from /remember (last 5, compact)
    try:
        from db.memory import get_recent_facts
        facts = get_recent_facts(limit=5)
        if facts:
            lines = ["## Memory (things you've been told to remember)"]
            for f in facts:
                cat = f.get("category", "general")
                content = f.get("content", "")[:120]
                lines.append(f"- [{cat}] {content}")
            sections.append("\n".join(lines))
    except Exception:
        pass
    
    # 2. Today's daily log (contains heartbeat summaries + reflections)
    try:
        from memory.flush import get_recent_daily_logs
        logs = get_recent_daily_logs(days=1)  # Just today
        if logs and len(logs.strip()) > 20:  # Skip if just a date header
            # Truncate if too long (max ~500 chars)
            if len(logs) > 500:
                logs = logs[:500] + "\n... (truncated)"
            sections.append(f"## Recent Activity Log (internal)\n{logs}")
    except Exception:
        pass
    
    return "\n\n".join(sections)


def build_system_context(user_message: str = "", is_heartbeat: bool = False) -> str:
    """
    Build unified system context using OpenClaw Workspace Architecture.
    """
    from core.workspace import load_workspace_prompt
    
    parts = []
    
    # 1. Base Formatting Rules (Project Defaults)
    parts.append(load_bot_instructions())
    
    # 2. Unified Workspace Context (AGENTS, SOUL, IDENTITY, USER, TOOLS, SKILLS)
    # This follows the official OpenClaw injection order.
    parts.append(load_workspace_prompt(include_heartbeat=is_heartbeat))
    
    # 3. Available UI Faces
    available_faces = _load_available_faces()
    if available_faces:
        parts.append(available_faces)
    
    # 4. Active Python Extension Tools
    skills_text = format_skills_for_prompt()
    if skills_text:
        parts.append(skills_text)
    
    # 5. Long Term Memory & Logs
    memory_parts = _build_memory_context()
    if memory_parts:
        parts.append(memory_parts)
    
    # 6. System Status
    parts.append(
        "## System Status (internal diagnostics)\n"
        + get_stats_string()
    )
    
    return "\n\n---\n\n".join(parts)


def build_history_prompt(history: list[dict]) -> str:
    """Format conversation history for prompt."""
    if not history:
        return ""
    
    lines = ["\n--- Previous conversation ---"]
    for msg in history:
        role = "User" if msg["role"] == "user" else "Assistant"
        content = msg["content"][:500]  # Truncate long messages
        lines.append(f"{role}: {content}")
    
    return "\n".join(lines)


# How many recent messages to always show in conversation context
CONVERSATION_LAST_N = 5


def build_conversation_context(history: list[dict]) -> str:
    """
    Build a short "where we are" block for the system prompt:
    - Summary of what was discussed (before the last N messages)
    - Last N messages (user + assistant), including tool usage when present.

    "System" messages here = the single [Earlier: ...] summary injected by optimize_history.
    We skip that in the "last 5" list because we already show "Summary so far" above.
    Assistant messages often end with "Tool usage (N): ..." — we keep a longer preview so
    that tool usage is visible (useful context for the next turn).
    """
    # Only user/assistant for "recent" list (skip the one system msg = [Earlier: ...] summary)
    chat_turns = [m for m in history if m.get("role") in ("user", "assistant")]
    if not chat_turns:
        return ""
    
    try:
        from memory.summarize import summarize_old_messages
    except Exception:
        return ""
    
    last_n = CONVERSATION_LAST_N
    if len(chat_turns) <= last_n:
        summary_line = "Beginning of conversation."
        recent = chat_turns
    else:
        old_part = chat_turns[:-last_n]
        summary_line = summarize_old_messages(old_part)
        if not summary_line:
            summary_line = "Earlier messages in this chat."
        recent = chat_turns[-last_n:]
    
    # Preview length: longer for assistant so "Tool usage (N):" footer is usually included
    PREVIEW_USER = 200
    PREVIEW_ASSISTANT = 450  # enough for main reply + "Tool usage (1): add_scheduled_task(...)"
    
    lines = [
        "## Current conversation context",
        "",
        "**Summary so far:** " + (summary_line if summary_line.startswith("[") else summary_line),
        "",
        f"**Last {len(recent)} messages (most recent):**"
    ]
    for msg in recent:
        role = "User" if msg.get("role") == "user" else "Assistant"
        content = (msg.get("content") or "").strip()
        if role == "Assistant" and content.startswith("[Earlier:"):
            lines.append(f"- {role}: (summary of earlier turns)")
        else:
            cap = PREVIEW_ASSISTANT if role == "Assistant" else PREVIEW_USER
            preview = content[:cap] + ("..." if len(content) > cap else "")
            lines.append(f"- {role}: {preview}")
    
    return "\n".join(lines)
