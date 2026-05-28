import math
import random

import pygame
import config as _cfg

from simulation.scenarios.base_scenario import BaseScenario
from simulation.utils import distance


class ShopScenario(BaseScenario):
    name = "shop"

    def __init__(self):
        super().__init__()
        self.speed                   = _cfg.SPEED
        self.shop_x                  = _cfg.SHOP_X
        self.shop_y                  = _cfg.SHOP_Y
        self.shop_radius             = _cfg.SHOP_RADIUS
        self.visitor_share           = _cfg.SHOP_VISITOR_SHARE
        self.visit_prob              = _cfg.SHOP_VISIT_PROBABILITY
        self.stay_time               = _cfg.SHOP_STAY_TIME
        self.cooldown                = _cfg.SHOP_COOLDOWN
        self.capacity                = _cfg.SHOP_CAPACITY
        self.shop_infection_radius   = _cfg.SHOP_INFECTION_RADIUS
        self.shop_infection_probability = _cfg.SHOP_INFECTION_PROBABILITY

    def initialize(self, model):
        for person in model.people:
            person.can_visit_shop = random.random() < self.visitor_share
            person.shop_cooldown  = random.randint(0, self.cooldown)

    def before_update(self, model):
        # Count people currently inside the shop (timer active)
        active_shop_people = sum(1 for p in model.people if p.shop_timer > 0)

        for person in model.people:
            if not person.can_visit_shop:
                continue

            if person.shop_cooldown > 0:
                person.shop_cooldown -= 1

            # Inside shop: wander slowly, count down timer
            if person.shop_timer > 0:
                person.shop_timer -= 1
                person.vx = random.uniform(-0.4, 0.4)
                person.vy = random.uniform(-0.4, 0.4)

                if person.shop_timer == 0:
                    # Teleport back to saved pre-shop position
                    person.x = person.target_x
                    person.y = person.target_y
                    person.target_x = None
                    person.target_y = None
                    person.vx = random.uniform(-self.speed, self.speed)
                    person.vy = random.uniform(-self.speed, self.speed)
                    person.shop_cooldown = self.cooldown
                continue

            # Decide to visit shop
            if (
                person.shop_cooldown == 0
                and active_shop_people < self.capacity
                and random.random() < self.visit_prob
            ):
                # Save current position for return teleport
                person.target_x = person.x
                person.target_y = person.y
                # Teleport to random spot inside shop
                angle = random.uniform(0, 2 * math.pi)
                r = random.uniform(0, self.shop_radius * 0.85)
                person.x = self.shop_x + r * math.cos(angle)
                person.y = self.shop_y + r * math.sin(angle)
                person.shop_timer = self.stay_time
                person.vx = random.uniform(-0.4, 0.4)
                person.vy = random.uniform(-0.4, 0.4)
                active_shop_people += 1

    def _is_in_shop(self, person) -> bool:
        return distance(person.x, person.y, self.shop_x, self.shop_y) <= self.shop_radius

    def get_infection_radius(self, infected, susceptible) -> float:
        if self._is_in_shop(infected) and self._is_in_shop(susceptible):
            return self.shop_infection_radius
        return self.infection_radius

    def get_infection_probability(self, infected, susceptible) -> float:
        if self._is_in_shop(infected) and self._is_in_shop(susceptible):
            return self.shop_infection_probability
        return self.infection_probability

    def draw_environment(self, screen):
        pygame.draw.circle(screen, (210, 195, 130), (self.shop_x, self.shop_y), self.shop_radius)
        pygame.draw.circle(screen, (180, 155,  60), (self.shop_x, self.shop_y), self.shop_radius, 3)
