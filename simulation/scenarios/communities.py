import math
import random

import pygame
import config as _cfg

from simulation.scenarios.base_scenario import BaseScenario
from simulation.utils import distance

_COMMUNITY_COLORS = [
    (80,  140, 220),
    (220, 130,  50),
    (80,  190, 100),
    (180,  80, 180),
    (220, 200,  50),
    ( 60, 190, 210),
    (230,  80, 120),
    (140, 200,  80),
]


def _community_centers_grid(n: int, width: int, height: int):
    """Arrange n communities in a grid matching the screen aspect ratio."""
    cols = math.ceil(math.sqrt(n * width / height))
    rows = math.ceil(n / cols)
    centers = []
    for i in range(n):
        col = i % cols
        row = i // cols
        cx = width  * (col + 1) / (cols + 1)
        cy = height * (row + 1) / (rows + 1)
        centers.append((cx, cy))
    return centers


class CommunitiesScenario(BaseScenario):
    name = "communities"

    def __init__(self):
        super().__init__()
        self.num_communities  = _cfg.NUM_COMMUNITIES
        self.square_half      = _cfg.COMMUNITY_SQUARE_HALF
        self.return_force     = _cfg.COMMUNITY_RETURN_FORCE
        self.damping          = _cfg.COMMUNITY_DAMPING
        self.within_radius    = _cfg.WITHIN_INFECTION_RADIUS
        self.between_radius   = _cfg.BETWEEN_INFECTION_RADIUS
        self.travel_prob      = _cfg.TRAVEL_PROBABILITY
        self.travel_stay_time = _cfg.TRAVEL_STAY_TIME
        self.max_speed        = _cfg.SPEED * 2.0
        self._centers = _community_centers_grid(
            self.num_communities, _cfg.WIDTH, _cfg.HEIGHT
        )

    def initialize(self, model):
        for i, person in enumerate(model.people):
            cid = i % self.num_communities
            cx, cy = self._centers[cid]
            spread = self.square_half * 0.8
            person.x = max(0, min(_cfg.WIDTH,  cx + random.uniform(-spread, spread)))
            person.y = max(0, min(_cfg.HEIGHT, cy + random.uniform(-spread, spread)))
            person.community_id      = cid
            person.community_cx      = cx
            person.community_cy      = cy
            person.home_community_id = cid
            person.home_cx           = cx
            person.home_cy           = cy
            person.travel_timer      = 0
            person.is_traveling      = False

    def before_update(self, model):
        for person in model.people:
            # Travel state machine
            if person.is_traveling:
                person.travel_timer -= 1
                if person.travel_timer <= 0:
                    person.is_traveling      = False
                    person.community_id      = person.home_community_id
                    person.community_cx      = person.home_cx
                    person.community_cy      = person.home_cy
            elif random.random() < self.travel_prob:
                other_ids = [k for k in range(self.num_communities)
                             if k != person.community_id]
                target_id = random.choice(other_ids)
                tcx, tcy = self._centers[target_id]
                person.is_traveling  = True
                person.community_id  = target_id
                person.community_cx  = tcx
                person.community_cy  = tcy
                person.travel_timer  = self.travel_stay_time

            # Spring + damping only when OUTSIDE the community zone.
            # Inside the square people wander freely — no interference.
            dx   = person.community_cx - person.x
            dy   = person.community_cy - person.y
            dist = distance(person.x, person.y, person.community_cx, person.community_cy)

            if dist > self.square_half:
                person.vx *= self.damping
                person.vy *= self.damping
                scale = min(dist / 30.0, 4.0)
                person.vx += self.return_force * dx / dist * scale
                person.vy += self.return_force * dy / dist * scale
                spd = (person.vx ** 2 + person.vy ** 2) ** 0.5
                if spd > self.max_speed:
                    factor = self.max_speed / spd
                    person.vx *= factor
                    person.vy *= factor

    def get_infection_radius(self, infected, susceptible) -> float:
        if infected.community_id == susceptible.community_id:
            return self.within_radius
        return self.between_radius

    def draw_environment(self, screen):
        hs = self.square_half
        for i, (cx, cy) in enumerate(self._centers):
            color = _COMMUNITY_COLORS[i % len(_COMMUNITY_COLORS)]
            rect = pygame.Rect(int(cx) - hs, int(cy) - hs, hs * 2, hs * 2)
            # Semi-transparent fill
            surf = pygame.Surface((hs * 2, hs * 2), pygame.SRCALPHA)
            surf.fill((*color, 35))
            screen.blit(surf, rect.topleft)
            # Solid border
            pygame.draw.rect(screen, color, rect, 2)
