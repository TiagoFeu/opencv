from enum import Enum
import numpy as np
import cv2
from geometry import Box, Point

class LightState(Enum):
    RED = 0
    YELLOW = 1
    GREEN = 2

class TrafficLight:
    def __init__(self, red: Box, yellow: Box, green: Box) -> None:
        self.red = red
        self.yellow = yellow
        self.green = green
    
    def detect_state(self, image: np.array) -> LightState:
        img_h, img_w, _ = image.shape
        best_color = None
        best_v = 0

        for color, box in zip([LightState.RED, LightState.YELLOW, LightState.GREEN], [self.red, self.yellow, self.green]):
            print(img_w)
            print(img_h)
            x1 = int(box.pt1.x*img_w)
            x2 = int(box.pt2.x*img_w)
            y1 = int(box.pt1.y*img_h)
            y2 = int(box.pt2.y*img_h)
            print(x1, x2, y1, y2)
            region = image[y1:y2, x1:x2]
            hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
            mean, _ = cv2.meanStdDev(hsv)

            if mean[2] > best_v:
                best_color = color
                best_v = mean[2]
        
        return best_color

if __name__ == '__main__':
    img = cv2.imread('yellow.png', cv2.IMREAD_COLOR)
    #tl = TrafficLight(Box(Point(157, 115), Point(173, 132)), Box(Point(154, 152), Point(171, 167)), Box(Point(153, 189), Point(168, 203)))
    #tl = TrafficLight(Box(Point(309, 125), Point(324, 138)), Box(Point(310, 150), Point(324, 164)), Box(Point(311, 177), Point(324, 190)))
    #tl = TrafficLight(Box(Point(334, 52), Point(341, 58)), Box(Point(334, 58), Point(340, 64)), Box(Point(334, 66), Point(340, 72)))
    # tl = TrafficLight(Box(Point(621, 394), Point(688, 458)), Box(Point(678, 556), Point(742, 620)), Box(Point(666, 654), Point(743, 727)))
    tl = TrafficLight(Box(Point(1466/1920, 372/1080), Point(1494/1920, 405/1080)), Box(Point(1466/1920, 419/1080), Point(1494/1920, 453/1080)), Box(Point(1464/1920, 468/1080), Point(1493/1920, 498/1080)))
    print(tl.detect_state(img))
