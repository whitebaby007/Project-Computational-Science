import matplotlib.pyplot as plt
import numpy as np
import covid_visualize
import Human
import Classes.US_Model as US_Model
import cv2
from PIL import Image

class MovingHuman:

    MAX_AGE = 500
    MIN_DURATION_BEFORE_DEATH = 21
    def __init__(self, x, y, state='S'):
        # Initialize the moving human with a position and infection state
        self.position = [x, y]
        self.state = state  # 'S' for susceptible, 'I' for infected, 'M' for immune
        self.infection_timer = 0
        self.immunity_prob =0.31
        self.vaccinated = 0
        
    def is_close_to(self, other_human):
        # Determine if another human is within the infection radius
        infection_radius = 2.0  # Define how close is 'close'
        return float(np.linalg.norm(np.array(self.position) - np.array(other_human.position))) < infection_radius

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
            if self.infection_timer > Human.Human.MIN_DURATION_BEFORE_DEATH:
                if np.random.rand() < deathrate:
                    self.state = 'D'
                elif np.random.rand() < self.immunity_prob:
                    self.state = 'M'
                    became_immune = True
                else:
            # Explicitly stating that the person remains infected
                    self.state = 'I'

        return became_immune