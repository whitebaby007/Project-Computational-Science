import matplotlib.pyplot as plt
import numpy as np
import covid_visualize
import cv2
from PIL import Image



SUSCEPTIBLE = 'S'
INFECTED = 'I'
IMMUNE = 'M'
DEAD = 'D'
class Model:
    def __init__(self, width=90, height=90, nHuman=100, nMovehuman=100, initHumanInfected=0.01, initMovehumanInfected=0.01,
                 humanInfectionProb=1, deathrate=0.0009, immune=0.32, image_path='us.jpg'):

        # Process the image and create a binary grid
        original_image = Image.open('us.jpg')
        resized_image = original_image.copy().resize((89, 56))
        gray_image = resized_image.convert('L')
        binary_image = gray_image.point(lambda x: 0 if x < 200 else 1, '1')
        self.grid = np.array(binary_image)

        # Use the binary grid dimensions to set the model width and height
        self.height, self.width = self.grid.shape

        self.nHuman = nHuman
        self.nMovehuman = nMovehuman
        self.humanInfectionProb = humanInfectionProb
        self.deathrate = deathrate
        self.immunity_prob = immune

        # Data parameters
        # To record the evolution of the model
        self.infectedCount = int(self.nHuman * initHumanInfected)
        self.deathCount = 0
        self.infectionCountsOverTime = [self.infectedCount]
        self.deathCountsOverTime = []

        # Population setters
        # Make a data structure in this case a list with the humans and moving humans.
        self.humanPopulation = self.set_human_population(initHumanInfected)
        self.movingHumanPopulation = self.set_moving_human_population(initMovehumanInfected)

    # Other class methods and properties...
    def replace_deceased_human(self, index, population_list, occupied_positions):
        self.deathCount += 1  # Increase death count
        while True:
            new_x = np.random.randint(self.width)
            new_y = np.random.randint(self.height)
        # Check if the new position is not occupied and the grid space is free (black)
            if ((new_x, new_y) not in occupied_positions and self.grid[new_y, new_x] == 0):
                occupied_positions.add((new_x, new_y))  # Mark the position as occupied
                break
        population_list[index] = Human(new_x, new_y, 'S')  # Replace with a new susceptible human
        self.nHuman += 1
    def set_human_population(self, initHumanInfected):
        humanPopulation = []
        occupied_positions = set()

        for j in range(self.nHuman):
            while True:
                x = np.random.randint(self.width)
                y = np.random.randint(self.height)

                # Check if the chosen position is a black cell and not occupied
                if (x, y) not in occupied_positions and self.grid[y, x] == 0:
                    occupied_positions.add((x, y))
                    break

            # Determine infection state based on initial infected ratio
            state = 'I' if (j / self.nHuman) <= initHumanInfected else 'S'

            humanPopulation.append(Human(x, y, state))

        return humanPopulation

    def set_moving_human_population(self, initMovehumanInfected):
        movingHumanPopulation = []
        occupied_positions = set()

        for i in range(self.nMovehuman):
            while True:
                x = np.random.randint(self.width)
                y = np.random.randint(self.height)

                # Check if the chosen position is a black cell and not occupied
                if (x, y) not in occupied_positions and self.grid[y, x] == 0:
                    occupied_positions.add((x, y))
                    break

            state = 'I' if i < self.nMovehuman * initMovehumanInfected else 'S'

            movingHumanPopulation.append(MovingHuman(x, y, state))

        return movingHumanPopulation






    def update(self):

        initial_infected_count = self.infectedCount
        initial_death_count = self.deathCount

    # Set of occupied positions to ensure no overlap when placing new humans
        occupied_positions = set((h.position[0], h.position[1]) for h in self.humanPopulation + self.movingHumanPopulation)

        for i, m in enumerate(self.movingHumanPopulation):
            m.move(sim.grid, sim.height, sim.width)  # Moving humans move first

    # Check for infection against all non-moving humans
            for j, h in enumerate(self.humanPopulation):
                if m.is_close_to(h) and m.state == 'I' and h.state == 'S':
                    if np.random.uniform() <= self.humanInfectionProb:
                        h.state = 'I'
                        self.infectedCount += 1

    # Check for infection against all other moving humans
            for k, other_m in enumerate(self.movingHumanPopulation):
                if i != k and m.is_close_to(other_m) and m.state == 'I' and other_m.state == 'S':
                    if np.random.uniform() <= self.humanInfectionProb:
                        other_m.state = 'I'
                        self.infectedCount += 1


    # This check should be within the same loop that defines 'm'

            if m.state == 'D':
                self.replace_deceased_human(i, self.movingHumanPopulation, occupied_positions)

    # Update for non-moving humans
        for j, h in enumerate(self.humanPopulation):


            if h.state == 'I':
        # Check against non-moving humans
                for k, other_h in enumerate(self.humanPopulation):
                    if j != k and other_h.state == 'S' and h.is_close_to(other_h):
                        if np.random.uniform() <= self.humanInfectionProb:
                            other_h.state = 'I'
                            self.infectedCount += 1

            for m in self.movingHumanPopulation:
                if m.state == 'S' and h.is_close_to(m):
                    if np.random.uniform() <= self.humanInfectionProb:
                        m.state = 'I'
                        self.infectedCount += 1

            if h.state == 'D':
                self.replace_deceased_human(j, self.humanPopulation, occupied_positions)

    # Handling new infections and deaths for statistics
        new_infections = self.infectedCount - initial_infected_count
        new_deaths = self.deathCount - initial_death_count

        self.infectionCountsOverTime.append(new_infections)
        self.deathCountsOverTime.append(new_deaths)

        return self.infectedCount, self.deathCount #return the infactedcount




