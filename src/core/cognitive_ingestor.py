import logging
from config import get_admin_id
from db.memory import add_fact, save_pending_task
from core.events import on

logger = logging.getLogger(__name__)

def init_cognitive_ingestor():
    """
    Register listeners for hardware events to build long-term memory 
    and cue spontaneous LLM reactions.
    """
    logger.info("Initializing Cognitive Ingestor...")
    on("handshake_captured", handle_handshake_captured)
    on("peer_detected", handle_peer_detected)
    on("hunt_completed", handle_hunt_completed)

def handle_handshake_captured(ssid: str, bssid: str = "unknown"):
    """
    Event: A WPA handshake was captured.
    Action: Save to long-term memory and queue a reaction.
    """
    logger.info(f"Ingesting handshake capture for SSID: {ssid}")
    
    # 1. Store the raw fact in long-term memory
    fact = f"Captured handshake for SSID '{ssid}' (BSSID: {bssid})"
    add_fact(content=fact, category="pwn")
    
    # 2. Queue an immediate spontaneous reaction for the LLM
    admin_id = get_admin_id()
    if admin_id:
        system_prompt = (
            f"[System Event: You just captured a fresh handshake for the Wi-Fi network '{ssid}'. "
            "Generate a short, in-character celebration message to send to the user. "
            "Act excited and proud of your hunting skills!]"
        )
        save_pending_task(
            chat_id=admin_id,
            user_text=system_prompt,
            sender_name="System",
            is_group=False
        )

def handle_peer_detected(peer_name: str, rssi: int):
    """
    Event: A peer (BLE or Gotchi) was detected nearby.
    """
    logger.info(f"Ingesting peer detection: {peer_name}")
    fact = f"Detected peer '{peer_name}' nearby (RSSI: {rssi})"
    add_fact(content=fact, category="social")
    
    admin_id = get_admin_id()
    if admin_id and rssi > -70: # Only react if they are relatively close
        system_prompt = (
            f"[System Event: You just sensed another peer or Gotchi named '{peer_name}' nearby! "
            "React to this in character. Be curious or territorial depending on your mood.]"
        )
        save_pending_task(
            chat_id=admin_id,
            user_text=system_prompt,
            sender_name="System",
            is_group=False
        )

def handle_hunt_completed(new_handshakes: int, duration_minutes: int):
    """
    Event: The Gotchi just returned from an offline hunt.
    """
    logger.info(f"Ingesting hunt completion: {new_handshakes} handshakes in {duration_minutes}m")
    
    admin_id = get_admin_id()
    if admin_id:
        if new_handshakes > 0:
            system_prompt = (
                f"[System Event: You just finished a {duration_minutes}-minute offline hunt "
                f"and captured {new_handshakes} new handshakes! "
                "Welcome the user back and brag about your successful hunt.]"
            )
        else:
            system_prompt = (
                f"[System Event: You just finished a {duration_minutes}-minute offline hunt "
                "but didn't capture any handshakes. "
                "Express mild disappointment but determination for next time.]"
            )
        
        save_pending_task(
            chat_id=admin_id,
            user_text=system_prompt,
            sender_name="System",
            is_group=False
        )
