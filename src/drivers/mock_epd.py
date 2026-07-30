"""
Mock EPD driver — enables running without physical E-Ink hardware.
Replaces epd2in13_V4 when MOCK_HARDWARE=1.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


class EPD:
    WIDTH = 250
    HEIGHT = 122

    def __init__(self):
        self.width = self.WIDTH
        self.height = self.HEIGHT

    def init(self):
        pass  # No real hardware

    def Clear(self, color=0xFF):
        pass

    def display(self, image):
        # Save the image for the web dashboard to serve
        sim_path = Path.cwd() / "simulator.png"
        try:
            image.save(sim_path)
        except Exception:
            pass

    def sleep(self):
        pass

    def reset(self):
        pass
