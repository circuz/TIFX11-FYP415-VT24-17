import matplotlib as mpl 
# mpl.use('pgf')

import pandas as pd
import numpy as np
from scipy.spatial.distance import pdist, squareform
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.lines import Line2D
plt.style.use('seaborn-v0_8')

def process__and_plot_frame(frame):
    # Load data using the first column as index (robot IDs)
    file_path = 'RandomWalk/Mätningar/19RobotarNyKamera/2024-04-21 12:11:07.551996.csv'
    data = pd.read_csv(file_path, index_col=0)

    # Filter columns that end in '_x' or '_y'
    relevant_columns = [col for col in data.columns if col.endswith('_x') or col.endswith('_y')]
    data = data[relevant_columns]

    # Set robots radius
    radius = 70

    fig, ax = plt.subplots()

    # Plot each robot's trajectory
    for index, (robot_id, robot_row) in enumerate(data.iterrows()):
        x_data = robot_row[[col for col in data.columns if col.endswith('_x')]]
        y_data = robot_row[[col for col in data.columns if col.endswith('_y')]]

        # Check where data is originally NaN
        x_is_nan = x_data.isna()
        y_is_nan = y_data.isna()

        # Interpolate missing values
        x_interpolated = x_data.interpolate().fillna(method='bfill').fillna(method='ffill')
        y_interpolated = y_data.interpolate().fillna(method='bfill').fillna(method='ffill')
        # Plot the paths and points for a single given index

        if ~x_is_nan[frame]:
            ax.scatter(x_interpolated[frame], y_interpolated[frame], color='blue')
            circle_original = Circle((x_interpolated[frame], y_interpolated[frame]), radius, color='blue', fill=False)
            ax.add_patch(circle_original)
        else:
            ax.scatter(x_interpolated[frame], y_interpolated[frame], color='red', marker='D')
            circle_interpolated = Circle((x_interpolated[frame], y_interpolated[frame]), radius, color='red', fill=False)
            ax.add_patch(circle_interpolated)

    # Final plot adjustments
    original = Line2D([], [], color='blue', linestyle='None', marker='o', label="Uppmätt robotposition")
    interpolerad = Line2D([], [], color='red', linestyle='None', marker='D', label="Interpolerad robotposition")
    plt.legend(handles=[original, interpolerad])
    ax.set_aspect('equal')
    ax.set_title(f'Robotarnas positioner vid bild {frame}')
    ax.set_xlabel('X-koordinat')
    ax.set_ylabel('Y-koordinat')
    ax.set_xlim(-200,2800)
    ax.set_ylim(-200,2800)
    plt.show()
    # plt.savefig(f"./RandomWalk/Mätningar/levande_kristaller/levande_kristall_bild{frame}.pgf")

process__and_plot_frame(47)