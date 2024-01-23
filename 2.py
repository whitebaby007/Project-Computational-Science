import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as mcolors
import random


# Initialize counters for each state


# Define the states
EMPTY, SUSCEPTIBLE, EXPOSED, INFECTED, RECOVERED, VACCINATED = -1, 0, 1, 2, 3, 4

# Set model parameters
grid_size = 70  # Size of the grid
infection_duration = 21  # How long an individual is infected before recovery
initial_infected = 1  # The initial number of infected individuals
infection_probability=0.50
lockdown_factor=1
exposure_duration=3
state_counts = {
    SUSCEPTIBLE: [],
    EXPOSED: [],
    INFECTED: [],
    RECOVERED: [],
    VACCINATED: []
}

num_people = 1000  # The number of susceptible individuals you want to have

grid = np.full((grid_size, grid_size), EMPTY)

# Randomly place susceptible individuals on the grid
filled_cells = set()
while len(filled_cells) < num_people:
    x, y = random.randint(0, grid_size - 1), random.randint(0, grid_size - 1)
    if grid[x, y] == EMPTY:  # Check if the cell is empty
        grid[x, y] = SUSCEPTIBLE
        filled_cells.add((x, y))

# Randomly initialize infected individuals, ensuring they are placed in cells not already occupied
for _ in range(initial_infected):
    x, y = random.randint(0, grid_size - 1), random.randint(0, grid_size - 1)
    while grid[x, y] != EMPTY:  # Ensure the cell is empty before placing an infected individual
        x, y = random.randint(0, grid_size - 1), random.randint(0, grid_size - 1)
    grid[x, y] = INFECTED
def get_neighbors(x, y, grid_size):
    neighbors = []
    for i in range(-1, 2):  # -1, 0, 1
        for j in range(-1, 2):  # -1, 0, 1
            if not (i == 0 and j == 0):  # Exclude the cell itself
                # Wrap around the grid to the other side (toroidal boundary conditions)
                nx, ny = (x + i) % grid_size, (y + j) % grid_size
                neighbors.append((nx, ny))
    return neighbors

def transition_state(x, y, grid, day):
    current_state = grid[x, y]
    neighbors = get_neighbors(x, y, grid_size)

    if current_state == SUSCEPTIBLE:
        if any(grid[nx, ny] == INFECTED for nx, ny in neighbors):
            if random.random() < (infection_probability * lockdown_factor):
                return EXPOSED

    elif current_state == EXPOSED:
        if day >= exposure_duration:  # Transition to infected after exposure duration
            return INFECTED

    elif current_state == INFECTED:
        if day >= infection_duration:  # Transition to recovered after infection duration
            return RECOVERED

    return current_state

def time_step(grid, infection_time_grid, day, infection_probability, exposure_duration, infection_duration, lockdown_factor):
    new_grid = np.copy(grid)
    new_infection_time_grid = np.copy(infection_time_grid)

    for x in range(grid_size):
        for y in range(grid_size):
            if new_grid[x, y] == SUSCEPTIBLE:
                # Check for infected neighbors and possibly become exposed
                neighbors = get_neighbors(x, y, grid_size)
                if any(grid[nx, ny] == INFECTED for nx, ny in neighbors):
                    if random.random() < (infection_probability * lockdown_factor):
                        new_grid[x, y] = EXPOSED
                        # Set the exposure counter when a susceptible becomes exposed
                        new_infection_time_grid[x, y] = exposure_duration

            elif new_grid[x, y] == EXPOSED:
                # If exposed for the set duration, become infected
                new_infection_time_grid[x, y] -= 1  # Decrement the exposure counter
                if new_infection_time_grid[x, y] <= 0:
                    new_grid[x, y] = INFECTED
                    # Set the infection counter when an exposed becomes infected
                    new_infection_time_grid[x, y] = infection_duration

            elif new_grid[x, y] == INFECTED:
                # Decrement the infection counter
                new_infection_time_grid[x, y] -= 1
                if new_infection_time_grid[x, y] <= 0:
                    # After the infection duration, become recovered
                    new_grid[x, y] = RECOVERED



    return new_grid, new_infection_time_grid
# Initialize the grids
grid = np.zeros((grid_size, grid_size), dtype=int)  # The state grid
infection_time_grid = np.zeros_like(grid)  # Grid to track time since infection


# Initialize infected and infection counters
for _ in range(initial_infected):
    x, y = random.randint(0, grid_size-1), random.randint(0, grid_size-1)
    while grid[x, y] != SUSCEPTIBLE:  # Ensure the cell is not already infected
        x, y = random.randint(0, grid_size-1), random.randint(0, grid_size-1)
    grid[x, y] = INFECTED
    infection_time_grid[x, y] = infection_duration




# Visualization setup
cmap = mcolors.ListedColormap(['green', 'yellow', 'red', 'blue', 'purple'])
bounds = [0, 1, 2, 3, 4, 5]
norm = mcolors.BoundaryNorm(bounds, cmap.N)

# Set up the figure for animation
fig, ax = plt.subplots()

# Initialize the grid visualization
img = ax.imshow(grid, cmap=cmap, norm=norm, interpolation='nearest')

# Initialize the time text
time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)

# Create legend patches
patches = [plt.plot([],[], marker="s", ms=10, ls="", mec=None, color=cmap(i),
            label="{:s}".format(text))[0] for i, text in enumerate(['Susceptible', 'Exposed', 'Infected', 'Recovered', 'Vaccinated'])]
plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

# Function to initialize the animation
def init():
    img.set_data(grid)
    time_text.set_text('')
    return (img, time_text)

# Initialize counters for each state
state_counts = {SUSCEPTIBLE: [], EXPOSED: [], INFECTED: [], RECOVERED: [], VACCINATED: []}

# Define the number of frames (time steps)
num_frames = 500

# Function to update the animation
# The animation update function
def animate(i):
    global grid, infection_time_grid

    if i >= 250:
        anim.event_source.stop()
        return
    grid, infection_time_grid = time_step(grid, infection_time_grid, i, infection_probability, exposure_duration, infection_duration, lockdown_factor)
    img.set_data(grid)
    time_text.set_text(f'Time: {i} days')

    # Update counts for each state
    counts = np.bincount(grid.ravel(), minlength=len(state_counts))
    for state, count_list in state_counts.items():
        count_list.append(counts[state])

    return (img, time_text)



# Create the animation object
anim = animation.FuncAnimation(fig, animate, init_func=init, frames=num_frames, interval=50, blit=True)

# Adjust the plot to make space for the legend
plt.subplots_adjust(right=0.7)

# Display the animation
plt.show()

plt.figure(figsize=(10, 6))
for state, state_label in zip([SUSCEPTIBLE, INFECTED, RECOVERED], ['Susceptible', 'Infected', 'Recovered']):
    plt.plot(state_counts[state], label=state_label)
plt.title('Number of Individuals Over Time')
plt.xlabel('Time (Days)')
plt.ylabel('Number of Individuals')
plt.legend()
plt.show()
