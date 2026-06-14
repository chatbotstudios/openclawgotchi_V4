import logging
from typing import Callable, Dict, List, Any

log = logging.getLogger(__name__)

class EventDispatcher:
    """
    Central Event Bus for the Game Engine.
    Allows Decoupling of Hardware, UI, and Mechanics.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventDispatcher, cls).__new__(cls)
            cls._instance._listeners: Dict[str, List[Callable[[Any], None]]] = {}
        return cls._instance

    def subscribe(self, event_type: str, callback: Callable[[Any], None]):
        """Subscribe to a specific event type."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        if callback not in self._listeners[event_type]:
            self._listeners[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable[[Any], None]):
        """Unsubscribe from a specific event type."""
        if event_type in self._listeners and callback in self._listeners[event_type]:
            self._listeners[event_type].remove(callback)

    def emit(self, event_type: str, data: Any = None):
        """Emit an event to all subscribers synchronously."""
        log.debug(f"EventBus Emitted: {event_type}")
        if event_type in self._listeners:
            for callback in self._listeners[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    log.error(f"Error in EventBus listener for {event_type}: {e}")

# Global singleton instance for easy import
events = EventDispatcher()
