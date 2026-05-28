import pygame
import config as _cfg

from simulation.person import Status
from simulation.scenarios.base_scenario import BaseScenario
from simulation.utils import distance


class SocialDistancingScenario(BaseScenario):
    name = "social_distancing"

    def __init__(self):
        super().__init__()
        self.distancing_after  = _cfg.DISTANCING_AFTER
        self.distancing_radius = _cfg.DISTANCING_RADIUS
        self.distancing_force  = _cfg.DISTANCING_FORCE
        self.max_speed         = _cfg.SPEED * 2.5
        self.width             = _cfg.WIDTH
        self.height            = _cfg.HEIGHT

        self.distancing_active   = False
        self.frames_since_first  = 0  # frames since first infected detected

    def before_update(self, model):
        # Activate distancing DISTANCING_AFTER frames after first infection appears
        if not self.distancing_active:
            if model.count_status(Status.I) >= 1:
                self.frames_since_first += 1
                if self.frames_since_first >= self.distancing_after:
                    self.distancing_active = True

        if not self.distancing_active:
            return

        people = model.people
        n = len(people)

        # Pairwise repulsion
        for i in range(n):
            for j in range(i + 1, n):
                p = people[i]
                q = people[j]
                dist = distance(p.x, p.y, q.x, q.y)
                if 0 < dist < self.distancing_radius:
                    force = self.distancing_force * (1.0 - dist / self.distancing_radius)
                    dx = (p.x - q.x) / dist
                    dy = (p.y - q.y) / dist
                    p.vx += force * dx
                    p.vy += force * dy
                    q.vx -= force * dx
                    q.vy -= force * dy

        # Cap speed so repulsion doesn't launch people across the screen
        for person in people:
            spd = (person.vx ** 2 + person.vy ** 2) ** 0.5
            if spd > self.max_speed:
                factor = self.max_speed / spd
                person.vx *= factor
                person.vy *= factor

    def draw_environment(self, screen):
        if self.distancing_active:
            pygame.draw.rect(screen, (60, 90, 200), (0, 0, self.width, self.height), 4)
            font = pygame.font.SysFont(None, 22)
            label = font.render("SOCIAL DISTANCING AKTYWNE", True, (100, 140, 240))
            screen.blit(label, (self.width // 2 - label.get_width() // 2, self.height - 28))
        elif self.frames_since_first > 0:
            remaining = self.distancing_after - self.frames_since_first
            font = pygame.font.SysFont(None, 20)
            label = font.render(
                f"Social distancing za: {remaining} kl.", True, (100, 110, 160)
            )
            screen.blit(label, (self.width // 2 - label.get_width() // 2, self.height - 24))
