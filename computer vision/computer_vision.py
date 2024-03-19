import cv2
import apriltag
import numpy as np
import pandas as pd
import matplotlib.animation
import matplotlib.pyplot as plt

import cammands


try:
    capture, detector = cammands.initialize_camera(0, "tag36h11")
    crop_coords = cammands.get_crop_coords(capture, detector)
except TypeError:
    capture, detector = cammands.initialize_camera(1, "tag36h11")
    crop_coords = cammands.get_crop_coords(capture, detector)

print(crop_coords)


plt.rcParams['axes.facecolor'] = 'black'

key = None

def main_loop(i):
    print(i)
    key = None
    if key == ord("q"):
        exit()

    _, raw_frame = capture.read()

    if key == ord("r"):
        crop_coords = cammands.get_crop_coords(capture, detector)

    frame = raw_frame#[crop_coords]

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    detected_tags = detector.detect(gray)
    if len(detected_tags) > 0:
        pointsx = []
        pointsy = []
        for tag in detected_tags:
            pointsx.append(tag["center"][0])
            pointsy.append(tag["center"][1])
        plt.scatter(pointsx, pointsy, c='white', s=100)



    #cv2.imshow("", frame)

    key = cv2.waitKey(1)


"""
Below is the code for creating the figure using pyplot. This is also where we run main_loop.
"""
fig1, ax1 = plt.subplots()
ani = matplotlib.animation.FuncAnimation(fig1, main_loop, frames=100, repeat=False, interval=50)
plt.show()
print("Animation done!")
