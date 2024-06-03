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

print(STATE_VALUES[-1])


# FUNCTIONS
def get_random_direction(current_direction=None):
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]
    if current_direction is not None:
        directions.remove(current_direction)

    return random.choice(directions)


# CLASSES
class Individual:
    def __init__(self, individual_max_age=MAX_AGE):
        self.x_pos = random.randint(0, GRID_WIDTH)
        self.y_pos = random.randint(0, GRID_HEIGHT)
        self.speed = random.choice(SPEED_VALUES)
        self.x_direction, self.y_direction = get_random_direction()
        self.age = random.randint(0, individual_max_age)
        self.immunity = self.get_initial_immunity()
        self.state = random.choice(STATE_VALUES)
        self.state_duration = STATE_DURATIONS[self.state]
        self.isAlive = True

    def get_initial_immunity(self):
        """Return the initial immunity of the individual based on their age."""

        if self.age < 15 or self.age > 70:
            return random.uniform(0, 3) + MIN_FLOAT
        elif 40 <= self.age < 70:
            return random.uniform(3, 6) + MIN_FLOAT
        elif 15 <= self.age < 40:
            return random.uniform(6, 10) + MIN_FLOAT

    def update_position(self):
        """Update the position of the individual."""

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

    def update_age(self):
        self.age += 1

        if self.age >= MAX_AGE:
            self.isAlive = False

    def update_state(self):
        """Update the state of the individual."""

        self.update_age()

        # Check if the individual is dead
        if not self.is_alive():
            return

        self.state_duration -= 1

        if self.state == "Z":
            immunity_diff = -0.1
        elif self.state == "C":
            immunity_diff = -0.5
        elif self.state == "ZD":
            immunity_diff = 0.1
        elif self.state == "ZZ":
            immunity_diff = 0.05

        # Update the immunity of the individual
        if immunity_diff < 0:
            self.immunity += immunity_diff
        else:
            # limit the immunity to the maximum immunity
            max_immunity = self.get_max_immunity()
            self.immunity = min(self.immunity + immunity_diff, max_immunity)

        # Check if the individual is dead
        if self.immunity <= 0:
            self.isAlive = False
            return

        if self.state_duration == 0:
            if self.state == "Z":
                self.state = "C"
            elif self.state == "C":
                self.state = "ZD"
            elif self.state == "ZD":
                self.state = "ZZ"

            self.state_duration = STATE_DURATIONS[self.state]

    def get_max_immunity(self):
        if self.age < 15 or self.age > 70:
            return 3
        elif 40 <= self.age < 70:
            return 6
        elif 15 <= self.age < 40:
            return 10

    def is_alive(self):
        return self.isAlive


class Simulation:
    def __init__(self):
        pass


if __name__ == "__main__":
    pass
