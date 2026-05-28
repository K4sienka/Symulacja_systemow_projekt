import config as _cfg

from simulation.person import Status
from simulation.scenarios.base_scenario import BaseScenario


class QuarantineScenario(BaseScenario):
    name = "quarantine"

    def __init__(self):
        super().__init__()
        self.quarantine_after = _cfg.QUARANTINE_AFTER

    def before_update(self, model):
        for person in model.people:
            if person.status == Status.I and person.infected_time >= self.quarantine_after:
                person.is_quarantined = True

    def can_move(self, person) -> bool:
        return not person.is_quarantined

    def can_infect(self, person) -> bool:
        return not person.is_quarantined
