"""
Heartbeat — periodic tasks, auto-mood, XP, bot_mail, reflection.
"""

import logging
import os
import sqlite3
from typing import Optional

from config import GROUP_CHAT_ID, get_admin_id, PROJECT_DIR
from db.memory import get_history, get_pending_tasks, delete_pending_task, save_message
from hardware.display import parse_and_execute_commands
from hardware.auto_mood import apply_auto_mood, get_auto_mood
from db.stats import on_heartbeat, get_status_bar, get_stats_summary
from core.router import get_router
from core.base import RateLimitError
from hooks.runner import run_hook, HookEvent

log = logging.getLogger(__name__)

# Bot mail config
DB_PATH = PROJECT_DIR / "gotchi.db"
# Bot identity — read from env, defaults to generic
MY_NAME = os.environ.get("BOT_NAME", "gotchi").lower().replace(" ", "-")
SIBLING_BOT = os.environ.get("SIBLING_BOT_NAME", "")  # Optional sibling for mail


def _sanitize_reflection_text(text: str) -> str:
    """Keep only the reflection text (strip tool usage, headers, and status boilerplate)."""
    if not text:
        return ""
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        lower = stripped.lower()
        if lower.startswith("**heartbeat") or lower.startswith("heartbeat"):
            continue
        if lower.startswith("**system") or lower.startswith("system:"):
            continue
        if lower.startswith("**рефлек") or lower.startswith("рефлек"):
            continue
        if stripped.startswith("---"):
            continue
        lines.append(stripped)
    return "\n".join(lines).strip()


def _get_heartbeat_target_chat_id() -> int:
    """Choose where to send heartbeat reflection."""
    if GROUP_CHAT_ID:
        return GROUP_CHAT_ID
    return get_admin_id() or 0


def get_unread_mail() -> list[dict]:
    """Get unread mail for this bot from brother."""
    if not DB_PATH.exists():
        return []
    
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, from_bot, message, timestamp FROM bot_mail WHERE to_bot=? AND read_at IS NULL ORDER BY id ASC",
            (MY_NAME,)
        )
        rows = cursor.fetchall()
        
        if rows:
            ids = [r[0] for r in rows]
            placeholders = ",".join("?" * len(ids))
            conn.execute(f"UPDATE bot_mail SET read_at=CURRENT_TIMESTAMP WHERE id IN ({placeholders})", ids)
            conn.commit()
        
        conn.close()
        return [{"id": r[0], "from": r[1], "message": r[2], "timestamp": r[3]} for r in rows]
        
    except Exception as e:
        log.error(f"Failed to check bot_mail: {e}")
        return []


def send_mail(to_bot: str, message: str) -> bool:
    """Send mail to another bot (sibling bot)."""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO bot_mail (from_bot, to_bot, message, sender) VALUES (?, ?, ?, ?)",
            (MY_NAME, to_bot, message, MY_NAME)
        )
        conn.commit()
        conn.close()
        log.info(f"Sent mail to {to_bot}")
        return True
    except Exception as e:
        log.error(f"Failed to send mail: {e}")
        return False


def process_command_mail(message: str) -> Optional[str]:
    """
    Process command mails from brother.
    Format: CMD:<command> [args]
    Returns response message or None if not a command.
    """
    if not message.startswith("CMD:"):
        return None
    
    cmd = message[4:].strip().upper()
    router = get_router()
    
    if cmd == "PRO":
        if not router.force_lite:
            return "Already in Pro mode 🧠"
        router.force_lite = False
        log.info("Remote command: switched to Pro mode")
        return "Switched to Pro mode! 🧠 Heavy thinking enabled."
    
    elif cmd == "LITE":
        if router.force_lite:
            return "Already in Lite mode ⚡"
        router.force_lite = True
        log.info("Remote command: switched to Lite mode")
        return "Switched to Lite mode! ⚡ Fast & free."
    
    elif cmd == "STATUS":
        stats = get_stats_summary()
        mood, _ = get_auto_mood()
        mode = "Lite" if router.force_lite else "Pro"
        return (
            f"Status Report:\n"
            f"Level {stats['level']} {stats['title']} ({stats['xp']} XP)\n"
            f"Mode: {mode}\n"
            f"Mood: {mood}\n"
            f"Messages: {stats['messages']} | Days: {stats['days_alive']}"
        )
    
    elif cmd == "PING":
        return "PONG! 🏓 I'm alive, brother!"
    
    elif cmd.startswith("FACE:"):
        face = cmd[5:].strip().lower()
        try:
            from hardware.display import show_face
            show_face(face, "From brother")
            return f"Face set to: {face}"
        except Exception as e:
            return f"Failed to set face: {e}"
    
    return f"Unknown command: {cmd}. Try: PRO, LITE, STATUS, PING, FACE:<mood>"


