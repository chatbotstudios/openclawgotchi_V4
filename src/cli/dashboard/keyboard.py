import threading
import sys
import tty
import termios
import logging
from queue import Queue

log = logging.getLogger(__name__)

class KeyboardListener:
    """Non-blocking keyboard listener for raw SSH input."""
    
    def __init__(self):
        self.queue = Queue()
        self.running = False
        self.thread = None
        
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._listen, daemon=True)
        self.thread.start()
        
    def stop(self):
        self.running = False
        
    def _listen(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(sys.stdin.fileno())
            while self.running:
                # Read a single character
                # Note: this will block until a key is pressed.
                # To prevent blocking forever on exit, we rely on daemon=True.
                import select
                if select.select([sys.stdin], [], [], 0.5)[0]:
                    ch = sys.stdin.read(1)
                    if ch:
                        self.queue.put(ch.lower())
        except Exception as e:
            log.error(f"Keyboard listener error: {e}")
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            
    def get_key(self):
        """Returns the pressed key or None if empty."""
        if not self.queue.empty():
            return self.queue.get()
        return None
