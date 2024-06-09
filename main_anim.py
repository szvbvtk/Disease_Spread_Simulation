import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.animation import FuncAnimation
import random
import sys

round.seed(212112)

# CONSTANTS
GRID_WIDTH = 100
GRID_HEIGHT = 100
NUM_INDIVIDUALS = 100
NUMBER_OF_TICKS = 10
SHOW_GRID = True
ANIMATION_PAUSE = 0.1
MAX_AGE = 100
DOT_SIZE = 0.5
SPEED_VALUES = (1, 2, 3)
# C - ill, Z - infected, ZD - convalescing, ZZ - healthy
STATE_COLORS = {"C": "red", "Z": "yellow", "ZD": "orange", "ZZ": "green"}
# In days
STATE_MAX_DURATIONS = {"Z": 2, "C": 7, "ZD": 5, "ZZ": -1}
# radius in which the infection can spread
INFECTION_RADIUS = 2
# probability of giving birth to one child, rate is halved for second child
BIRTH_RATE = 0.1
# do not change the following two lines
STATE_VALUES = tuple(STATE_COLORS.keys())
MIN_FLOAT = sys.float_info.min


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
    def __init__(
        self,
        birth=False,
        individual_max_age=MAX_AGE,
        parent_x_pos=None,
        parent_y_pos=None,
    ):
        # self.x_pos = random.randint(0, GRID_WIDTH)
        # self.y_pos = random.randint(0, GRID_HEIGHT)
        self.x_pos = random.uniform(DOT_SIZE, GRID_WIDTH - DOT_SIZE)
        self.y_pos = random.uniform(DOT_SIZE, GRID_HEIGHT - DOT_SIZE)
        self.speed = random.choice(SPEED_VALUES)
        self.x_direction, self.y_direction = get_random_direction()

        if not birth:
            self.age = random.randint(0, individual_max_age)
            self.immunity = self.get_initial_immunity()
            self.state = random.choice(STATE_VALUES)
            self.isAlive = True

            if self.state == "ZZ":
                self.state_duration = STATE_MAX_DURATIONS[self.state]
            else:
                self.state_duration = random.randint(1, STATE_MAX_DURATIONS[self.state])
        else:
            self.x_pos = parent_x_pos
            self.y_pos = parent_y_pos
            self.age = 0
            self.immunity = 10
            self.state = "ZZ"
            self.isAlive = True

            self.state_duration = STATE_MAX_DURATIONS[self.state]

    def get_initial_immunity(self):
        """Return the initial immunity of the individual based on their age."""

        if self.age < 15 or self.age >= 70:
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
        if self.x_pos <= DOT_SIZE:
            self.x_pos = DOT_SIZE
            self.x_direction = 1
        elif self.x_pos >= GRID_WIDTH - DOT_SIZE:
            self.x_pos = GRID_WIDTH - DOT_SIZE
            self.x_direction = -1

        if self.y_pos < -DOT_SIZE:
            self.y_pos = DOT_SIZE
            self.y_direction = 1
        elif self.y_pos >= GRID_HEIGHT - DOT_SIZE:
            self.y_pos = GRID_HEIGHT - DOT_SIZE
            self.y_direction = -1

    def update_state(self):
        """Update the state of the individual."""

        # Check if the individual is dead
        if not self.is_alive():
            return

        if self.state != "ZZ":
            self.state_duration += 1

            # dont know whether its the right way to update the state
            if self.state_duration == STATE_MAX_DURATIONS[self.state]:
                if self.state == "Z":
                    self.state = "C"
                elif self.state == "C":
                    self.state = "ZD"
                elif self.state == "ZD":
                    self.state = "ZZ"

                self.state_duration = STATE_MAX_DURATIONS[self.state]

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
        if self.age < 15 or self.age >= 70:
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
        self.state_duration = STATE_MAX_DURATIONS[self.state]

    def is_alive(self):
        return self.isAlive


