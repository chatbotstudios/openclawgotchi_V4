import requests
import sys

# Update this to match your Buddy's IP on your network
BUDDY_IP = "192.168.1.13"
BUDDY_URL = f"http://{BUDDY_IP}:81/pulse"

def pulse_buddy(status, model_name="GOTCHI", text="", tokens=None, level=None, approvals=None, denials=None, tools=None):
    """
    Sends a pulse to the Gemini Buddy.
    :param status: 'idle', 'busy', 'attention', 'celebrate'
    :param model_name: Name of the model (e.g. 'GOTCHI')
    :param text: Status text to show on screen
    :param tools: List of tools being used
    """
    try:
        payload = {
            "status": status,
            "model": model_name,
            "text": text
        }
        if tokens is not None: payload["tokens"] = tokens
        if level is not None: payload["level"] = level
        if approvals is not None: payload["approvals"] = approvals
        if denials is not None: payload["denials"] = denials
        if tools is not None: payload["tools"] = tools
        
        # Using a short timeout so we don't block the main app
        response = requests.post(BUDDY_URL, json=payload, timeout=2)
        return response.status_code == 200
    except Exception:
        # Silently fail to avoid crashing the main app if Buddy is offline
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 buddy_pulse.py <status> [text] [tools] [tokens]")
        sys.exit(1)
        
    status = sys.argv[1]
    text = sys.argv[2] if len(sys.argv) > 2 else ""
    tools = sys.argv[3] if len(sys.argv) > 3 else None
    tokens = int(sys.argv[4]) if len(sys.argv) > 4 else None
    
    success = pulse_buddy(status, text=text, tools=tools, tokens=tokens)
    print(f"Pulse sent: {'Success' if success else 'Failed'}")
