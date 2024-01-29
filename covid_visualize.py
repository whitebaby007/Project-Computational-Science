import numpy as np
import matplotlib
# matplotlib.use('TkAgg') # Mac specific
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


class Visualization:
    def __init__(self, height, width, image_grid, pauseTime=0.1):
        self.h = height
        self.w = width
        self.pauseTime = pauseTime
        self.image_grid = image_grid  # Store the processed image grid

        # Initialize a grid to track the states of individuals, set to -1 initially
        self.state_grid = np.full((self.h, self.w), -1)

        # Define a custom colormap including a color for 'empty' state
        self.cmap = ListedColormap(['black', 'white', 'red', 'yellow', 'green'])  # Adding 'green' for 'empty'

        # Initialize the plot with the image grid
        self.fig, self.ax = plt.subplots()
        self.im = self.ax.imshow(self.image_grid, cmap='gray', vmin=0, vmax=1)
        self.overlay = self.ax.imshow(self.state_grid, cmap=self.cmap, vmin=-1, vmax=3, alpha=0.5)

    def update(self, t, movingHumanPopulation, humanPopulation):
        # Reset the state grid to -1 (empty) each time
        self.state_grid.fill(-1)

        # Update the state grid with the positions of humans and moving humans
        for m in movingHumanPopulation:
            if m.state == 'I':  # Infected
                self.state_grid[m.position[1], m.position[0]] = 1
            elif m.state == 'S':  # Susceptible
                self.state_grid[m.position[1], m.position[0]] = 3

        for h in humanPopulation:
            if h.state == 'I':  # Infected
                self.state_grid[h.position[1], h.position[0]] = 1
            elif h.state == 'S':  # Susceptible
                self.state_grid[h.position[1], h.position[0]] = 3

        # Update the overlay with the state grid
        self.overlay.set_data(self.state_grid)
        self.ax.set_title('t = %i' % t)
        plt.draw()
        plt.pause(self.pauseTime)

    def persist(self):
        plt.show()
