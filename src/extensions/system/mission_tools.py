from sdk.tool_builder import register_tool
from core.missions.manager import get_missions, get_mission, update_mission_status

@register_tool
def list_available_missions() -> str:
    """Lists all available missions that can be accepted. Shows the mission ID, title, XP reward, and who can accept it (actor: human, gotchi, or any)."""
    missions = get_missions("available")
    if not missions:
        return "No missions are currently available."
        
    result = []
    for m in missions:
        result.append(f"- ID: {m.id} | Actor: {m.actor} | Title: {m.title} | Reward: +{m.reward_xp} XP\n  Desc: {m.description}")
        
    return "Available Missions:\n" + "\n".join(result)

@register_tool
def accept_mission(mission_id: str) -> str:
    """Accepts a mission by ID. You (Gotchi) can only accept missions where actor is 'gotchi' or 'any'. You cannot accept 'human' only missions yourself."""
    m = get_mission(mission_id)
    if not m:
        return f"Error: Mission '{mission_id}' not found."
    if m.status != 'available':
        return f"Error: Mission '{mission_id}' is already {m.status}."
    
    if m.actor == "human":
        return "Error: You cannot accept this mission autonomously. Only the human can accept and execute this."
        
    update_mission_status(mission_id, "active")
    return f"Success! You have accepted mission: {m.title}. Objective: {m.description}"

@register_tool
def get_mission_status(status: str = "active") -> str:
    """Lists missions filtered by status (e.g., 'active', 'completed', 'available'). Use this to check what missions you are currently tracking."""
    missions = get_missions(status)
    if not missions:
        return f"No missions found with status '{status}'."
        
    result = []
    for m in missions:
        result.append(f"- ID: {m.id} | Actor: {m.actor} | Title: {m.title} | Progress: {m.progress}/{m.target}\n  Desc: {m.description}")
        
    return f"Missions ({status}):\n" + "\n".join(result)

