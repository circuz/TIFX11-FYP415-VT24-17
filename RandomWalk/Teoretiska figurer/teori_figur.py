import matplotlib as mpl 
mpl.use('pgf')

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
plt.style.use('seaborn-v0_8')

def check_overlap_and_correct(positions, radius):
    num_particles = len(positions)
    for i in range(num_particles):
        for j in range(i + 1, num_particles):
            displacement = positions[j] - positions[i]
            distance = np.linalg.norm(displacement)
            min_distance = 2 * radius
            if distance < min_distance:
                # Move particles to the minimum distance apart
                correction_vector = displacement * (min_distance - distance) / distance
                positions[i] -= correction_vector / 2
                positions[j] += correction_vector / 2

def attractive_force(positions, radius, v0, box_size):
    num_particles = len(positions)
    velocities = np.zeros_like(positions)
    for i in range(num_particles):
        for j in range(i + 1, num_particles):
            displacement = positions[j] - positions[i]
            distance = np.linalg.norm(displacement)
            if distance > 0:  # Avoid division by zero
                force_magnitude = v0 * (radius ** 2) / (distance ** 2)
                force_vector = displacement * (force_magnitude / distance)
                velocities[i] += force_vector
                velocities[j] -= force_vector  # Equal and opposite force
    return velocities

def simulate_particles(num_particles, steps, radius, v0, box_size=10):
    positions = np.random.rand(num_particles, 2) * box_size
    for _ in range(steps):
        # Apply attractive forces
        velocities = attractive_force(positions, radius, v0, box_size)
        positions += velocities

        # Random small movements
        random_displacements = np.random.randn(num_particles, 2) * 0.1
        positions += random_displacements

        # Apply periodic boundary conditions
        positions %= box_size

        # Correct for overlaps
        check_overlap_and_correct(positions, radius)
    return positions

# Simulation parameters
num_particles = 25
steps = 100
particle_radius = 3
v0 = 0
box_size = 100

# Run simulation
positions = simulate_particles(num_particles, steps, particle_radius, v0, box_size)

# Plot results
plt.figure(figsize=(8, 8))
plt.scatter(positions[:, 0], positions[:, 1], color='blue')
ax = plt.gca()
for i in range(num_particles):
    circle = plt.Circle((positions[i, 0], positions[i, 1]), particle_radius, color='blue', fill=False)
    ax.add_artist(circle)
plt.xlim(0, box_size)
plt.ylim(0, box_size)
# plt.axis('off')
ax.set_aspect('equal', adjustable='box')
ax.set_xticklabels([])
ax.set_yticklabels([])
# plt.show()
plt.savefig(f"./RandomWalk/Teoretiska figurer/levande_kristall_v0={v0}.pgf")
