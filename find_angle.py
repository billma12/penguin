'''
Description:
	This script detects a cone in an image of a map and finds the angle
	between the the cone lines
General steps:
	1. Detect Cone using cv2.MatchTemplate()
	2. Crop the cone
	3. Filter cropped image (HSV then Canny)
	4. Perform Hough Transform on Cannified image to detect lines
	5. Do some math to find angle between lines
Bugs (as of 1/5/18):
	1. When there is too much 'junk' in the image, it's hard to detect the
	   proper lines (problem in city maps)
	   		- need to manually check proper angles
	2. Sometimes angle is off by 90 degrees (not that big a deal)
	3. Sometimes cone line is too short and doesn't get detected (rare)
TODO (1/5/18):
	1. Find angle of street
'''

from __future__ import division
import cv2
import numpy as np


class MapImage:

    def __init__(self, img_path):
        self.img = cv2.imread(img_path)

    def cropCone(self):
        cone_template = cv2.imread("pics/template/bluedot.png")
        w, h, c = cone_template.shape
        method = 'cv2.TM_CCORR_NORMED'
        res = cv2.matchTemplate(self.img, cone_template, eval(method))
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        x = max_loc
        y = (x[0] + w, x[1] + h)

        crop = self.img[x[1] - 40:y[1] + 40, x[0] - 40:y[0] + 40]

        return crop

    def filterImg(self, img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        edges = cv2.Canny(s, 80, 180, apertureSize=3)

        return s, edges


class Angle(MapImage):

    def __init__(self, img_path):
        MapImage.__init__(self, img_path)
        self.cone = self.cropCone()
        self.s, self.canny = self.filterImg(self.cone)
        self.drawing = self.cone.copy()
        self.angles = []
        self.points = []
        self.mid_angle = 0

    def findAngles(self):
        lines = cv2.HoughLinesP(self.canny, 1, np.pi /
                                180, 45, minLineLength=35, maxLineGap=10)

        for line in lines[0]:
            x1, y1, x2, y2 = line
            angle = np.arctan((y1 - y2) / (x2 - x1)) * 180 / np.pi
            self.points.append(line)
            self.angles.append(angle)
            cv2.line(self.drawing, (x1, y1), (x2, y2), (0, 255, 0), 2)

        return self.drawing

    def drawMidLine(self):
        if len(self.angles) > 1 and self.angles[0] != self.angles[1]:
            self.mid_angle = 90 + ((self.angles[0] + self.angles[1]) / 2)

            x1, y1, x2, y2 = self.points[0]
            x3, y3, x4, y4 = self.points[1]

            mid_x0 = int(((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / (
                (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)))
            mid_y0 = int(((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / (
                (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)))

            cv2.circle(self.drawing, (int(mid_x0),
                       int(mid_y0)), 10, (0, 255, 0))

            mid_a = np.cos(self.mid_angle * np.pi / 180)
            mid_b = np.sin(self.mid_angle * np.pi / 180)

            x5 = int(mid_x0 + 1000 * (-mid_a))
            y5 = int(mid_y0 + 1000 * (mid_b))
            x6 = int(mid_x0 - 1000 * (-mid_a))
            y6 = int(mid_y0 - 1000 * (mid_b))

            cv2.line(self.drawing, (x5, y5), (x6, y6), (0, 0, 255), 2)

        return self.drawing

    def displayPictures(self):
    	print "angles: ", self.angles
    	print "mid angle: ", self.mid_angle
        full = cv2.vconcat([self.cone, cv2.cvtColor(self.s, cv2.COLOR_GRAY2BGR), cv2.cvtColor(
            self.canny, cv2.COLOR_GRAY2BGR), self.drawing])
        cv2.imshow('full', full)
        cv2.waitKey(0)

    def main(self):
		self.findAngles()
		self.drawMidLine()
		self.displayPictures()


def main():
    # img_path = "pics/121317/suburban/" + str(i) + ".png"
    # img_path = "pics/121317/city/lgg4/" + str(i) + ".png"
    # img_path = "pics/121317/city/huawei/" + str(i) + ".png"
    # img_path = "pics/121917/city/huawei/" + str(i) + ".png"
    # img_path = "pics/121917/city/lgg4/" + str(i) + ".png"

    for i in range(1, 30):
        print '------' 'IMG {}' '------'.format(i)
        img_path = "pics/121917/city/lgg4/" + str(i) + ".png"
        Angle(img_path).main()

if __name__ == '__main__':
    main()
