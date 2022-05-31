import cv2

img = cv2.imread('../data/street.png')

cv2.imshow("Street", img)
cv2.waitKey()