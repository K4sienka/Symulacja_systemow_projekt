import random

import config as _cfg

from simulation.person import Person, Status
from simulation.utils import distance


class SimulationModel:
    def __init__(self, scenario):
        self.scenario = scenario
        self.people = []

        population_size = _cfg.POPULATION_SIZE
        initial_infected = _cfg.INITIAL_INFECTED
        self._recovery_time = _cfg.RECOVERY_TIME

        for i in range(population_size):
            if i < initial_infected:
                self.people.append(Person(status=Status.I))
            else:
                self.people.append(Person(status=Status.S))

        self.history = {"S": [], "I": [], "R": []}

        scenario.initialize(self)

    def update(self):
        self.scenario.before_update(self)

        for person in self.people:
            if self.scenario.can_move(person):
                person.move()

        self.spread_infection()
        self.recover_people()
        self.save_history()

    def spread_infection(self):
        infected_people = [p for p in self.people if p.status == Status.I]
        susceptible_people = [p for p in self.people if p.status == Status.S]

        for infected in infected_people:
            if not self.scenario.can_infect(infected):
                continue

            for susceptible in susceptible_people:
                dist = distance(infected.x, infected.y, susceptible.x, susceptible.y)

                infection_radius = self.scenario.get_infection_radius(infected, susceptible)
                infection_probability = self.scenario.get_infection_probability(infected, susceptible)

                if dist <= infection_radius:
                    if random.random() < infection_probability:
                        susceptible.status = Status.I
                        susceptible.infected_time = 0

    def recover_people(self):
        for person in self.people:
            if person.status == Status.I:
                person.infected_time += 1

                if person.infected_time >= self._recovery_time:
                    person.status = Status.R
                    person.is_quarantined = False

    def save_history(self):
        self.history["S"].append(self.count_status(Status.S))
        self.history["I"].append(self.count_status(Status.I))
        self.history["R"].append(self.count_status(Status.R))

    def count_status(self, status):
        return sum(1 for person in self.people if person.status == status)
