import cv2
#works, dont modify
videoCaptureObject = cv2.VideoCapture("http://192.168.1.36/capture")
videoCaptureObject2 = cv2.VideoCapture("http://192.168.1.40/capture")
result = True
num=5

while(result):
    ret,frame = videoCaptureObject.read()
    ret2, frame2 = videoCaptureObject2.read()

    cv2.imwrite('images/stereoLeft/imageL' + str(num) + '.jpg', frame2)
    cv2.imwrite('images/stereoright/imageR' + str(num) + '.jpg', frame)

    result = False

videoCaptureObject.release()
videoCaptureObject2.release()
cv2.destroyAllWindows()