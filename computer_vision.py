import cv2
import apriltag

capture = cv2.VideoCapture(0)
detector = apriltag.apriltag("tag36h11")

_, init_frame = capture.read()
init_width = len(init_frame[0])
width = init_width//2
init_height = len(init_frame)
height = init_height//2
xoffset = width//2
yoffset = height//2
while True:
    _, raw_frame = capture.read()

    frame = raw_frame[yoffset:(yoffset+height),xoffset:(xoffset+width)]

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    raw_markers = detector.detect(gray)
    if len(raw_markers) > 0:
        print(type(raw_markers))
        print(raw_markers)

    cv2.imshow("", frame)
    key = cv2.waitKey(1)

    if key == ord("q"):
        exit()
