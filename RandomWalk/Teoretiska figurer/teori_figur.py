import numpy as np
import matplotlib.pyplot as plt

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

def simulate_particles(num_particles, steps, radius, box_size=10):
    positions = np.random.rand(num_particles, 2) * box_size
    for _ in range(steps):
        # Random small movements
        random_displacements = np.random.randn(num_particles, 2) * 0.1
        positions += random_displacements
        # Apply periodic boundary conditions
        positions %= box_size
        # Correct for overlaps
        check_overlap_and_correct(positions, radius)
    return positions

# Simulation parameters
num_particles = 100
steps = 1000
particle_radius = 0.1
box_size = 10

# Run simulation
positions = simulate_particles(num_particles, steps, particle_radius, box_size)

# Plot results
plt.figure(figsize=(8, 8))
plt.scatter(positions[:, 0], positions[:, 1], s=10)
plt.xlim(0, box_size)
plt.ylim(0, box_size)
plt.title('Particle positions after simulation with volume exclusion')
plt.gca().set_aspect('equal', adjustable='box')
plt.show()
