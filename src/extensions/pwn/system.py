from sdk.tool_builder import register_tool
from core.commands import clear_bot_history
import logging

log = logging.getLogger("Extensions.System")

@register_tool
def flush_context() -> str:
    """Clear the entire current conversation history and reset the LLM context window. 
    Use this when the user asks to 'forget', 'reset', or 'flush' history."""
    try:
        # We assume 0 for CLI and 1+ for Discord/Telegram
        # Since we don't easily have the chat_id here, we use a broad clear
        # In V2, we often use 0 as a placeholder or fetch it from context
        from core.litellm_connector import _get_cron_target_chat_id
        chat_id = _get_cron_target_chat_id() or 0
        
        clear_bot_history(chat_id)
        log.warning(f"Context Flush triggered for chat_id {chat_id}")
        return "✅ Context flushed. My memory of this conversation has been reset."
    except Exception as e:
        return f"Error flushing context: {e}"
