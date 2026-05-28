from pathlib import Path

import pygame
from PIL import Image

import config as _cfg


class GifRecorder:
    def __init__(self):
        self.frames = []
        self.step = 0
        self._frame_interval = _cfg.GIF_FRAME_INTERVAL
        self._frame_duration = _cfg.GIF_FRAME_DURATION

        Path(_cfg.RESULTS_DIR).mkdir(exist_ok=True)

    def capture(self, screen):
        self.step += 1

        if self.step % self._frame_interval != 0:
            return

        image_data = pygame.image.tostring(screen, "RGB")
        image = Image.frombytes("RGB", screen.get_size(), image_data)

        self.frames.append(image)

    def save(self):
        if not self.frames:
            return

        self.frames[0].save(
            _cfg.GIF_PATH,
            save_all=True,
            append_images=self.frames[1:],
            duration=self._frame_duration,
            loop=0,
        )
