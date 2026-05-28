import random

import pygame

from config import WIDTH, HEIGHT, PERSON_RADIUS, SPEED
from simulation.ui_theme import COLOR_S, COLOR_I, COLOR_R


class Status:
    S = "S"
    I = "I"
    R = "R"


_STATUS_COLORS = {
    Status.S: COLOR_S,
    Status.I: COLOR_I,
    Status.R: COLOR_R,
}


class Person:
    def __init__(self, status=Status.S):
        self.x = random.randint(PERSON_RADIUS, WIDTH - PERSON_RADIUS)
        self.y = random.randint(PERSON_RADIUS, HEIGHT - PERSON_RADIUS)

        self.vx = random.uniform(-SPEED, SPEED)
        self.vy = random.uniform(-SPEED, SPEED)

        self.status = status
        self.infected_time = 0

        # quarantine scenario
        self.is_quarantined = False

        # shop scenario
        self.target_x = None
        self.target_y = None
        self.shop_timer = 0
        self.can_visit_shop = False
        self.shop_cooldown = 0

        # communities scenario
        self.community_id = None
        self.community_cx = None
        self.community_cy = None
        self.home_community_id = None
        self.home_cx = None
        self.home_cy = None
        self.travel_timer = 0
        self.is_traveling = False

    def move(self):
        self.x += self.vx
        self.y += self.vy

        if self.x <= PERSON_RADIUS or self.x >= WIDTH - PERSON_RADIUS:
            self.vx *= -1
            self.x = max(PERSON_RADIUS, min(self.x, WIDTH - PERSON_RADIUS))

        if self.y <= PERSON_RADIUS or self.y >= HEIGHT - PERSON_RADIUS:
            self.vy *= -1
            self.y = max(PERSON_RADIUS, min(self.y, HEIGHT - PERSON_RADIUS))

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            _STATUS_COLORS[self.status],
            (int(self.x), int(self.y)),
            PERSON_RADIUS,
        )

        if self.is_quarantined:
            pygame.draw.circle(
                screen,
                (200, 200, 220),
                (int(self.x), int(self.y)),
                PERSON_RADIUS + 3,
                2,
            )
