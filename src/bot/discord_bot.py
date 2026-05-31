import logging
import asyncio
import random
import discord
from discord.ext import commands, tasks

# Suppress discord.client warnings about PyNaCl and davey (voice support)
logging.getLogger("discord.client").setLevel(logging.ERROR)

from config import (
    DISCORD_BOT_TOKEN, get_discord_allowed_users, 
    DISCORD_HEARTBEATS_CHANNEL, DISCORD_CHANNEL_ID, BOT_NAME,
    OWNER_NAME, SIBLING_BOT_NAME, HISTORY_LIMIT, MODEL_CONTEXT_TOKENS,
    DB_PATH, _env_flag
)
from db.memory import (
    save_message, get_history, clear_history, get_message_count,
    save_user, add_fact, search_facts, get_recent_facts
)
from hardware.display import parse_and_execute_commands, error_screen, show_face
from hardware.system import get_stats
from core.router import get_router
from db.stats import get_stats_summary
from memory.summarize import optimize_history
from hooks.runner import run_hook, HookEvent

log = logging.getLogger(__name__)

def _fire_discord_command_hook(interaction, command_name):
    hook_event = run_hook(HookEvent(
        event_type="command",
        user_id=interaction.user.id,
        chat_id=interaction.channel_id,
        username=interaction.user.name,
        action=f"/{command_name}"
    ))
    if hook_event and hasattr(hook_event, "messages") and hook_event.messages:
        return "\n\n" + "\n".join(hook_event.messages)
    return ""

def is_allowed(user_id: int) -> bool:
    allowed_users = get_discord_allowed_users()
    if not allowed_users:
        from config import ALLOW_ALL_USERS
        return bool(ALLOW_ALL_USERS)
    return user_id in allowed_users

