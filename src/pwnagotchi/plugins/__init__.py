import logging
from hooks.runner import register_hook, HookEvent

log = logging.getLogger("Pwnagotchi.Plugins")

class PluginLogAdapter:
    """Mock logger that matches Pwnagotchi's self.log format."""
    def __init__(self, name):
        self.logger = logging.getLogger(f"Plugins.{name}")

    def info(self, msg, *args):
        self.logger.info(msg, *args)

    def warning(self, msg, *args):
        self.logger.warning(msg, *args)

    def error(self, msg, *args):
        self.logger.error(msg, *args)

    def debug(self, msg, *args):
        self.logger.debug(msg, *args)


class BasePlugin:
    """
    Thin backward-compatible BasePlugin layer.
    Automatically scans legacy lifecycle methods and registers them as V4 Hooks.
    """
    def __init__(self):
        self.log = PluginLogAdapter(self.__class__.__name__)
        self._register_callbacks()

    def _register_callbacks(self):
        # Maps legacy callback names to OpenClawGotchi V4 Hook types
        mapping = {
            "on_loaded": "startup",
            "on_ready": "pwn.ready",
            "on_wifi_update": "pwn.wifi_update",
            "on_handshake": "pwn.handshake",
            "on_peer_detected": "pwn.peer_detected",
            "on_periodic": "heartbeat",
            "on_unload": "shutdown",
        }
        for method_name, event_type in mapping.items():
            method = getattr(self, method_name, None)
            if method and callable(method):
                self._bind_hook(event_type, method, method_name)

    def _bind_hook(self, event_type, method, method_name):
        def hook_wrapper(event: HookEvent):
            try:
                # Map standard event arguments to expected legacy signatures
                if method_name in ("on_loaded", "on_unload"):
                    method()
                elif method_name == "on_ready":
                    # Pwnagotchi expects: on_ready(self, agent)
                    method(event.data.get("agent"))
                elif method_name == "on_wifi_update":
                    # Pwnagotchi expects: on_wifi_update(self, agent, access_points)
                    method(event.data.get("agent"), event.data.get("aps", []))
                elif method_name == "on_handshake":
                    # Pwnagotchi expects: on_handshake(self, agent, filename, access_point)
                    method(
                        event.data.get("agent"), 
                        event.data.get("filename"), 
                        event.data.get("ap")
                    )
                elif method_name == "on_peer_detected":
                    # Pwnagotchi expects: on_peer_detected(self, agent, peer)
                    method(event.data.get("agent"), event.data.get("peer"))
                elif method_name == "on_periodic":
                    # Pwnagotchi expects: on_periodic(self, agent)
                    method(event.data.get("agent"))
                else:
                    method(event)
            except Exception as e:
                self.log.error(f"Error in legacy callback {method_name}: {e}")

        register_hook(event_type, hook_wrapper)
