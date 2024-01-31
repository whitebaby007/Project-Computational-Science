import matplotlib.pyplot as plt
import numpy as np
from Classes import covid_visualize
from Classes import Human
from Classes import MovingHuman
from Classes import US_Model
import cv2
from PIL import Image



SUSCEPTIBLE = 'S'
INFECTED = 'I'
IMMUNE = 'M'
DEAD = 'D'


if __name__ == '__main__':
    # Simulation parameters
    timeSteps = 200
    t = 0
    plotData = True

    # Create an instance of the Model class
    sim = US_Model.Model(nHuman=750, nMovehuman=750, initHumanInfected=0.01, initMovehumanInfected=0.01,
                 humanInfectionProb=0.35, VaccinationRate_PerUpdate = 0.0, InfectionProb_Vaccinated = 0.35, deathrate=0.05, immune=0.95,  image_path='US_Population.png')

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
        line = f"{t}, {susceptible}, {infected}, {dead}, {immune}\n"
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
