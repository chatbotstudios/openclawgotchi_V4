import logging

logger = logging.getLogger(__name__)

# Global registry of event listeners
_listeners = {}

def on(event_name: str, callback):
    """Register a callback function for a specific event."""
    if event_name not in _listeners:
        _listeners[event_name] = []
    _listeners[event_name].append(callback)
    logger.debug(f"Registered listener for event: {event_name}")

def emit(event_name: str, **kwargs):
    """Emit an event, calling all registered listeners with the provided kwargs."""
    if event_name in _listeners:
        logger.info(f"Emitting event: {event_name}")
        for callback in _listeners[event_name]:
            try:
                callback(**kwargs)
            except Exception as e:
                logger.error(f"Error in event listener for {event_name}: {e}")
    else:
        logger.debug(f"Event emitted but no listeners registered: {event_name}")
