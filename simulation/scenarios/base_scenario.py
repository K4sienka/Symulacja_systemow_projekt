import config as _cfg


class BaseScenario:
    def __init__(self):
        self.infection_radius = _cfg.INFECTION_RADIUS
        self.infection_probability = _cfg.INFECTION_PROBABILITY

    def initialize(self, model):
        pass

    def before_update(self, model):
        pass

    def can_move(self, person) -> bool:
        return True

    def can_infect(self, person) -> bool:
        return True

    def get_infection_radius(self, infected, susceptible) -> float:
        return self.infection_radius

    def get_infection_probability(self, infected, susceptible) -> float:
        return self.infection_probability

    def draw_environment(self, screen):
        pass
