"""
=========================================================
                        PACKAGES
This is a bunch of stuff we need for running the program.
After each of the packages (cv2, datetime, apriltag, ...) 
we'll write a small description of what it's used it for.
"""
import cv2 # This is the package we have for using webcam
import datetime # Date, time are used for naming csv file
import apriltag # Apriltags are the (not at all) QR codes
import numpy as np # np contains a lot of good math stuff
import pandas as pd # Pandas saves the data to a csv file
import matplotlib.animation # We use to run the main_loop
import matplotlib.pyplot as plt # For plotting chemtrails

from functools import partial # Is help for the main_loop

import cammands # We wrote a few neat functions ourselves
"""
=========================================================
                      PARAMETERS
Change these parameters to change how the program is run.
"""
CHEMOTAXI = False # Are you running chemotaxi experiment?
RUNTIME = 100 # Number of frames to be recorded, e.g. 100
FRAMETIME = 5 # Number of ms/frame (in theory) low = good
"""
=========================================================
               PREPARING COMPUTER VISION
Establish the video capturer object and apriltag detector
used later in the script. This code block also *tries* to
fix the error that sometimes happens with webcam. Mostly.
"""
try: # If cam isn't '/dev/video0' it wil throw TypeError.
    capture, detector = cammands.initialize_camera(0, "tag36h11")
    crop_coords = cammands.get_crop_coords(capture, detector)
except TypeError: # Then '/dev/video1' should be correct!
    capture, detector = cammands.initialize_camera(1, "tag36h11")
    crop_coords = cammands.get_crop_coords(capture, detector)
"""
=========================================================
                   PANDAS DATAFRAME
Here we initialize the pandas dataframe used to store our
data to [date].csv files located in the "../data" folder.
"""
_, frame = capture.read() # "frame" is what the cam sees.
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # decolor!
detected_tags = detector.detect(gray) # Try to find tags.
# The code below creates a dictionary that is on the form 
# {X:[], Y:[], ...}, for example {1:[], 7:[], 8:[], 4:[]}
# by going over detected_tags and saving each in tag_ids.
tag_ids = { onetag['id']:[] for onetag in detected_tags }
dataframe = pd.DataFrame(tag_ids) # making the DataFrame.
"""
=========================================================
                        PROGRAM
This is the main program loop of this file. This is where
the logic, plotting, projecting, and computer vision will
all be controlled from. It's run from the FuncAnimation()
call in the bottom of the entire computer_vision.py file.
"""
def main_loop(i, df):
    print(i) # 'i' is a variable that increases each loop

    # We begin with initializing each of coordinate for a
    # frame for all robots with NaN which means undefined
    df.loc[f'{i}_x'] = np.NaN # We dont know x values yet
    df.loc[f'{i}_y'] = np.NaN # We dont know y values yet


    key = None

    if key == ord("q"):
        exit()


    if key == ord("r"):
        crop_coords = cammands.get_crop_coords(capture, detector)
        frame = frame[crop_coords]

    if ((i+1) % 50) == 0:
        csv_name = f'../data/{datetime.datetime.now()}.csv'
        print(csv_name)
        df.to_csv(csv_name)

    _, frame = capture.read()

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
            
        if CHEMOTAXI:
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

ani = matplotlib.animation.FuncAnimation(fig1, main_loop_with_args, frames=RUNTIME, repeat=False, interval=FRAMETIME)
plt.show()
print("We're done here!")
