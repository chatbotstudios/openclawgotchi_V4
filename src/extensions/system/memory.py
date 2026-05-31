from sdk.tool_builder import register_tool

def _sanitize_string(s: str, max_len: int = 10000) -> str:
    if s is None:
        return ""
    return str(s)[:max_len]

@register_tool
def remember_fact(category: str, fact: str) -> str:
    """Save to long-term memory."""
    if not category or not fact:
        return "Error: Both category and fact are required"
    category = _sanitize_string(category, 50)
    fact = _sanitize_string(fact, 500)
    try:
        from db.memory import add_fact
        add_fact(fact, category)
        return f"✓ Remembered [{category}]: {fact}"
    except Exception as e:
        return f"Error: {e}"

@register_tool
def recall_facts(query: str = "", limit: int = 10) -> str:
    """Search long-term memory."""
    try:
        from db.memory import search_facts, get_recent_facts
        if query:
            facts = search_facts(query, limit)
        else:
            facts = get_recent_facts(limit)
        if not facts:
            return "No facts found"
        result = [f"[{f['category']}] {f['content']}" for f in facts]
        return "\n".join(result)
    except Exception as e:
        return f"Error: {e}"

@register_tool
def recall_messages(limit: int = 20) -> str:
    """Look back at recent conversation messages from the database."""
    try:
        from db.memory import get_history
        from config import get_admin_id
        chat_id = get_admin_id() or 0
        history = get_history(chat_id, limit=min(limit, 50))
        if not history:
            return "No messages found in history."
        lines = [f"Last {len(history)} messages:"]
        for msg in history:
            role = "👤 User" if msg["role"] == "user" else "🤖 Bot"
            lines.append(f"{role}: {msg['content'][:200]}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error reading messages: {e}"

@register_tool
def write_daily_log(entry: str) -> str:
    """Write to today's daily log."""
    try:
        from memory.flush import write_to_daily_log
        write_to_daily_log(entry)
        return "Logged to daily log"
    except Exception as e:
        return f"Error: {e}"

@register_tool
def check_mail() -> str:
    """Check unread mail from sibling/brother bot."""
    try:
        from bot.heartbeat import get_unread_mail
        mail = get_unread_mail()
        if not mail:
            return "No unread mail from brother."
        lines = [f"From {m['from']}: {m['message']}" for m in mail]
        return "\n".join(lines)
    except Exception as e:
        return f"Error checking mail: {e}"

@register_tool
def add_scheduled_task(name: str, interval_minutes: int = 0, run_in_minutes: int = 0, run_in_seconds: int = 0, message: str = "") -> str:
    """Add a scheduled/cron task."""
    try:
        from cron.scheduler import add_cron_job
        from core.litellm_connector import _get_cron_target_chat_id
        target_chat = _get_cron_target_chat_id() or 0
        
        if run_in_seconds > 0:
            job = add_cron_job(name=name, message=message, run_at=f"{run_in_seconds}s", delete_after_run=True, target_chat_id=target_chat)
            return f"Task added: ID: {job.id}"
        if run_in_minutes > 0:
            job = add_cron_job(name=name, message=message, run_at=f"{run_in_minutes}m", delete_after_run=True, target_chat_id=target_chat)
            return f"Task added: ID: {job.id}"
        elif interval_minutes > 0:
            job = add_cron_job(name=name, message=message, interval_minutes=interval_minutes, target_chat_id=target_chat)
            return f"Task added: ID: {job.id}"
        else:
            return "Error: specify time"
    except Exception as e:
        return f"Error: {e}"

@register_tool
def list_scheduled_tasks() -> str:
    """List all scheduled tasks."""
    try:
        from cron.scheduler import list_cron_jobs
        jobs = list_cron_jobs()
        if not jobs:
            return "No tasks"
        lines = [f"job_id='{job.id}' | {job.name}" for job in jobs]
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"

@register_tool
def remove_scheduled_task(job_id: str) -> str:
    """Remove a scheduled task by ID."""
    try:
        from cron.scheduler import remove_cron_job
        if remove_cron_job(job_id):
            return f"Removed task: {job_id}"
        return f"Task not found: {job_id}"
    except Exception as e:
        return f"Error: {e}"
