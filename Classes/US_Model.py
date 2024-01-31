import matplotlib.pyplot as plt
import numpy as np
import covid_visualize
import Human
import MovingHuman
import cv2
from PIL import Image

class Model:
    def __init__(self, width=90, height=60, nHuman=300, nMovehuman=300, initHumanInfected=0.1, initMovehumanInfected=0.1,
                 humanInfectionProb=0.75, VaccinationRate_PerUpdate = 0.01, InfectionProb_Vaccinated = 0.4, deathrate=0.2, immune=0.5,  image_path='US_Population.png'):

        # Process the image and create a binary grid
        original_image = Image.open('US_Population.png')
        resized_image = original_image.copy().resize((90, 60))
        gray_image = resized_image.convert('L')
        binary_image = gray_image.point(lambda x: 1 if x < 33 else 0, '1')
        self.grid = np.array(binary_image)

        # Use the binary grid dimensions to set the model width and height
        self.height, self.width = self.grid.shape

        self.nHuman = nHuman
        self.nMovehuman = nMovehuman
        self.humanInfectionProb = humanInfectionProb
        self.InfectionProb_Vaccinated = InfectionProb_Vaccinated
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

    # Check if we are replacing a MovingHuman or a Human
        if isinstance(population_list[index], MovingHuman.MovingHuman):
            population_list[index] = MovingHuman.MovingHuman(new_x, new_y, 'S')  # Replace with a new susceptible moving human
        else:
            population_list[index] = Human.Human(new_x, new_y, 'S')



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

            humanPopulation.append(Human.Human(x, y, state))

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

            movingHumanPopulation.append(MovingHuman.MovingHuman(x, y, state))

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
        
        #Iterate Movinghuman vaccination + infection
        for i, m in enumerate(self.movingHumanPopulation):
            m.move(self.grid, self.height, self.width)  # Moving humans move first
            
            #apply vaccination 
            if m.vaccinated == 0:
                if np.random.uniform() <= self.VaccinationRate_PerUpdate:
                                h.state = 'I'

            # Infect non-moving humans
            if m.state == 'I':
                for j, h in enumerate(self.humanPopulation):
                    if h.state == 'S' and m.is_close_to(h) and m.state == 'I':
                        
                        #check if other human is vaccinated
                        if h.vaccinated == 1:
                            if np.random.uniform() <= self.InfectionProb_Vaccinated:
                                h.state = 'I'
                                new_infections += 1

                        else:
                            if np.random.uniform() <= self.humanInfectionProb:
                                h.state = 'I'
                                new_infections += 1

            # Infect other moving humans
            if m.state == 'I':
                for k, other_m in enumerate(self.movingHumanPopulation):
                    if i != k and other_m.state == 'S' and m.is_close_to(other_m):
                        
                        #check if other moving human is vaccinated
                        if other_m.vaccinated == 1:
                            if np.random.uniform() <= self.InfectionProb_Vaccinated:
                                other_m.state = 'I'
                                new_infections += 1

                        else:
                            if np.random.uniform() <= self.humanInfectionProb:
                                other_m.state = 'I'
                                new_infections += 1

            # Apply updates for this moving human (death or immunity)
            #Count Immunes
            became_immune = m.update(self.grid, self.movingHumanPopulation, self.deathrate, self.humanInfectionProb)
            if became_immune:
                new_immunities += 1  # Increment the immune count if the individual became immune

            # Replace deceased moving humans
            if m.state == 'D':
                self.replace_deceased_human(i, self.movingHumanPopulation, occupied_positions)
                new_deaths += 1




        #Iterate Non-moving human vaccination + infection
        for j, h in enumerate(self.humanPopulation):

            # Infect other non-moving humans                    
            if h.state == 'I':
                for k, other_h in enumerate(self.humanPopulation):
                    if j != k and other_h.state == 'S' and h.is_close_to(other_h):

                        if other_h.vaccinated == 1:
                            if np.random.uniform() <= self.InfectionProb_Vaccinated:
                                other_h.state = 'I'
                                new_infections += 1

                        else:
                            if np.random.uniform() <= self.humanInfectionProb:
                                other_h.state = 'I'
                                new_infections += 1


            # Infect moving humans
            if h.state == 'I':
                for k, other_m in enumerate(self.movingHumanPopulation):
                    if other_m.state == 'S' and h.is_close_to(other_m):
                        if other_m.vaccinated == 1:
                            if np.random.uniform() <= self.InfectionProb_Vaccinated:
                                other_m.state = 'I'
                                new_infections += 1

                        else:
                            if np.random.uniform() <= self.humanInfectionProb:
                                other_m.state = 'I'
                                new_infections += 1


            # Apply updates for this non-moving human (death or immunity)
            #Count Immunes                    
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
        total_immune = sum(1 for human in self.humanPopulation + self.movingHumanPopulation if human.state == 'M')



        # Since you're removing the dead, you don't need to count 'D' states at each step.
        # The deathCount variable should already be incrementing properly in your code when someone dies.

        self.susceptibleCount = total_susceptible
        self.infectedCount = total_infected
        # self.deathCount is already updated elsewhere in your code whenever someone dies
        self.immuneCount = total_immune


        return self.susceptibleCount, self.infectedCount, self.immuneCount,self.deathCount