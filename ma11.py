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
    def __init__(self, width=90, height=90, nHuman=10, nMovehuman=1, initHumanInfected=0.1, initMovehumanInfected=0.1,
                 humanInfectionProb=1, deathrate=0.1, immune=0.32, image_path='us.jpg'):

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

        self.immuneCount = 0  # Add this attribute to track the immune count
        self.immuneCountsOverTime = []
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
        initial_immune_count = self.immuneCount
        new_infections = 0
        new_deaths = 0
        new_immunities = 0
    # Set of occupied positions to ensure no overlap when placing new humans
        occupied_positions = set((h.position[0], h.position[1]) for h in self.humanPopulation + self.movingHumanPopulation)

        for i, m in enumerate(self.movingHumanPopulation):
            m.move(self.grid, self.height, self.width)  # Moving humans move first

            # Check for infection against all non-moving humans
            if m.state == 'I':
                for j, h in enumerate(self.humanPopulation):
                    if h.state == 'S' and m.is_close_to(h) and m.state == 'I':
                        if np.random.uniform() <= self.humanInfectionProb:
                            h.state = 'I'
                            new_infections += 1

            # Check for infection against all other moving humans
            if m.state == 'I':
                for k, other_m in enumerate(self.movingHumanPopulation):
                    if i != k and other_m.state == 'S' and m.is_close_to(other_m):
                        if np.random.uniform() <= self.humanInfectionProb:
                            other_m.state = 'I'
                            self.infectedCount += 1

            # Apply updates for this moving human (death or immunity)
            became_immune = m.update(self.grid, self.movingHumanPopulation, self.deathrate, self.humanInfectionProb)
            if became_immune:
                new_immunities += 1  # Increment the immune count if the individual became immune

            # Replace deceased moving humans
            if m.state == 'D':
                self.replace_deceased_human(i, self.movingHumanPopulation, occupied_positions)
                new_deaths += 1

        # Update for non-moving humans
        for j, h in enumerate(self.humanPopulation):
            if h.state == 'I':
                for k, other_h in enumerate(self.humanPopulation):
                    if j != k and other_h.state == 'S' and h.is_close_to(other_h):
                        if np.random.uniform() <= self.humanInfectionProb:
                            other_h.state = 'I'
                            self.infectedCount += 1

    # Check for infection against all moving humans
            if h.state == 'I':
                for k, other_m in enumerate(self.movingHumanPopulation):
                    if other_m.state == 'S' and h.is_close_to(other_m):
                        if np.random.uniform() <= self.humanInfectionProb:
                            other_m.state = 'I'
                            self.infectedCount += 1

            became_immune = h.update(self.grid, self.humanPopulation, self.deathrate, self.humanInfectionProb)
            if became_immune:
                new_immunities += 1  # Increment the immune count if the individual became immune

            # Replace deceased non-moving humans
            if h.state == 'D':
                self.replace_deceased_human(j, self.humanPopulation, occupied_positions)
                new_deaths += 1

        # Update the model's counts based on this timestep's events
        total_susceptible = sum(1 for human in self.humanPopulation + self.movingHumanPopulation if human.state == 'S')
        total_infected = sum(1 for human in self.humanPopulation + self.movingHumanPopulation if human.state == 'I')
        total_dead = sum(1 for human in self.humanPopulation + self.movingHumanPopulation if human.state == 'D')
        total_immune = sum(1 for human in self.humanPopulation + self.movingHumanPopulation if human.state == 'M')

        # Update the model's counts based on this timestep's events
        self.susceptibleCount = total_susceptible
        self.infectedCount = total_infected
        self.deathCount = total_dead
        self.immuneCount = total_immune


        return self.susceptibleCount, self.infectedCount, self.deathCount, self.immuneCount




class MovingHuman:

    MAX_AGE = 500
    MIN_DURATION_BEFORE_DEATH = 100
    def __init__(self, x, y, state='S'):
        # Initialize the moving human with a position and infection state
        self.position = [x, y]
        self.state = state  # 'S' for susceptible, 'I' for infected, 'M' for immune
        self.infection_timer = 0
        self.immunity_prob = 0.01

    def is_close_to(self, other_human):
        # Determine if another human is within the infection radius
        infection_radius = 2  # Define how close is 'close'
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

        if np.random.rand() < self.immunity_prob:
                self.state = 'M'
                became_immune = True

        return became_immune

class Human:

    MIN_DURATION_BEFORE_DEATH = 100

    def __init__(self, x, y, state='S'):
        self.position = [x, y]
        self.state = state
        self.infection_timer = 0
        self.immunity_timer = 0
        self.immunity_prob = 0.01

    def is_close_to(self, other_human):
        infection_radius = 2  # Define how close is 'close'
        return np.linalg.norm(np.array(self.position) - np.array(other_human.position)) < infection_radius

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

        if np.random.rand() < self.immunity_prob:
                self.state = 'M'
                became_immune = True

        return became_immune



if __name__ == '__main__':
    # Simulation parameters
    timeSteps = 500
    t = 0
    plotData = True

    # Create an instance of the Model class
    sim = Model()

    # Initialize lists for storing simulation data
    susceptible_counts = []
    infected_counts = []
    immune_counts = []
    death_counts = []

    # Open the file to write simulation data
    file = open('simulation.csv', 'w')
    file.write("Time,Susceptible,Infected,Immune,Dead\n")  # Include headers for the CSV file

    # Pass the binary grid to Visualization
    vis = covid_visualize.Visualization(sim.height, sim.width, sim.grid)

    print('Starting simulation')
    while t < timeSteps:
        susceptible, infected, immune, dead = sim.update()
        line = f"{t}, {susceptible}, {infected}, {immune}, {dead}\n"
        file.write(line)

        # Store the data for plotting
        susceptible_counts.append(susceptible)
        infected_counts.append(infected)
        immune_counts.append(immune)
        death_counts.append(dead)

        vis.update(t, sim.movingHumanPopulation, sim.humanPopulation)
        t += 1

    file.close()
    vis.persist()

    if plotData:
        # Plotting the data
        plt.figure()
        plt.plot(range(timeSteps), susceptible_counts, label='Susceptible')
        plt.plot(range(timeSteps), infected_counts, label='Infected')
        plt.plot(range(timeSteps), immune_counts, label='Immune')
        plt.plot(range(timeSteps), death_counts, label='Dead')
        plt.xlabel('Time (timesteps)')
        plt.ylabel('Number of People')
        plt.title('Trajectory of Infection and Recovery Over Time')
        plt.legend()
        plt.show()
