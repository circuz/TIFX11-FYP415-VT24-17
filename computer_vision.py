import cv2
import apriltag
import cammands

capture, detector = cammands.initialize_camera(0, "tag36h11")

crop_coords = cammands.get_crop_coords(capture, detector)

key = None
while key != ord("q"):
    _, raw_frame = capture.read()

    if key == ord("r"):
        crop_coords = cammands.get_crop_coords(capture, detector)

    frame = raw_frame[crop_coords]

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    raw_markers = detector.detect(gray)
    if len(raw_markers) > 0:
        print(type(raw_markers))
        print(raw_markers)

    cv2.imshow("", frame)

    key = cv2.waitKey(1)
