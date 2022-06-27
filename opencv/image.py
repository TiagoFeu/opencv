import cv2

img = cv2.imread('../data/street.png')

cv2.imwrite('../data/street_mod.png', img)