"""
Mock EPD driver — enables running without physical E-Ink hardware.
Replaces epd2in13_V4 when MOCK_HARDWARE=1.
"""
import logging

log = logging.getLogger(__name__)


class EPD:
    WIDTH = 122
    HEIGHT = 250

    def __init__(self):
        self.width = self.WIDTH
        self.height = self.HEIGHT

    def init(self):
        log.debug("Mock EPD: init() — no-op")
        return 0

    def Clear(self, color=0xFF):
        log.debug(f"Mock EPD: Clear(0x{color:02X}) — no-op")

    def getbuffer(self, image):
        """Return a bytearray matching the expected buffer size."""
        buf_size = int(self.width / 8) * self.height
        log.debug(f"Mock EPD: getbuffer() — returning {buf_size}-byte blank buffer")
        return bytearray([0x00] * buf_size)

    def display(self, image):
        log.debug("Mock EPD: display() — no-op")

    def display_fast(self, image):
        log.debug("Mock EPD: display_fast() — no-op")

    def displayPartial(self, image):
        log.debug("Mock EPD: displayPartial() — no-op")

    def displayPartBaseImage(self, image):
        log.debug("Mock EPD: displayPartBaseImage() — no-op")

    def sleep(self):
        log.debug("Mock EPD: sleep() — no-op")

    def reset(self):
        log.debug("Mock EPD: reset() — no-op")
