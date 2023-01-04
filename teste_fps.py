import cv2

cap = cv2.VideoCapture('rtsp://admin:StartID0176@10.50.30.63:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')
print(cap.get(cv2.CAP_PROP_FPS))