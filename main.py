import random
import sys

MIN_FLOAT = sys.float_info.min

# CONSTANTS
GRID_WIDTH = 100
GRID_HEIGHT = 100

NUM_INDIVIDUALS = 100
MAX_AGE = 100
SPEED_VALUES = (1, 2, 3)
# C - ill, Z - infected, ZD - convalescing, ZZ - healthy
STATE_COLORS = {"C": "red", "Z": "yellow", "ZD": "orange", "ZZ": "green"}
STATE_VALUES = tuple(STATE_COLORS.keys())
# In days
STATE_DURATIONS = {"Z": 2, "C": 7, "ZD": 5}
# radius in which the infection can spread
INFECTION_RADIUS = 2
BIRTH_RATE = 0.1

print(STATE_VALUES[-1])


# FUNCTIONS
def get_random_direction(current_direction=None):
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]
    if current_direction is not None:
        directions.remove(current_direction)

    return random.choice(directions)


def calculate_distance(x1, y1, x2, y2):
    return max(x1 - x2, y1 - y2)


# CLASSES
class Individual:
    def __init__(self, birth=False, individual_max_age=MAX_AGE):
        self.x_pos = random.randint(0, GRID_WIDTH)
        self.y_pos = random.randint(0, GRID_HEIGHT)
        self.speed = random.choice(SPEED_VALUES)
        self.x_direction, self.y_direction = get_random_direction()

        if not birth:
            self.age = random.randint(0, individual_max_age)
            self.immunity = self.get_initial_immunity()
            self.state = random.choice(STATE_VALUES)
            self.isAlive = True
        else:
            # TODO: position of the newborn should be the same one of the parent
            self.age = 0
            self.immunity = 10
            self.state = "ZZ"
            self.isAlive = True

        self.state_duration = STATE_DURATIONS[self.state]

    def get_initial_immunity(self):
        """Return the initial immunity of the individual based on their age."""

        if self.age < 15 or self.age > 70:
            return random.uniform(0, 3) + MIN_FLOAT
        elif 40 <= self.age < 70:
            return random.uniform(3, 6) + MIN_FLOAT
        elif 15 <= self.age < 40:
            return random.uniform(6, 10) + MIN_FLOAT

    def update_age(self):
        self.age += 1

        # Check if the individual is dead
        if self.age >= MAX_AGE:
            self.isAlive = False

    def update_position(self):
        """Update the position of the individual."""

        # Check if the individual is dead
        if not self.is_alive():
            return

        # Update the position of the individual
        self.x_pos += self.speed * self.x_direction
        self.y_pos += self.speed * self.y_direction

        # Check if the individual is out of bounds
        if self.x_pos < 0:
            self.x_pos = 0
            self.x_direction = 1
        elif self.x_pos > GRID_WIDTH:
            self.x_pos = GRID_WIDTH
            self.x_direction = -1

        if self.y_pos < 0:
            self.y_pos = 0
            self.y_direction = 1
        elif self.y_pos > GRID_HEIGHT:
            self.y_pos = GRID_HEIGHT
            self.y_direction = -1

    def update_state(self):
        """Update the state of the individual."""

        # Check if the individual is dead
        if not self.is_alive():
            return

        self.state_duration -= 1

        if self.state_duration == 0:
            if self.state == "Z":
                self.state = "C"
            elif self.state == "C":
                self.state = "ZD"
            elif self.state == "ZD":
                self.state = "ZZ"

            self.state_duration = STATE_DURATIONS[self.state]

    def update_immunity(self, val=None):
        """Update the immunity of the individual."""

        # Check if the individual is dead
        if not self.is_alive():
            return

        # Update the immunity of the individual
        if val is None:
            if self.state == "Z":
                immunity_diff = -0.1
            elif self.state == "C":
                immunity_diff = -0.5
            elif self.state == "ZD":
                immunity_diff = 0.1
            elif self.state == "ZZ":
                immunity_diff = 0.05
        else:
            # if the value is provided from the outside (Simulation)
            immunity_diff = val

        if immunity_diff < 0:
            self.immunity += immunity_diff
        else:
            # limit the immunity to the maximum immunity
            max_immunity = self.get_max_immunity()
            self.immunity = min(self.immunity + immunity_diff, max_immunity)

        # Check if the individual is dead
        if self.immunity <= 0:
            self.isAlive = False

    def update(self):
        """Update the individual."""
        self.update_age()
        self.update_position()
        self.update_immunity()
        self.update_state()

    def get_max_immunity(self):
        if self.age < 15 or self.age > 70:
            return 3
        elif 40 <= self.age < 70:
            return 6
        elif 15 <= self.age < 40:
            return 10

    def get_immunity_category(self):
        if self.immunity <= 3:
            return "low"
        elif 3 < self.immunity <= 6:
            return "medium"
        elif self.immunity > 6:
            return "high"

    def reset_state_duration(self):
        self.state_duration = STATE_DURATIONS[self.state]

    def is_alive(self):
        return self.isAlive


