import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# import os

################ ChatGPTs kod  ##################

def read_csv_with_coordinates(filename):
    # Load the CSV file, assuming the first row contains the headers and skip the first column
    df = pd.read_csv(filename, index_col=0)

    # Initialize a dictionary to store coordinates
    coordinates = {}
    
    # Iterate over each column, assuming each column represents one name with its x, y coordinates interleaved
    for name in df.columns:
        # Extracting values as floats; assuming rows alternate between x and y coordinates starting with x
        coords = df[name].replace('', np.nan).dropna().astype(float)
        x_coords = coords[::2]  # Even index rows: x-coordinates
        y_coords = coords[1::2]  # Odd index rows: y-coordinates
        coordinates[name] = list(zip(x_coords, y_coords))

    return coordinates

############### ------ #################

# print("Current working directory:", os.getcwd())
filename = './Mätningar/14_apr_1.csv'

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
names_to_plot = ['21']  # Update this list with the names you want to plot
plot_paths(data_points, names_to_plot)

