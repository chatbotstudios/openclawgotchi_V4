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

    Legacy callback → V4 event type mapping (Phase 1 + Phase 2):
    ─────────────────────────────────────────────────────────────
    on_loaded             → startup
    on_ready              → pwn.ready
    on_wifi_update        → pwn.wifi_update
    on_handshake          → pwn.handshake
    on_deauthentication   → pwn.deauth
    on_association        → pwn.association
    on_epoch              → pwn.epoch
    on_channel_hop        → pwn.channel_hop
    on_internet_available → pwn.internet
    on_rebooting          → pwn.rebooting
    on_peer_detected      → pwn.peer_detected
    on_periodic           → heartbeat
    on_unload             → shutdown
    on_bcap_*             → pwn.bcap.<suffix>  (dynamic)
    """

    # Phase 1 static mapping
    _STATIC_MAPPING = {
        "on_loaded":             "startup",
        "on_ready":              "pwn.ready",
        "on_wifi_update":        "pwn.wifi_update",
        "on_handshake":          "pwn.handshake",
        "on_deauthentication":   "pwn.deauth",
        "on_association":        "pwn.association",
        "on_epoch":              "pwn.epoch",
        "on_channel_hop":        "pwn.channel_hop",
        "on_internet_available": "pwn.internet",
        "on_rebooting":          "pwn.rebooting",
        "on_peer_detected":      "pwn.peer_detected",
        "on_periodic":           "heartbeat",
        "on_unload":             "shutdown",
    }

    def __init__(self):
        self.log = PluginLogAdapter(self.__class__.__name__)
        self._register_callbacks()

    def _register_callbacks(self):
        """Scan instance methods and wire legacy callbacks to V4 hook events."""
        # --- Static / named mappings ---
        for method_name, event_type in self._STATIC_MAPPING.items():
            method = getattr(self, method_name, None)
            if method and callable(method):
                self._bind_hook(event_type, method, method_name)

        # --- Dynamic on_bcap_* → pwn.bcap.<suffix> ---
        # e.g. on_bcap_wifi_ap_new → pwn.bcap.wifi_ap_new
        for attr in dir(self):
            if attr.startswith("on_bcap_") and callable(getattr(self, attr)):
                suffix = attr[len("on_bcap_"):]
                event_type = f"pwn.bcap.{suffix}"
                self._bind_hook(event_type, getattr(self, attr), attr)

    def _build_legacy_args(self, method_name: str, event: HookEvent):
        """Extract arguments from the V4 HookEvent into the legacy positional signature."""
        d = event.data
        agent = d.get("agent")

        if method_name in ("on_loaded", "on_unload", "on_rebooting"):
            return ()
        elif method_name in ("on_ready", "on_internet_available", "on_periodic"):
            return (agent,)
        elif method_name == "on_wifi_update":
            # on_wifi_update(self, agent, access_points)
            return (agent, d.get("aps", []))
        elif method_name == "on_handshake":
            # on_handshake(self, agent, filename, access_point, client_station=None)
            return (agent, d.get("filename"), d.get("ap"), d.get("client"))
        elif method_name == "on_deauthentication":
            # on_deauthentication(self, agent, access_point, client_station)
            return (agent, d.get("ap"), d.get("client"))
        elif method_name == "on_association":
            # on_association(self, agent, access_point)
            return (agent, d.get("ap"))
        elif method_name == "on_epoch":
            # on_epoch(self, agent, epoch, epoch_data)
            return (agent, d.get("epoch", 0), d.get("epoch_data", {}))
        elif method_name == "on_channel_hop":
            # on_channel_hop(self, agent, channel)
            return (agent, d.get("channel", 0))
        elif method_name == "on_peer_detected":
            return (agent, d.get("peer"))
        elif method_name.startswith("on_bcap_"):
            # on_bcap_*(self, agent, event_dict)
            return (agent, d.get("bcap_event", {}))
        else:
            return (event,)

    def _bind_hook(self, event_type: str, method, method_name: str):
        """Register a closure that adapts a V4 HookEvent to the legacy positional signature."""
        def hook_wrapper(event: HookEvent):
            try:
                args = self._build_legacy_args(method_name, event)
                method(*args)
            except TypeError as e:
                # Fallback: call with raw event so plugins that have custom sigs still fire
                try:
                    method(event)
                except Exception as inner:
                    self.log.error(f"Error in legacy callback {method_name} (fallback): {inner}")
            except Exception as e:
                self.log.error(f"Error in legacy callback {method_name}: {e}")

        register_hook(event_type, hook_wrapper)
