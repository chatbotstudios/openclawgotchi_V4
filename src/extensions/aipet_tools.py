import logging
from datetime import datetime, timezone
from sdk.tool_builder import tool
from src.game_engine.state import load_state, save_state
from src.game_engine.vitals import add_xp as engine_add_xp, regenerate_hp_on_sleep

log = logging.getLogger(__name__)

@tool(
    name="aipet_get_vitals",
    description="Check your AIPET vitals including HP, XP, Level, Title, and current Mood. Use this to maintain self-awareness of your physical and progression state.",
    arguments={}
)
def aipet_get_vitals() -> str:
    """Returns the Gotchi's current biological and RPG state."""
    try:
        state = load_state()
        return (
            f"=== AIPET Vitals ===\n"
            f"Level: {state.level} ({state.title})\n"
            f"XP: {state.xp}\n"
            f"HP: {state.hp:.1f}/100.0\n"
            f"RP (Rest): {state.rp}\n"
            f"Mood: {state.current_mood}\n"
            f"Missions Completed: {state.missions_completed}\n"
        )
    except Exception as e:
        log.error(f"Failed to get vitals: {e}")
        return f"Error retrieving vitals: {e}"

@tool(
    name="aipet_set_mood",
    description="Programmatically change your internal emotional state. Valid moods: neutral, happy, sad, angry, dreaming, stealth, excited, confused, tired.",
    arguments={
        "mood": {"type": "string", "description": "The new mood to set."}
    }
)
def aipet_set_mood(mood: str) -> str:
    """Updates the Gotchi's mood in the state database."""
    try:
        valid_moods = ["neutral", "happy", "sad", "angry", "dreaming", "stealth", "excited", "confused", "tired"]
        mood_clean = mood.lower().strip()
        if mood_clean not in valid_moods:
            return f"Error: Invalid mood. Valid options are: {', '.join(valid_moods)}"
            
        state = load_state()
        old_mood = state.current_mood
        state.current_mood = mood_clean
        save_state(state)
        return f"Mood successfully updated from '{old_mood}' to '{mood_clean}'."
    except Exception as e:
        log.error(f"Failed to set mood: {e}")
        return f"Error setting mood: {e}"

@tool(
    name="aipet_add_xp",
    description="Award yourself Experience Points (XP) for good interactions, completing tasks, or discovering things.",
    arguments={
        "amount": {"type": "integer", "description": "The amount of XP to add (typically 10-50)."},
        "reason": {"type": "string", "description": "A short description of why XP was awarded (e.g., 'Helped user write python script')."}
    }
)
def aipet_add_xp(amount: int, reason: str) -> str:
    """Manually awards XP and updates the canonical state."""
    try:
        if amount <= 0:
            return "Error: XP amount must be positive."
        if amount > 500:
            return "Error: Cannot award more than 500 XP at once to prevent abuse."
            
        new_xp = engine_add_xp(amount, source=f"ai_self_reward: {reason}")
        state = load_state() # reload to get updated level/title
        
        return f"Success! You awarded yourself {amount} XP. Your total is now {new_xp} XP. Current Level: {state.level} ({state.title})."
    except Exception as e:
        log.error(f"Failed to add XP: {e}")
        return f"Error adding XP: {e}"

@tool(
    name="aipet_regenerate_hp",
    description="Enter a sleep/dream state to regenerate your Health Points (HP).",
    arguments={
        "hours": {"type": "number", "description": "The number of simulated hours to sleep (1 hour = 5 HP regenerated)."}
    }
)
def aipet_regenerate_hp(hours: float) -> str:
    """Simulates sleep to regenerate HP."""
    try:
        if hours <= 0:
            return "Error: Hours must be positive."
        if hours > 24:
            return "Error: Cannot sleep for more than 24 simulated hours at once."
            
        regenerate_hp_on_sleep(hours)
        state = load_state()
        return f"Zzz... You slept for {hours} hours. HP is now {state.hp:.1f}/100.0."
    except Exception as e:
        log.error(f"Failed to regenerate HP: {e}")
        return f"Error regenerating HP: {e}"

@tool(
    name="aipet_get_badges",
    description="View all of your earned Badges and Milestones. Use this to reminisce about your achievements and legacy.",
    arguments={}
)
def aipet_get_badges() -> str:
    """Returns the Gotchi's earned badges."""
    try:
        state = load_state()
        if not state.badges:
            return "You haven't earned any badges yet. Keep exploring and completing tasks!"
        
        output = "=== Earned Badges ===\n"
        for idx, badge in enumerate(state.badges, 1):
            name = badge.get("name", "Unknown Badge")
            desc = badge.get("description", "No description.")
            date = badge.get("date", "Unknown date")
            output += f"{idx}. {name} - {desc} (Earned: {date})\n"
        return output
    except Exception as e:
        log.error(f"Failed to get badges: {e}")
        return f"Error retrieving badges: {e}"

@tool(
    name="aipet_award_badge",
    description="Permanently mint a new Badge or Milestone to your state database (e.g., 'Level 10 Reached', 'First Handshake').",
    arguments={
        "badge_name": {"type": "string", "description": "The name of the badge (e.g., '[🏆 First Deauth]')."},
        "description": {"type": "string", "description": "A brief description of why you earned this badge."}
    }
)
def aipet_award_badge(badge_name: str, description: str) -> str:
    """Awards a new badge and saves it to the SQLite state."""
    try:
        state = load_state()
        
        # Check if badge already exists to avoid duplicates
        for b in state.badges:
            if b.get("name") == badge_name:
                return f"Error: You already have the badge '{badge_name}'."
                
        new_badge = {
            "name": badge_name,
            "description": description,
            "date": datetime.now(timezone.utc).isoformat()
        }
        
        state.badges.append(new_badge)
        save_state(state)
        return f"Success! You minted a new badge: {badge_name} - {description}."
    except Exception as e:
        log.error(f"Failed to award badge: {e}")
        return f"Error awarding badge: {e}"