class Simulation:
    def __init__(self):
        # 1 tick = 1 day
        self.ticks = 0
        self.individuals = [Individual() for _ in range(NUM_INDIVIDUALS)]

    def update(self):
        self.ticks += 1

        # TO DO: Update the simulation

    def remove_dead_individuals(self):
        self.individuals = [
            individual for individual in self.individuals if individual.is_alive()
        ]

    def check_interactions(self):
        for individual in self.individuals:
            for other_individual in self.individuals:
                if individual == other_individual:
                    continue

                distance = calculate_distance(
                    individual.x_pos,
                    individual.y_pos,
                    other_individual.x_pos,
                    other_individual.y_pos,
                )
                if distance > INFECTION_RADIUS:
                    continue

                individual_immunity_category = individual.get_immunity_category()
                other_individual_immunity_category = (
                    other_individual.get_immunity_category()
                )

                if individual.state == "ZZ" and other_individual.state == "Z":
                    if individual_immunity_category == "low":
                        individual.state = "Z"
                        individual.reset_state_duration()
                elif individual.state == "ZZ" and other_individual.state == "C":
                    if individual_immunity_category in ("low", "medium"):
                        individual.state = "Z"
                        individual.reset_state_duration()
                    elif individual_immunity_category == "high":
                        individual.update_immunity(-3)
                elif individual.state == "ZZ" and other_individual.state == "ZD":
                    other_individual.update_immunity(1)
                elif individual.state == "ZZ" and other_individual.state == "ZZ":
                    immunity = max(individual.immunity, other_individual.immunity)
                    individual.update_immunity(immunity)
                    other_individual.update_immunity(immunity)
                elif individual.state == "C" and other_individual.state == "Z":
                    if other_individual_immunity_category in ("low", "medium"):
                        other_individual.state = "C"
                        other_individual.reset_state_duration()
                    individual.reset_state_duration()
                elif individual.state == "C" and other_individual.state == "ZD":
                    if other_individual_immunity_category in ("low", "medium"):
                        other_individual.state = "Z"
                        other_individual.reset_state_duration()
                elif individual.state == "C" and other_individual.state == "C":
                    immunity = min(individual.immunity, other_individual.immunity)
                    individual.update_immunity(immunity)
                    other_individual.update_immunity(immunity)
                    individual.reset_state_duration()
                    other_individual.reset_state_duration()
                elif individual.state == "Z" and other_individual.state == "ZD":
                    other_individual.update_immunity(-1)
                elif individual.state == "ZD" and other_individual.state == "ZD":
                    pass

                if (
                    20 <= individual.age <= 40
                    and 20 <= other_individual.age <= 40
                    and random.random() < BIRTH_RATE
                ):
                    self.individuals.append(Individual())

                    if random.random() < BIRTH_RATE / 2:
                        self.individuals.append(Individual())


# now state_duration stars from number of days and goes down to 0
# maybe it would be better to start from 0 and go up to the number of days
if __name__ == "__main__":
    pass