async def process_pending_tasks(send_message_func):
    """Retry pending tasks from queue."""
    tasks = get_pending_tasks()
    if not tasks:
        return
    
    log.info(f"Processing {len(tasks)} pending tasks...")
    
    # Avoid overload — process only a few per heartbeat
    MAX_TASKS = 3
    
    for task_id, chat_id, text, sender, is_group in tasks[:MAX_TASKS]:
        try:
            router = get_router()
            history = get_history(chat_id)
            if history:
                history = history[:-1]
            
            response, connector = await router.call(text, history)
            
            # Handle error responses
            if response.startswith("Error:"):
                if send_message_func:
                    await send_message_func(chat_id, f"🔔 [Delayed Reply]\n{response}")
                delete_pending_task(task_id)
                continue
            
            # Parse hardware commands
            clean_text, cmds = parse_and_execute_commands(response)
            
            # Fallback face if none provided
            if not cmds.get("face"):
                try:
                    from hardware.display import show_face
                    show_face(mood="happy", text=clean_text[:50] if clean_text else "...")
                except Exception:
                    pass
            
            # Execute memory command
            if cmds.get("remember"):
                try:
                    from db.memory import add_fact
                    add_fact(cmds["remember"], "auto_memory")
                except Exception:
                    pass
            
            # Execute mail command
            if cmds.get("mail") and SIBLING_BOT:
                send_mail(SIBLING_BOT, cmds["mail"])
            
            # Save response to history
            save_message(chat_id, "assistant", response)
            
            # Send delayed reply
            msg = clean_text if clean_text.strip() else response
            if send_message_func:
                await send_message_func(chat_id, f"🔔 [Delayed Reply]\n{msg}")
            
            delete_pending_task(task_id)
            from db.stats import on_task_completed
            on_task_completed()
        
        except RateLimitError:
            log.info("Still rate limited, keeping task in queue")
            break
        except Exception as e:
            log.error(f"Task failed: {e}")
            delete_pending_task(task_id)


def _extract_recent_reflection_snippets(n: int = 5) -> list[str]:
    """Pull the last N heartbeat reflection snippets from daily logs."""
    try:
        from memory.flush import get_recent_daily_logs
        logs = get_recent_daily_logs(days=3)
        snippets = []
        for line in logs.splitlines():
            if "[Heartbeat Reflection]" in line:
                text = line.split("[Heartbeat Reflection]")[-1].strip()
                if text:
                    snippets.append(text[:120])
        return snippets[-n:]
    except Exception:
        return []


