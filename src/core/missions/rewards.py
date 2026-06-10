import logging
from core.missions.models import Mission
from src.game_engine.vitals import add_xp
from utils.buddy_pulse import pulse_buddy

log = logging.getLogger(__name__)

def dispense_mission_reward(mission: Mission):
    """Dispense rewards when a mission is completed."""
    log.info(f"🏆 Mission Completed: {mission.title}")
    
    # 1. Add XP
    add_xp(mission.reward_xp, f"Mission: {mission.title}")
    
    # 2. Mood Boost / UI Notification
    try:
        from db.stats import get_stats_summary
        stats = get_stats_summary()
        pulse_buddy(
            action="celebrate",
            app="MISSIONS",
            text=f"Mission Complete: {mission.title} (+{mission.reward_xp} XP)",
            tokens=stats.get("xp", 0),
            level=stats.get("level", 0),
            approvals=stats.get("messages", 0)
        )
    except Exception as e:
        log.warning(f"Failed to pulse buddy for mission reward: {e}")