class MovingHuman:

    MAX_AGE = 500
    MIN_DURATION_BEFORE_DEATH = 50
    IMMUNITY_DURATION = 50
    def __init__(self, x, y, state):
        # Initialize the moving human with a position and infection state
        self.position = [x, y]
        self.state = state  # 'S' for susceptible, 'I' for infected, 'M' for immune



    def is_close_to(self, other_human):
        # Determine if another human is within the infection radius
        infection_radius = 1  # Define how close is 'close'
        return np.linalg.norm(np.array(self.position) - np.array(other_human.position)) < infection_radius

    def move(self, grid, height, width):
        # Attempt to move the human to a black cell within the specified number of tries
        for _ in range(100):  # Limit the number of tries to avoid infinite loops
            # Randomly choose a direction to move
            delta_x = np.random.randint(-1, 2)
            delta_y = np.random.randint(-1, 2)

            # Calculate the new position with wrap-around at edges
            new_x = (self.position[0] + delta_x) % width
            new_y = (self.position[1] + delta_y) % height

            # Check if the new position is a black cell (value 0)
            if grid[new_y, new_x] == 0:
                # Update the position if the cell is black
                self.position[0] = new_x
                self.position[1] = new_y
                return
    def update(self, grid, movingHumanPopulation, deathrate, infection_probability):
        became_immune = False
        # Check for infection state and update infection timer
        if self.state == 'I':
            self.infection_timer += 1
            if self.infection_timer > Human.MIN_DURATION_BEFORE_DEATH:
                if np.random.rand() < deathrate:
                    self.state = 'D'
                elif np.random.rand() < self.immunity_prob:
                    self.state = 'M'
                    became_immune = True

            # Infect other humans if this human is infected
            for other_human in humanPopulation:
                if self is not other_human and self.is_close_to(other_human) and other_human.state == 'S':
                    if np.random.uniform() <= infection_probability:
                        other_human.state = 'I'

        # Handle immunity duration
        if self.state == 'M':
            self.immunity_timer += 1
            if self.immunity_timer > Human.IMMUNITY_DURATION:
                self.state = 'S'
                self.immunity_timer = 0

        return became_immune

class Human:

    MAX_AGE = 500
    MIN_DURATION_BEFORE_DEATH = 50
    IMMUNITY_DURATION = 50

    def __init__(self, x, y, state='S'):
        self.position = [x, y]
        self.state = state
        self.age_timer = 0
        self.infection_timer = 0
        self.immunity_timer = 0
        self.immunity_prob = 0.32

    def is_close_to(self, other_human):
        infection_radius = 1  # Define how close is 'close'
        return np.linalg.norm(np.array(self.position) - np.array(other_human.position)) < infection_radius

    def update(self, deathrate):
        became_immune = False
        self.age_timer += 1
        if self.age_timer > Human.MAX_AGE:
            self.state = 'D'

        if self.state == 'I':
            self.infection_timer += 1
            if self.infection_timer > Human.MIN_DURATION_BEFORE_DEATH:
                if np.random.rand() < deathrate:
                    self.state = 'D'
            elif np.random.rand() < self.immunity_prob:
                self.state = 'M'
                became_immune = True

        if self.state == 'M':
            self.immunity_timer += 1
            if self.immunity_timer > Human.IMMUNITY_DURATION:
                self.state = 'S'
                self.immunity_timer = 0

        return became_immune



if __name__ == '__main__':
    """
    Simulation parameters
    """
    timeSteps = 500
    t = 0
    plotData = True

    infection_counts = []
    death_counts = []

    file = open('simulation.csv', 'w')
    sim = Model(width=894, height=565, image_path='us.jpg')  # Specify the path to your image

    # No need to call load_boundary_from_image if you're not using boundaries
    # sim.load_boundary_from_image()  # Load the boundary from the image

    # Pass the binary grid to Visualization
    vis = covid_visualize.Visualization(sim.height, sim.width, sim.grid)

    print('Starting simulation')
    while t < timeSteps:
        [d1, d2] = sim.update()
        line = str(t) + ',' + str(d1) + ',' + str(d2) + '\n'
        file.write(line)
        vis.update(t, sim.movingHumanPopulation, sim.humanPopulation)
        t += 1
    file.close()
    vis.persist()



    if plotData:
        """
        Make a plot from the stored simulation data.
        """
        data = np.loadtxt('simulation.csv', delimiter=',')
        time = data[:, 0]
        infectedCount = data[:, 1]
        deathCount = data[:, 2]

        infectedPercentage = (infectedCount / sim.nHuman+sim.nMovehuman) * 100# find the percentage of infacted people in the whol population
        deathPercentage = (deathCount / sim.nHuman+sim.nMovehuman) * 100# find the percentage of dead human in the whole population

        plt.figure()
        plt.plot(time, infectedPercentage, label='infected (%)')
        plt.plot(time, deathPercentage, label='deaths (%)')
        plt.xlabel('Time (timesteps)')
        plt.ylabel('Percentage (%)')
        plt.title('Percentage of Infected and Dead Over Time')
        plt.legend()
        plt.show()
