from pathlib import Path

import pygame
from PIL import Image

from config import RESULTS_DIR, GIF_PATH, GIF_FRAME_INTERVAL, GIF_FRAME_DURATION


class GifRecorder:
    def __init__(self):
        self.frames = []
        self.step = 0

        Path(RESULTS_DIR).mkdir(exist_ok=True)

    def capture(self, screen):
        self.step += 1

        if self.step % GIF_FRAME_INTERVAL != 0:
            return

        image_data = pygame.image.tostring(screen, "RGB")
        image = Image.frombytes("RGB", screen.get_size(), image_data)

        self.frames.append(image)

    def save(self):
        if not self.frames:
            return

        self.frames[0].save(
            GIF_PATH,
            save_all=True,
            append_images=self.frames[1:],
            duration=GIF_FRAME_DURATION,
            loop=0,
        )