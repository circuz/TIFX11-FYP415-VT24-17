import cv2
import apriltag
import numpy

def initialize_camera(camera_id = 0, tag_type = "tag36h11"):
    """
    This command is used to initialize the camera and detector
    TODO: add error handling
    """
    capture = cv2.VideoCapture(camera_id)
    detector = apriltag.apriltag(tag_type)
    return capture, detector

def get_crop_coords(video_capture, apriltag_detector):
    """
    This command is used to get the coordinates of the most extreme points on any apriltag in view.
    TODO: maybe add a bit of padding
    """
    _, init_frame = video_capture.read()
    init_width = len(init_frame[0])
    init_height = len(init_frame)

    gray = cv2.cvtColor(init_frame, cv2.COLOR_BGR2GRAY)
    tags = apriltag_detector.detect(gray)

    if len(tags) < 2:
        print(f"Not enough markers found! At least two needed but I found {len(tags)}.")
        return (slice(0,init_height),slice(0,init_width))

    xmin = init_width
    xmax = 0
    ymin = init_height
    ymax = 0
    for tag in tags:
        for corner in tag['lb-rb-rt-lt']:
            xmin = min(xmin,corner[0])
            xmax = max(xmax,corner[0])
            ymin = min(ymin,corner[1])
            ymax = max(ymax,corner[1])

    return (slice(int(ymin),int(ymax)),slice(int(xmin),int(xmax)))

def circle_tags(markers, frame):
    """
    Put a circle on each marker in view using cv2.circle
    TODO: Everything
    """
    pass

