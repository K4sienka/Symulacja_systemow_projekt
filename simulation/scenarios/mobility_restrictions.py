import random

import pygame
import config as _cfg

from simulation.person import Status
from simulation.scenarios.base_scenario import BaseScenario


class MobilityRestrictionsScenario(BaseScenario):
    name = "mobility_restrictions"

    def __init__(self):
        super().__init__()
        self.restriction_threshold = _cfg.RESTRICTION_THRESHOLD
        self.release_threshold = _cfg.RESTRICTION_RELEASE_THRESHOLD
        self.restricted_speed = _cfg.RESTRICTED_SPEED
        self.population_size = _cfg.POPULATION_SIZE
        self.speed = _cfg.SPEED
        self.width = _cfg.WIDTH
        self.height = _cfg.HEIGHT
        self.restrictions_active = False

    def before_update(self, model):
        infected_fraction = model.count_status(Status.I) / self.population_size

        if not self.restrictions_active and infected_fraction >= self.restriction_threshold:
            self.restrictions_active = True
            self._clamp_speeds(model)

        elif self.restrictions_active and infected_fraction <= self.release_threshold:
            self.restrictions_active = False
            self._restore_speeds(model)

    def _clamp_speeds(self, model):
        for person in model.people:
            current = (person.vx ** 2 + person.vy ** 2) ** 0.5
            if current > self.restricted_speed and current > 0:
                factor = self.restricted_speed / current
                person.vx *= factor
                person.vy *= factor

    def _restore_speeds(self, model):
        for person in model.people:
            person.vx = random.uniform(-self.speed, self.speed)
            person.vy = random.uniform(-self.speed, self.speed)

    def draw_environment(self, screen):
        if not self.restrictions_active:
            return
        border = 6
        pygame.draw.rect(screen, (200, 60, 60), (0, 0, self.width, self.height), border)
        font = pygame.font.SysFont(None, 22)
        label = font.render("OGRANICZENIA MOBILNOSCI AKTYWNE", True, (220, 80, 80))
        screen.blit(label, (self.width // 2 - label.get_width() // 2, self.height - 28))
