import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

################ ChatGPTs kod  ##################

def read_csv_with_coordinates(filename):
    # Load the CSV file, treating the first row and the first column as headers
    df = pd.read_csv(filename, index_col=0, header=0)

    # Filter out the rows that contain names, which are now the indexes in the DataFrame
    # We assume that name rows contain numeric data in coordinate columns (like 0_x, 0_y, etc.)
    # and that non-name rows contain non-numeric data that we can discard.
    df = df[df.index.to_series().str.isnumeric()]

    # Initialize a dictionary to store coordinates
    coordinates = {}

    # Iterate through rows, assuming each row now represents a name with all x and y coordinates
    for index, row in df.iterrows():
        # Collect all x and y coordinates for this name (index)
        x_coords = []
        y_coords = []
        for col in df.columns:
            if '_x' in col:
                x_coords.append(row[col])
            elif '_y' in col:
                y_coords.append(row[col])

        # Store the collected coordinates as pairs
        coordinates[index] = list(zip(x_coords, y_coords))

    return coordinates

############### ------ #################

# print("Current working directory:", os.getcwd())
filename = './RandomWalk/Mätningar/16_apr_1.csv'

data_points = read_csv_with_coordinates(filename)

def plot_paths(data_points, names_to_plot):
    plt.figure(figsize=(10, 6))
    for name in names_to_plot:
        if name in data_points:
            coords = np.array(data_points[name])
            plt.plot(coords[:, 0], coords[:, 1], marker='o', label=f'Path for {name}')
        else:
            print(f"Name '{name}' not found in data points.")
    
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.title('Paths of Selected Names')
    plt.legend()
    plt.grid(True)
    plt.show()

# print(data_points)
names_to_plot = ['12']  # Update this list with the names you want to plot
plot_paths(data_points, names_to_plot)
