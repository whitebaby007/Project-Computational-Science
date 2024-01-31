import matplotlib.pyplot as plt
import numpy as np
import covid_visualize
import MovingHuman
import Classes.US_Model as US_Model
import cv2
from PIL import Image

class Human:

    MIN_DURATION_BEFORE_DEATH = 21

    def __init__(self, x, y, state='S'):
        self.position = [x, y]
        self.state = state
        self.infection_timer = 0
        self.immunity_prob=0.31
        self.vaccinated = 0

    def is_close_to(self, other_human):
        infection_radius = 2.0  # Define how close is 'close'
        return float(np.linalg.norm(np.array(self.position) - np.array(other_human.position))) < infection_radius

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
                else:
                    self.state ='I'


        return became_immune