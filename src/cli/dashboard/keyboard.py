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
                import select
                if select.select([sys.stdin], [], [], 0.5)[0]:
                    ch = sys.stdin.read(1)
                    if ch:
                        if ch == '\x1b':
                            self.queue.put("key:escape")
                        elif ch in ('\n', '\r'):
                            self.queue.put("key:enter")
                        elif ch in ('\x7f', '\x08'):
                            self.queue.put("key:backspace")
                        else:
                            # Preserve case for typing, put in format char:<ch>
                            self.queue.put(f"char:{ch}")
        except Exception as e:
            log.error(f"Keyboard listener error: {e}")
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            
    def get_key(self):
        """Returns the pressed key or None if empty."""
        if not self.queue.empty():
            return self.queue.get()
        return None
