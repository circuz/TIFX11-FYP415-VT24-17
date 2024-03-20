import cv2
import datetime
import apriltag
import numpy as np
import pandas as pd
import matplotlib.animation
import matplotlib.pyplot as plt

from functools import partial

import cammands

CHEMOTAXI = True

try:
    capture, detector = cammands.initialize_camera(0, "tag36h11")
    crop_coords = cammands.get_crop_coords(capture, detector)
except TypeError:
    try:
        capture, detector = cammands.initialize_camera(1, "tag36h11")
        crop_coords = cammands.get_crop_coords(capture, detector)
    except TypeError:
        capture, detector = cammands.initialize_camera(2, "tag36h11")
        crop_coords = cammands.get_crop_coords(capture, detector)

print(crop_coords)

_, frame = capture.read()
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
detected_tags = detector.detect(gray)
tagids = { tag['id'] : [] for tag in detected_tags }
dataframe = pd.DataFrame(tagids)
print(dataframe)


def main_loop(i, df):
    print(i)
    # Initialize each row to a bunch of Nones
    df.loc[f'{i}_x'] = np.NaN
    df.loc[f'{i}_y'] = np.NaN

    key = None

    if key == ord("q"):
        exit()

    _, raw_frame = capture.read()

    if key == ord("r"):
        crop_coords = cammands.get_crop_coords(capture, detector)

    if ((i+1) % 50) == 0:
        csv_name = f'{datetime.datetime.now()}.csv'
        print(csv_name)
        df.to_csv(csv_name)

    frame = raw_frame#[crop_coords]

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    detected_tags = detector.detect(gray)

    # If there are any tags visible in the camera record them and we are doing chemotaxi, plot them!
    if (len(detected_tags) > 0):
        
        if CHEMOTAXI:
            pointsx = []
            pointsy = []

        for tag in detected_tags:
            name = tag["id"]
            if not (name in df.columns):
                df.insert(0, name, np.NaN)
            xpoint = tag["center"][0]
            ypoint = tag["center"][1]
            df.loc[f'{i}_x'][name] = xpoint
            df.loc[f'{i}_y'][name] = ypoint
            if CHEMOTAXI:
                pointsx.append(xpoint)
                pointsy.append(ypoint)
            
            plt.scatter(pointsx, pointsy, c='white', s=100)



    #cv2.imshow("", frame)

    key = cv2.waitKey(1)


"""
Below is the code for creating the figure using pyplot. This is also where we run main_loop.
"""
fig1, ax1 = plt.subplots()

if CHEMOTAXI:
    ax1.set_facecolor('black')

main_loop_with_args = partial(main_loop, df=dataframe)

ani = matplotlib.animation.FuncAnimation(fig1, main_loop_with_args, frames=100, repeat=False, interval=50)
plt.show()
print("We're done here!")