class OpenClawDiscord(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Start syncing in the background after a short delay to avoid rate limits
        asyncio.create_task(self.delayed_sync())
            
        if DISCORD_HEARTBEATS_CHANNEL and DISCORD_HEARTBEATS_CHANNEL != "0":
            self.heartbeat_task.start()
        
        if _env_flag("AUTO_NIGHT_MODE", False):
            self.night_mode_task.start()

    async def delayed_sync(self):
        """
        Syncs slash commands with a retry mechanism to handle transient 503 errors.
        """
        # Wait for the bot to stabilize first
        await asyncio.sleep(10)
        
        max_retries = 5
        retry_delay = 30 # Initial delay
        
        for attempt in range(max_retries):
            log.info(f"Syncing Discord Slash Commands (Attempt {attempt + 1}/{max_retries})...")
            try:
                await self.tree.sync()
                log.info("Slash Commands synced successfully.")
                return
            except discord.HTTPException as e:
                if e.status == 503:
                    log.warning(f"Discord API 503 (Service Unavailable) during sync. Retrying in {retry_delay}s...")
                elif e.status == 429:
                    log.warning(f"Discord API 429 (Rate Limited) during sync. Retrying in {retry_delay}s...")
                else:
                    log.warning(f"HTTP error during command sync: {e}")
                    break # Non-transient error?
            except Exception as e:
                log.warning(f"Unexpected error during command sync: {e}")
                break
                
            await asyncio.sleep(retry_delay)
            retry_delay *= 2 # Exponential backoff
            
        log.error("Failed to sync Slash Commands after multiple attempts.")

    @tasks.loop(hours=4)
    async def heartbeat_task(self):
        channel_id = int(DISCORD_HEARTBEATS_CHANNEL)
        channel = self.get_channel(channel_id)
        if not channel: return
            
        async def send_to_discord(chat_id, text):
            try:
                target = self.get_channel(int(chat_id)) or self.get_user(int(chat_id))
                if target: await target.send(text)
                else: await channel.send(text)
            except Exception as e:
                log.error(f"Failed to route heartbeat message to {chat_id}: {e}")
                
        from bot.heartbeat import send_heartbeat
        await send_heartbeat(send_message_func=send_to_discord)
        stats = get_stats()
        await channel.send(f"💓 **System Vitals**\nUptime: {stats.uptime} | Temp: {stats.temp} | Mem: {stats.memory}")

    @tasks.loop(minutes=15)
    async def night_mode_task(self):
        try:
            from hardware.night_mode import update_night_mode_state
            await asyncio.to_thread(update_night_mode_state)
        except Exception as e:
            log.error(f"NightMode task error: {e}")

    async def on_ready(self):
        log.info(f"Discord Bot connected as {self.user}")
        if not hasattr(self, "_awakened"):
            self._awakened = True
            asyncio.create_task(self.awakening_pulse())
        else:
            log.info("Bot reconnected, skipping awakening pulse.")

    async def awakening_pulse(self):
        try:
            stats = get_stats()
            router = get_router()
            prompt = (
                f"You just woke up. You are {BOT_NAME}. Vitals: Temp {stats.temp}, Uptime {stats.uptime}, Memory {stats.memory}. "
                "All systems are NOMINAL. Greet the operator with one short, tactical, but cute sentence. "
                "Keep it under 60 characters. End with FACE: <mood> (happy, cool, smart, or sly)."
            )
            response, _ = await router.call(prompt, history=[])
            clean_text, cmds = parse_and_execute_commands(response)
            mood = cmds.get("face") or "happy"
            display_text = cmds.get("display") or clean_text
            
            # Prevent double SAY: SAY:
            stripped_say = display_text[4:].strip() if display_text.startswith("SAY:") else display_text
            
            show_face(mood, f"SAY:{stripped_say} | STATUS: Nominal")
            
            from ui.faces import get_all_faces
            faces = get_all_faces()
            face_data = faces.get(mood, faces["happy"])
            face_str = random.choice(face_data) if isinstance(face_data, list) else face_data
            
            # Post raw LLM message to #general
            general_channel = None
            for g in self.guilds:
                for c in g.text_channels:
                    if c.name.lower() == "general":
                        general_channel = c
                        break
                if general_channel: break
            
            if general_channel:
                formatted_general_msg = f"{clean_text}\n\n`{face_str}`\n\n```\nFACE: {face_str} ({mood})\nSAY: {stripped_say}\n```"
                await general_channel.send(formatted_general_msg)
            
            if DISCORD_HEARTBEATS_CHANNEL and DISCORD_HEARTBEATS_CHANNEL != "0":
                channel = self.get_channel(int(DISCORD_HEARTBEATS_CHANNEL))
                if channel:
                    await channel.send(f"`{face_str}` **{BOT_NAME} Awakening:** {clean_text}")
        except Exception as e:
            log.warning(f"Failed dynamic awakening: {e}")
            show_face("happy", "SAY:Systems Nominal! | STATUS: Online")

    async def on_message(self, message):
        log.info(f"[Debug on_message] Event from '{message.author}' (ID: {message.author.id}) in #{message.channel} (ID: {message.channel.id}). Content: '{message.content}'")
        if message.author.bot: return
        if not is_allowed(message.author.id): return
        
        if DISCORD_CHANNEL_ID and DISCORD_CHANNEL_ID != "0":
            if message.channel.id != int(DISCORD_CHANNEL_ID):
                return
        
        # Tactical Deduplication: Don't process the same message ID twice
        if not hasattr(self, "_processed_msgs"):
            self._processed_msgs = set()
        if message.id in self._processed_msgs:
            return
        self._processed_msgs.add(message.id)
        # Keep cache small (last 100 msgs)
        if len(self._processed_msgs) > 100:
            self._processed_msgs.remove(next(iter(self._processed_msgs)))

        user_text = message.content
        if self.user:
            user_text = user_text.replace(f"<@{self.user.id}>", "")
            user_text = user_text.replace(f"<@!{self.user.id}>", "")
        user_text = user_text.strip()
        
        if not user_text or user_text.startswith("/"): return
        conv_id = message.channel.id
        sender = message.author.display_name
        
        hook_event = run_hook(HookEvent(
            event_type="message",
            user_id=message.author.id,
            chat_id=message.channel.id,
            username=sender,
            text=user_text
        ))
        
        save_user(message.author.id, message.author.name, sender, "")
        save_message(conv_id, "user", user_text)
        
        history = get_history(conv_id)
        if history: history = history[:-1]
        history = optimize_history(history)
        router = get_router()
        try:
            log.info(f"[{sender}] -> {user_text[:80]}")
            response, connector = await router.call(user_text, history)
            log.info(f"[{sender}] <- [{connector}] {response[:80]}")
            tool_footer = ""
            if "__TOOL_FOOTER__" in response:
                parts = response.split("__TOOL_FOOTER__", 1)
                response = parts[0].rstrip()
                tool_footer = parts[1].strip()
            clean_text, cmds = parse_and_execute_commands(response)
            from ui.faces import get_all_faces
            faces = get_all_faces()
            face_key = cmds.get("face") or "happy"
            face_data = faces.get(face_key, faces.get("happy", ["(◕‿◕)"]))
            face_str = random.choice(face_data) if isinstance(face_data, list) else face_data
            debug_lines = []
            if cmds.get("face"): debug_lines.append(f"FACE: {face_str} ({face_key})")
            if cmds.get("display"):
                debug_text = cmds["display"]
                if debug_text.startswith("SAY:"): debug_lines.append(f"SAY: {debug_text[4:]}")
                else: debug_lines.append(f"DISPLAY: {debug_text}")
            debug_footer = ""
            if debug_lines: 
                debug_block = "\n".join(debug_lines)
                debug_footer = f"\n\n```\n{debug_block}\n```"
            if not cmds.get("face"): show_face(mood="happy", text=clean_text[:50] if clean_text else "...")
            save_message(conv_id, "assistant", response)
            status_block = ""
            status_header = f"{BOT_NAME.upper()} — STATUS"
            if status_header in clean_text:
                parts = clean_text.split(status_header, 1)
                clean_text = parts[0].strip()
                status_block = f"🤖 {status_header}" + parts[1]
            final_msg = f"{clean_text}\n\n`{face_str}`" if clean_text else f"`{face_str}`"
            if debug_footer: final_msg += debug_footer
            if status_block: final_msg += f"\n\n{status_block}"
            if tool_footer: final_msg += f"\n\n{tool_footer}"
            if hook_event and hasattr(hook_event, "messages") and hook_event.messages:
                final_msg += "\n\n" + "\n".join(hook_event.messages)
            if len(final_msg) > 2000:
                for i in range(0, len(final_msg), 2000): await message.channel.send(final_msg[i:i+2000])
            else: await message.channel.send(final_msg)
        except Exception as e:
            log.error(f"LLM Error: {e}")
            error_screen(str(e))
            await message.channel.send(f"Error: {e}")

bot_instance = OpenClawDiscord()

@bot_instance.tree.command(name="start", description="Start interacting with OpenClawGotchi")
async def cmd_start(interaction: discord.Interaction):
    if not is_allowed(interaction.user.id): return await interaction.response.send_message("Access denied.", ephemeral=True)
    await interaction.response.send_message(f"Hi {interaction.user.display_name}! I'm 🦋OpenClawGotchi🦋, your edge AI companion.\nUse `/status`, `/clear`, `/xp` or just talk to me in this channel!")

@bot_instance.tree.command(name="status", description="Show system and XP stats")
async def cmd_status(interaction: discord.Interaction):
    if not is_allowed(interaction.user.id): return await interaction.response.send_message("Access denied.", ephemeral=True)
    await interaction.response.defer()
    
    stats = get_stats()
    gotchi_stats = get_stats_summary()
    router = get_router()
    mode = "Lite ⚡" if router.force_lite else "Pro 🧠"
    
    # Active AI/LLM model resolution
    active_model = router.litellm.model if router.force_lite else router.pro_llm.model
    if active_model and "/" in active_model:
        active_model = active_model.split("/")[-1]
    active_model_str = active_model.upper() if active_model else "UNKNOWN"
    
    from ui.faces import get_all_faces
    faces = get_all_faces()
    smart_faces = faces.get("smart", ["(✜‿‿✜)"])
    face_str = random.choice(smart_faces) if isinstance(smart_faces, list) else smart_faces
    
    msg = (f"`{face_str}` **{BOT_NAME.upper()} — STATUS**\n"
           f"🎮 Level: {gotchi_stats['level']} ({gotchi_stats.get('title', 'Newborn')})\n"
           f"⭐ XP: {gotchi_stats['xp_in_level']}/{gotchi_stats['xp_needed_this_level']}\n"
           f"💬 Messages: {gotchi_stats['messages']}\n"
           f"🌡️ Temperature: {stats.temp}\n"
           f"💾 RAM Free: {stats.memory}\n"
           f"🤖 AI/LLM Model: {active_model_str}\n"
           f"🧠 Mode: {mode}")
    
    # Slow hardware update
    show_face("smart", f"SAY:Status check! | STATUS:{mode}")
    notifications = _fire_discord_command_hook(interaction, "status")
    await interaction.followup.send(msg + notifications)

@bot_instance.tree.command(name="clear", description="Wipe conversation history")
async def cmd_clear(interaction: discord.Interaction):
    if not is_allowed(interaction.user.id): return await interaction.response.send_message("Access denied.", ephemeral=True)
    clear_history(interaction.channel_id)
    await interaction.response.send_message("History cleared.")

@bot_instance.tree.command(name="xp", description="Show XP rules and level progress")
async def cmd_xp(interaction: discord.Interaction):
    if not is_allowed(interaction.user.id): return await interaction.response.send_message("Access denied.", ephemeral=True)
    await interaction.response.defer()
    
    from db.stats import get_level_progress, get_xp_rules
    prog = get_level_progress()
    rules = get_xp_rules()
    xp_in, xp_need = prog.get("xp_in_level", 0), prog.get("xp_needed_this_level", 1) or 1
    if prog["level"] >= prog.get("max_level", 20): xp_bar = "█" * 10 + " MAX"; progress_line = f"Lv{prog['level']} {prog['title']} — {xp_bar}"
    else:
        filled = min(10, int(10 * xp_in / xp_need)); xp_bar = "█" * filled + "░" * (10 - filled)
        progress_line = f"Lv{prog['level']} {prog['title']} — {xp_bar} {xp_in}/{xp_need} to Lv{prog['level'] + 1}"
    lines = ["📊 **XP & Levels**\n", progress_line, f"Total XP: {prog['xp']}\n", "**How you earn XP:**"]
    for action, amount, desc in rules: lines.append(f"• {action}: **+{amount}** — {desc}")
    await interaction.followup.send("\n".join(lines))

@bot_instance.tree.command(name="context", description="View or trim model context window")
async def cmd_context(interaction: discord.Interaction, action: str = None):
    if not is_allowed(interaction.user.id): return await interaction.response.send_message("Access denied.", ephemeral=True)
    if action == "trim":
        import sqlite3
        conn = sqlite3.connect(str(DB_PATH)); conn.execute("DELETE FROM messages WHERE user_id = ? AND id NOT IN (SELECT id FROM messages WHERE user_id = ? ORDER BY id DESC LIMIT 3)", (interaction.channel_id, interaction.channel_id)); conn.commit(); conn.close()
        return await interaction.response.send_message("✂️ Trimmed! Kept last 3 messages.")
    elif action in ("summarize", "sum"):
        await interaction.response.defer()
        from memory.flush import summarize_conversation_with_llm, write_to_daily_log
        summary = await summarize_conversation_with_llm(get_history(interaction.channel_id))
        if summary: write_to_daily_log(f"[Manual Summary]\n{summary}"); await interaction.followup.send(f"📝 **Summary saved:**\n\n{summary}")
        else: await interaction.followup.send("No summary needed.")
        return
    msg_count = get_message_count(interaction.channel_id)
    history = get_history(interaction.channel_id)
    total_chars = sum(len(m.get("content", "")) for m in history); est_tokens = total_chars // 4
    usage_pct = min(100, (est_tokens * 100) // MODEL_CONTEXT_TOKENS); filled = min(10, (usage_pct * 10) // 100); bar = "█" * filled + "░" * (10 - filled)
    await interaction.response.send_message(f"📊 **Context Window**\n\n**Model window:** ~{est_tokens:,} / {MODEL_CONTEXT_TOKENS:,} tokens\n[{bar}] {usage_pct}%\nMessages: {len(history)}/{HISTORY_LIMIT}")

@bot_instance.tree.command(name="remember", description="Save a fact to long-term memory")
async def cmd_remember(interaction: discord.Interaction, category: str, fact: str):
    if not is_allowed(interaction.user.id): return await interaction.response.send_message("Access denied.", ephemeral=True)
    add_fact(fact, category)
    from memory.flush import write_to_daily_log
    write_to_daily_log(f"Remembered [{category}]: {fact}")
    notifications = _fire_discord_command_hook(interaction, "remember")
    await interaction.response.send_message(f"📝 Saved [{category}]: {fact}" + notifications)

@bot_instance.tree.command(name="recall", description="Search memory")
async def cmd_recall(interaction: discord.Interaction, query: str = None):
    if not is_allowed(interaction.user.id): return await interaction.response.send_message("Access denied.", ephemeral=True)
    await interaction.response.defer()
    
    facts = search_facts(query) if query else get_recent_facts(5)
    if not facts: return await interaction.followup.send("No facts found.")
    msg = "🔍 Results:\n\n"
    for f in facts: msg += f"[{f['timestamp'][:10]}] ({f['category']}) {f['content']}\n"
    notifications = _fire_discord_command_hook(interaction, "recall")
    await interaction.followup.send(msg + notifications)

@bot_instance.tree.command(name="memory", description="Database stats")
async def cmd_memory(interaction: discord.Interaction):
    if not is_allowed(interaction.user.id): return await interaction.response.send_message("Access denied.", ephemeral=True)
    await interaction.response.defer()
    
    import sqlite3
    conn = sqlite3.connect(str(DB_PATH)); cursor = conn.cursor()
    m_c = cursor.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    f_c = cursor.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
    conn.close()
    gotchi_stats = get_stats_summary()
    notifications = _fire_discord_command_hook(interaction, "memory")
    await interaction.followup.send(f"📊 **Memory Dashboard**\nMessages: {m_c}\nFacts: {f_c}\nXP: {gotchi_stats['xp']} (Lv{gotchi_stats['level']})" + notifications)

@bot_instance.tree.command(name="pro", description="Toggle Lite/Pro LLM modes")
async def cmd_pro(interaction: discord.Interaction):
    if not is_allowed(interaction.user.id): return await interaction.response.send_message("Access denied.", ephemeral=True)
    await interaction.response.defer()
    
    router = get_router()
    is_lite = router.toggle_lite_mode()
    
    # Slow hardware update
    show_face("cool" if is_lite else "smart", f"SAY: Switched! | MODE: {'L' if is_lite else 'P'}")
    await interaction.followup.send(f"✨ Mode: {'Lite ⚡' if is_lite else 'Pro 🧠'}")

@bot_instance.tree.command(name="cron", description="Add a scheduled task")
async def cmd_cron(interaction: discord.Interaction, name: str, interval: str, message: str):
    if not is_allowed(interaction.user.id): return await interaction.response.send_message("Access denied.", ephemeral=True)
    from cron.scheduler import add_cron_job
    if interval.endswith("m"): add_cron_job(name=name, message=message, run_at=interval, delete_after_run=True, target_chat_id=interaction.channel_id)
    else: add_cron_job(name=name, message=message, interval_minutes=int(interval), target_chat_id=interaction.channel_id)
    notifications = _fire_discord_command_hook(interaction, "cron")
    await interaction.response.send_message(f"⏰ Job added: {name}" + notifications)

@bot_instance.tree.command(name="pwn", description="Pwnagotchi Subconscious Control")
async def cmd_pwn(interaction: discord.Interaction, action: str = "status", target: str = None):
    if not is_allowed(interaction.user.id): return await interaction.response.send_message("Access denied.", ephemeral=True)
    await interaction.response.defer()
    from extensions.pwn.wifi import pwn_status, pwn_pause, pwn_crack, pwn_lock_target, pwn_show_qr
    action = action.lower()
    if action == "status": res = pwn_status()
    elif action == "pause": res = pwn_pause(int(target) if target else 5)
    elif action == "crack": res = pwn_crack(target) if target else pwn_crack()
    elif action == "lock": res = pwn_lock_target(target)
    elif action == "show_qr": res = pwn_show_qr(target)
    else: res = "Unknown action."
    await interaction.followup.send(f"📡 **Pwnagotchi:**\n```\n{res}\n```")

@bot_instance.tree.command(name="restart", description="Safely restart the OpenClawGotchi daemon")
async def cmd_restart(interaction: discord.Interaction):
    if not is_allowed(interaction.user.id): return await interaction.response.send_message("Access denied.", ephemeral=True)
    from extensions.system.commands import safe_restart
    await interaction.response.defer(); res = safe_restart(); await interaction.followup.send(res)

@bot_instance.tree.command(name="jobs", description="List or remove scheduled tasks")
async def cmd_jobs(interaction: discord.Interaction, action: str = None, job_id: str = None):
    if not is_allowed(interaction.user.id): return await interaction.response.send_message("Access denied.", ephemeral=True)
    await interaction.response.defer()
    
    from cron.scheduler import list_cron_jobs, remove_cron_job
    if action == "rm" and job_id:
        if remove_cron_job(job_id): return await interaction.followup.send(f"Removed job: {job_id}")
        return await interaction.followup.send("Job not found.")
    jobs = list_cron_jobs()
    if not jobs: return await interaction.followup.send("No jobs.")
    msg = "⏰ **Jobs**\n\n"
    for j in jobs: msg += f"• **{j.name}** ({j.id}) - {j.run_count} runs\n"
    notifications = _fire_discord_command_hook(interaction, "jobs")
    await interaction.followup.send(msg + notifications)

def run_discord():
    if not DISCORD_BOT_TOKEN:
        log.error("DISCORD_BOT_TOKEN is not set!")
        return
    
    global bot_instance
    retry_delay = 10
    
    while True:
        try:
            log.info("Starting OpenClawGotchi Discord Bot...")
            bot_instance.run(DISCORD_BOT_TOKEN)
            break # Exit loop if run() finishes normally
        except Exception as e:
            log.error(f"Discord Bot crashed/failed: {e}")
            
            # Recreate bot instance to fix "Session is closed" errors on retry
            log.info("Re-initializing bot instance for recovery...")
            old_tree = bot_instance.tree
            bot_instance = OpenClawDiscord()
            
            # Transfer registered slash commands to the new instance
            for cmd in old_tree.get_commands():
                try:
                    bot_instance.tree.add_command(cmd)
                except Exception as register_err:
                    log.warning(f"Failed to transfer command {cmd.name}: {register_err}")
            
            log.info(f"Retrying in {retry_delay}s...")
            import time
            time.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 300) # Max 5 mins