async def send_heartbeat(send_message_func=None):
    """
    Periodic heartbeat: auto-mood, XP, mail check, reflect.
    Returns: reflection_text (str)
    """
    run_hook(HookEvent(event_type="heartbeat", action="start"))

    # 0. Retrieve unsurfaced feedback events
    try:
        from db.memory import get_unsurfaced_feedback
        feedback_events = get_unsurfaced_feedback()
        feedback_ids = [f["id"] for f in feedback_events]
    except Exception:
        feedback_events = []
        feedback_ids = []

    # 1. Apply auto-mood first
    mood, mood_text = apply_auto_mood()

    # 2. Award heartbeat XP
    on_heartbeat()
    status_bar = get_status_bar()
    log.info(f"Heartbeat XP awarded. {status_bar}")

    # 3. Process pending queue
    await process_pending_tasks(send_message_func)

    # 4. Summarize recent conversations (LLM)
    try:
        from memory.flush import get_chats_with_recent_messages, summarize_and_save
        recent_chats = get_chats_with_recent_messages()
        if recent_chats:
            log.info(f"Summarizing {len(recent_chats)} chat(s) with recent activity")
            for chat_id in recent_chats[:3]:  # Max 3 chats to avoid overload
                saved = await summarize_and_save(chat_id)
                if saved:
                    log.info(f"Saved summary for chat {chat_id}")
    except Exception as e:
        log.warning(f"Conversation summarization failed: {e}")

    # 4b. Knowledge crystallization (autonomous — runs once per 24h)
    crystallized_count = 0
    try:
        from memory.knowledge import crystallize_knowledge
        from config import BOT_NAME, OWNER_NAME
        crystallized_count = await crystallize_knowledge(BOT_NAME, OWNER_NAME or "the owner")
        if crystallized_count:
            log.info(f"Crystallized {crystallized_count} knowledge insights")
    except Exception as e:
        log.warning(f"Knowledge crystallization failed: {e}")
    
    # 5. Check for mail from brother
    unread_mail = get_unread_mail()
    mail_section = ""
    command_responses = []
    
    if unread_mail:
        from db.stats import on_brother_chat
        on_brother_chat()
        log.info(f"Got {len(unread_mail)} new mail(s) from brother!")
        
        for m in unread_mail:
            # Check if it's a command
            cmd_response = process_command_mail(m['message'])
            if cmd_response:
                command_responses.append(cmd_response)
                if SIBLING_BOT:
                    send_mail(SIBLING_BOT, cmd_response)
            else:
                # Regular mail - add to prompt
                mail_section += f"- From {m['from']}: {m['message']}\n"
    
    # Get recent mail history for context
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute("SELECT from_bot, message FROM bot_mail ORDER BY id DESC LIMIT 5")
        history_rows = cursor.fetchall()
        conn.close()
        
        history_section = "\n## Recent Mail History\n"
        for h_from, h_msg in reversed(history_rows):
            history_section += f"- {h_from}: {h_msg[:100]}...\n"
    except Exception:
        history_section = ""
    
    # 7. Build unified reflection prompt using Workspace Architecture
    from core.prompts import build_system_context
    system_prompt = build_system_context(is_heartbeat=True)
    
    # 8. Add recent activity context (what happened, not just stats)
    context_parts = []

    # Last conversation summary
    try:
        admin_id = get_admin_id()
        if admin_id:
            recent = get_history(admin_id, limit=5)
            if recent:
                last_user = [m for m in recent if m["role"] == "user"]
                if last_user:
                    last_msg = last_user[-1]["content"][:150]
                    owner = OWNER_NAME or "Owner"
                    context_parts.append(f"Last thing {owner} said: \"{last_msg}\"")
    except Exception:
        pass

    # Today's activity log snippets
    try:
        from memory.flush import get_recent_daily_logs
        daily = get_recent_daily_logs(days=1)
        if daily and len(daily.strip()) > 20:
            context_parts.append(f"Today's log summary:\n{daily[:500]}...")
    except Exception:
        pass

    # Knowledge context
    try:
        from memory.knowledge import get_knowledge_context
        knowledge_ctx = get_knowledge_context()
        if knowledge_ctx:
            context_parts.append(f"Knowledge Context:\n{knowledge_ctx}")
    except Exception:
        pass

    # Anti-cycling snippets
    recent_snippets = _extract_recent_reflection_snippets(n=4)
    if recent_snippets:
        context_parts.append("Recent thoughts (avoid repeating these): " + "; ".join(recent_snippets))

    # Negative feedback context (allows the bot to learn from its mistakes)
    if feedback_events:
        feedback_lines = ["## Recent Negative Feedback from Owner (Correct these mistakes/behaviors):"]
        for f in feedback_events:
            feedback_lines.append(f"- Owner was unhappy with your response to: \"{f['user_text']}\" (which was: \"{f['bot_response']}\")")
        context_parts.append("\n".join(feedback_lines))

    # Assemble the final user-facing heartbeat instruction
    prompt = "## Heartbeat Context\n" + "\n\n".join(context_parts)
    prompt += "\n\n[Action: Reflect on your status, check mail, and internalize learnings. End with FACE: and SAY:]"
    
    # Choose target chat
    target_chat_id = _get_heartbeat_target_chat_id()
    
    # 7. Call LLM
    router = get_router()
    
    if router.lock.locked() and not router.force_lite:
        log.info("Heartbeat LLM busy (Claude). Attempting Lite fallback.")
        try:
            response = await router.litellm.call(prompt, [])
            connector = "litellm"
        except Exception as e:
            log.error(f"Heartbeat fallback failed: {e}")
            run_hook(HookEvent(event_type="heartbeat", action="error", text=str(e)))
            return
    else:
        response = None
        connector = None
    
    try:
        if response is None:
            async with router.lock:
                response, connector = await router.call(prompt, [], system_prompt=system_prompt)
        # 7. Print and run hook
        log.info(f"💓 [Heartbeat] [{connector}]: {response[:100]}")
        
        clean_text, commands = parse_and_execute_commands(response)
        reflection_text = _sanitize_reflection_text(clean_text)
        if not reflection_text:
            # Fallback to a minimal reflection so heartbeat always speaks
            reflection_text = "The system is quiet. I'm here, deep in thought. 🦋"
        
        # Save reflection to daily log (always, even if no commands)
        if reflection_text:
            try:
                from memory.flush import write_to_daily_log
                write_to_daily_log(f"[Heartbeat Reflection] {reflection_text[:300]}")
            except Exception as e:
                log.warning(f"Failed to save reflection: {e}")
        
        # Handle MAIL: reply to sibling bot
        if commands.get("mail") and SIBLING_BOT:
            send_mail(SIBLING_BOT, commands["mail"])
        
        # Send group message
        if commands.get("group"):
            try:
                if GROUP_CHAT_ID and send_message_func:
                    await send_message_func(GROUP_CHAT_ID, commands["group"])
                else:
                    log.warning("GROUP: command but GROUP_CHAT_ID not configured")
            except Exception as e:
                log.error(f"Failed to send GROUP message: {e}")
        
        # Send DM to admin
        if commands.get("dm") and admin_id and send_message_func:
            try:
                await send_message_func(admin_id, commands["dm"])
            except Exception as e:
                log.error(f"Failed to send DM: {e}")

        # Mark surfaced feedback events as seen
        if feedback_ids:
            try:
                from db.memory import mark_feedback_surfaced
                mark_feedback_surfaced(feedback_ids)
            except Exception:
                pass

        # Always send reflection to chat (owner by default)
        if reflection_text and target_chat_id and send_message_func:
            try:
                await send_message_func(target_chat_id, reflection_text)
            except Exception as e:
                log.error(f"Failed to send reflection message: {e}")

        # TRAITS drift — autonomously add one self-discovery (once per 7 days)
        try:
            from memory.knowledge import update_traits
            from config import BOT_NAME
            added = await update_traits(BOT_NAME)
            if added:
                log.info("Added new trait to TRAITS.md")
        except Exception as e:
            log.warning(f"Trait update failed: {e}")

        run_hook(HookEvent(event_type="heartbeat", action="complete", text=response[:100]))
                
    except Exception as e:
        log.error(f"Heartbeat error: {e}")
        # Final fallback: send a minimal reflection so the owner still hears from us
        try:
            target_chat_id = _get_heartbeat_target_chat_id()
            if target_chat_id and send_message_func:
                await send_message_func(target_chat_id, "Quiet hours. I'm processing data and staying alert. 🦋")
        except Exception:
            pass
        run_hook(HookEvent(event_type="heartbeat", action="error", text=str(e)))
        return "Quiet hours. I'm processing data and staying alert. 🦋"
