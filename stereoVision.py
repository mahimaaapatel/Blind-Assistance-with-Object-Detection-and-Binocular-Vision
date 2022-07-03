import sys
import cv2
import numpy as np
import time
import imutils
from matplotlib import pyplot as plt
import urllib.request
# Function for stereo vision and depth estimation
import triangulation as tri
import calibration
from detect_left import run as left
from detect_right import run as right
import httplib2, json
import time
http = httplib2.Http()

# Open both cameras
cap_right = cv2.VideoCapture("http://192.168.43.159/capture")
cap_left = cv2.VideoCapture("http://192.168.43.203/capture")

# Stereo vision setup parameters
frame_rate = 30  # Camera frame rate (maximum at 120 fps)
B = 4  # Distance between the cameras [cm]
f = 10  # Camera lenses focal length [mm]
alpha = 60  # Camera field of view in the horizontal plane [degrees]
true=True

# Main program loop with face detector and depth estimation using stereo vision
left_url = "http://192.168.43.203/capture"
right_url = "http://192.168.43.159/capture"
print("starting now")
while True:
        img_resp_left = urllib.request.urlopen(left_url)
        img_resp_right = urllib.request.urlopen(right_url)
        print("opening yolov5")
        imgnp_left = np.array(bytearray(img_resp_left.read()), dtype=np.uint8)
        imgnp_right = np.array(bytearray(img_resp_right.read()), dtype=np.uint8)
        frame_left = cv2.imdecode(imgnp_left, -1)
        frame_right = cv2.imdecode(imgnp_right, -1)


        ################## CALIBRATION #########################################################

        # frame_right, frame_left = calibration.undistortRectify(frame_right, frame_left)
        # cv2.imwrite("NewPictureee.jpg", frame_right)
        ########################################################################################

        if True:

            start = time.time()
            cv2.imwrite("left.jpg", frame_left)
            cv2.imwrite("right.jpg", frame_right)
            classes_left, centroids_left = left(source = "left.jpg", weights = "yolov5s.pt")
            classes_right, centroids_right = right(source = "right.jpg", weights = "yolov5s.pt")
            print("Centroids_left",classes_left, centroids_left)
            print("Centroids right", classes_right, centroids_right)

            center_right = 0
            center_left = 0


            # If no ball can be caught in one camera show text "TRACKING LOST"
            if not centroids_right or not centroids_left:
                cv2.putText(frame_right, "TRACKING LOST", (75, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(frame_left, "TRACKING LOST", (75, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            else:
                # Function to calculate depth of object. Outputs vector of all depths in case of several balls.
                # All formulas used to find depth is in video presentaion
                for i in range (0, len(centroids_left)):
                    try:
                        cv2.rectangle(frame_left, (int(centroids_left[i][3][0]), int(centroids_left[i][3][1])),
                                      (int(centroids_left[i][3][2]), int(centroids_left[i][3][3])), (255, 0, 0), 1)
                        cv2.rectangle(frame_right, (int(centroids_right[i][3][0]), int(centroids_right[i][3][1])),
                                      (int(centroids_right[i][3][2]), int(centroids_right[i][3][3])), (255, 0, 0), 1)
                    except:
                        pass
                    try:
                        print("classes", centroids_right[i][2], centroids_left[i][2])
                        if centroids_right[i][2] == centroids_left[i][2]:
                            try:
                                depth = tri.find_depth(centroids_left[i], centroids_right[i], frame_right, frame_left, B, f, alpha)
                                cv2.rectangle(frame_left, (int(centroids_left[i][3][0]), int(centroids_left[i][3][1])),
                                              (int(centroids_left[i][3][2]), int(centroids_left[i][3][3])), (255, 0, 0),
                                              1)
                                cv2.rectangle(frame_right,
                                              (int(centroids_right[i][3][0]), int(centroids_right[i][3][1])),
                                              (int(centroids_right[i][3][2]), int(centroids_right[i][3][3])),
                                              (255, 0, 0), 1)
                                cv2.putText(frame_right, "Distance: " + str(round(depth, 1)),
                                            (int(centroids_left[i][3][0]), int(centroids_left[i][3][1]) - 10),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.3,
                                            (0, 255, 0), 3)
                                cv2.putText(frame_left, "Distance: " + str(round(depth, 1)), (50, 50),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.3,
                                            (0, 255, 0), 3)
                                # Multiply computer value with 205.8 to get real-life depth in [cm]. The factor was found manually.
                                print("Depth: ", str(round(depth, 1)))
                                if depth>0 and depth<70:
                                    url = "http://192.168.43.19/jblink"
                                    headers = {"Content-type": "application/json; charset=UTF-8"}
                                    data = {"times":"4", "play":"1000", "pause":"0"}
                                    response, content = http.request(url, "POST", headers=headers, body=json.dumps(data))
                                elif depth>70 and depth<200:
                                    url = "http://192.168.43.19/jblink"
                                    headers = {"Content-type": "application/json; charset=UTF-8"}
                                    data = {"times":"3", "play":"700", "pause":"500"}
                                    response, content = http.request(url, "POST", headers=headers, body=json.dumps(data))
                                elif depth>200 and depth<500:
                                    url = "http://192.168.43.19/jblink"
                                    headers = {"Content-type": "application/json; charset=UTF-8"}
                                    data = {"times":"3", "play":"200", "pause":"1000"}
                                    response, content = http.request(url, "POST", headers=headers, body=json.dumps(data))
                            except:
                                pass

                    except:
                        continue
            cv2.imshow('Left Cam', frame_left)
            cv2.imshow('Right Cam', frame_right)
            end = time.time()
            totalTime = end - start

            fps = 1 / totalTime
            # print("FPS: ", fps)

            cv2.putText(frame_right, f'FPS: {int(fps)}', (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
            cv2.putText(frame_left, f'FPS: {int(fps)}', (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)

            # Hit "q" to close the window
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

# Release and destroy all windows before termination
cap_right.release()
cap_left.release()

cv2.waitKey(5000)
cv2.destroyAllWindows()