class Simulation:
    def __init__(self, num_ticks=100):
        # 1 tick = 1 day
        self.current_tick = 0
        self.num_ticks = num_ticks
        self.individuals = [
            Individual(birth=False, individual_max_age=60)
            for _ in range(NUM_INDIVIDUALS)
        ]

    def update(self):
        self.current_tick += 1

        for individual in self.individuals:
            individual.update()

        self.remove_dead_individuals()
        self.check_interactions()

    def remove_dead_individuals(self):
        self.individuals = [
            individual for individual in self.individuals if individual.is_alive()
        ]

    def check_interactions(self):
        for i, individual in enumerate(self.individuals):
            # so that we don't check the same pair twice
            for other_individual in self.individuals[i + 1 :]:
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

                # if distance <= DOT_SIZE:
                #     individual.x_direction, individual.y_direction = get_random_direction(
                #         (individual.x_direction, individual.y_direction)
                #     )
                #     other_individual.x_direction, other_individual.y_direction = get_random_direction(
                #         (other_individual.x_direction, other_individual.y_direction)
                #     )

                if (
                    abs(individual.x_pos - other_individual.x_pos) <= 0
                    and abs(individual.y_pos - other_individual.y_pos) <= 0
                ):
                    individual.x_direction, individual.y_direction = (
                        get_random_direction(
                            (individual.x_direction, individual.y_direction)
                        )
                    )
                    other_individual.x_direction, other_individual.y_direction = (
                        get_random_direction(
                            (individual.x_direction, individual.y_direction)
                        )
                    )

                # if the individuals are close enough, check if they can infect each other
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

                # reproduction
                if (
                    20 <= individual.age <= 40
                    and 20 <= other_individual.age <= 40
                    and random.random() < BIRTH_RATE
                ):
                    self.individuals.append(
                        Individual(
                            birth=True,
                            parent_x_pos=individual.x_pos,
                            parent_y_pos=individual.y_pos,
                        )
                    )

                    if random.random() < BIRTH_RATE / 2:
                        self.individuals.append(
                            Individual(
                                birth=True,
                                parent_x_pos=individual.x_pos,
                                parent_y_pos=individual.y_pos,
                            )
                        )

    def draw(self, ax):
        ax.clear()
        ax.set_xlim(0, GRID_WIDTH)
        ax.set_ylim(0, GRID_HEIGHT)

        ax.set_yticks([])
        ax.set_yticks([])

        if SHOW_GRID:
            ax.set_xticks(range(0, GRID_WIDTH + 1, 1))
            ax.set_yticks(range(0, GRID_HEIGHT + 1, 1))
            ax.set_xticklabels([])
            ax.set_yticklabels([])
            ax.grid(True, alpha=0.5)

        for individual in self.individuals:
            ax.add_patch(
                mpatches.Circle(
                    (individual.x_pos, individual.y_pos),
                    DOT_SIZE,
                    color=STATE_COLORS[individual.state],
                )
            )

        ax.set_title(f"Day: {self.current_tick}")

        if self.current_tick == self.num_ticks:
            ax.text(
                GRID_WIDTH / 2,
                GRID_HEIGHT / 2,
                "Simulation has ended",
                fontsize=20,
                ha="center",
                va="center",
            )
            self.current_tick = 0


def init():
    ax.set_xlim(0, GRID_WIDTH)
    ax.set_ylim(0, GRID_HEIGHT)
    ax.set_yticks([])
    ax.set_xticks([])
    if SHOW_GRID:
        ax.set_xticks(range(0, GRID_WIDTH + 1, 1))
        ax.set_yticks(range(0, GRID_HEIGHT + 1, 1))
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.grid(True, alpha=0.5)

    ax.set_title("Day: 1")
    return []


def update(frame, sim, ax):
    sim.update()
    sim.draw(ax)


if __name__ == "__main__":
    fig, ax = plt.subplots(num="virus spread", figsize=(10, 10))
    fig.set_tight_layout(True)
    # fig.suptitle("Simulation of a virus spread")

    sim = Simulation(num_ticks=NUMBER_OF_TICKS)
    ani = FuncAnimation(
        fig,
        update,
        fargs=(sim, ax),
        frames=NUMBER_OF_TICKS,
        init_func=init,
        repeat=False,
        # repeat_delay=3000,
        interval=ANIMATION_PAUSE * 1000,
    )
    plt.show()
