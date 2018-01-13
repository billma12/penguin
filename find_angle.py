'''
Description:
	This script detects a cone in an image of a map and finds the angle
	between the the cone lines. Also finds the angle of streets
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
	2. Sometimes angle is off by 90 degrees (can be fixed)
'''

from __future__ import division
import cv2
import numpy as np
import os


class MapImage:

    def __init__(self, img_path):
        self.img = cv2.imread(img_path)
        self.crop = None
        self.crop_center = (0, 0)

    def cropCone(self):
        cone_template = cv2.imread("pics/template/bluedot.png")
        res = cv2.matchTemplate(self.img, cone_template, eval('cv2.TM_CCORR_NORMED'))
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        cone_center = (max_loc[0] + 35, max_loc[1] + 40)
        self.crop = self.img[cone_center[1] - 250:cone_center[1] +
                             250, cone_center[0] - 225:cone_center[0] + 225]
        w, h, c = self.crop.shape
        self.crop_center = (h // 2, w // 2)

        return self.crop

    def filterImgCone(self):
        hsv = cv2.cvtColor(self.crop, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        canny = cv2.Canny(s, 80, 180, apertureSize=3)

        return canny

    def filterImgStreet(self):
        bw = cv2.cvtColor(self.crop, cv2.COLOR_BGR2GRAY)
        canny = cv2.Canny(bw, 25, 80, apertureSize=3)

        return canny


class Angle(MapImage):

    def __init__(self, img_path):
        MapImage.__init__(self, img_path)
        self.cone = self.cropCone()
        self.canny_cone = self.filterImgCone()
        self.canny_street = self.filterImgStreet()
        self.drawing = self.cone.copy()
        self.cone_angles = []
        self.cone_points = []
        self.street_angles = []
        self.mid_angle = 0
        self.street_angle = 0

    def findConeAngles(self):
        lines = cv2.HoughLinesP(self.canny_cone, 1, np.pi /
                                180, 25, minLineLength=40, maxLineGap=8)

        for line in lines[0]:
            x1, y1, x2, y2 = line
            if x2 == x1:
                angle = 0
            else:
                angle = np.arctan((y1 - y2) / (x2 - x1)) * 180 / np.pi
            mx = (x1 + x2) // 2
            my = (y1 + y2) // 2
            dist_from_center = np.sqrt(
                (mx - self.crop_center[0])**2 + (my - self.crop_center[1])**2)
            length = np.sqrt(
                (x2 - x1)**2 + (y2 - y1)**2)
            if dist_from_center < 90:
                if angle > 92 or angle < 88:
                    if abs(angle) > 2 and abs(angle) < 88:
                        self.cone_angles.append(angle)
                        self.cone_points.append(line)
                        cv2.line(self.drawing, (x1, y1),
                                 (x2, y2), (0, 255, 0), 2)

        if len(self.cone_angles) > 1:
            print 'cone angles: {}, {}'.format(self.cone_angles[0],self.cone_angles[1])
        print 'other possible cone angles: {}'.format(self.cone_angles)

    def findStreetAngle(self):
        lines = cv2.HoughLinesP(self.canny_street, 1, np.pi /
                                180, 20, minLineLength=90, maxLineGap=8)

        for line in lines[0]:
            x1, y1, x2, y2 = line
            if x2 == x1:
                angle = 90
            else:
                angle = np.arctan((y1 - y2) / (x2 - x1)) * 180 / np.pi
            
            print angle
            if abs(angle) > 70 and abs(angle) < 120:
                cv2.line(self.drawing, (x1, y1), (x2, y2), (255, 0, 0), 2)       
        
        '''    
        for line in lines[0]:
            x1, y1, x2, y2 = line
            if x2 == x1:
                angle = 0
            else:
                angle = np.arctan((y1 - y2) / (x2 - x1)) * 180 / np.pi

            if angle < 0:
                angle = angle + 180

            # assume streets are between 70 and 120 degrees
            if angle > 70 and angle < 120:
                # angles_temp.append((angle, [x1, y1, x2, y2]))
                cv2.line(self.drawing, (x1, y1), (x2, y2), (255, 0, 0), 2)
        '''
        # cv2.imshow('self.drawing', self.drawing)
        # cv2.waitKey(0)
        '''
        angles_temp = []
        for line in lines[0]:
            x1, y1, x2, y2 = line
            if x2 == x1:
                angle = 0
            else:
                angle = np.arctan((y1 - y2) / (x2 - x1)) * 180 / np.pi

            if angle < 0:
                angle = angle + 180

            # assume streets are between 70 and 120 degrees
            if angle < 120 and angle > 70:
                angles_temp.append((angle, [x1, y1, x2, y2]))

        # only display streets in the middle
        angles_temp = sorted(angles_temp, key=lambda x: x[1][0])

        half = len(angles_temp) // 2
        _max = 0

        if len(angles_temp) > 8:
            start = half
            end = half + 4
        else:
            start = 0
            end = len(angles_temp)

        for i in range(start, end):
            x1, y1, x2, y2 = angles_temp[i][1]
            dist = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            self.street_angles.append(angles_temp[i][0])
            cv2.line(self.drawing, (x1, y1), (x2, y2), (255, 0, 0), 2)

            if dist > _max:
                self.street_angle = angles_temp[i][0]
                _max = dist
                x3, y3, x4, y4 = x1, y1, x2, y2

        # draw the street angle (based on longest line)
        cv2.line(self.drawing, (x3, y3), (x4, y4), (255, 255, 0), 2)

        print 'street angle: ', self.street_angle
        print 'other possible street angles: {}'.format(self.street_angles)
        '''

    def drawMidLine(self):
        if len(self.cone_angles) > 1:
            self.mid_angle = 90 + \
                ((self.cone_angles[0] + self.cone_angles[1]) / 2)

            # sometimes angle is off by 90 degrees
            if self.cone_angles[0] * self.cone_angles[1] > 0:
                self.mid_angle = self.mid_angle + 90
                if self.mid_angle > 180:
                    self.mid_angle = self.mid_angle - 180

            x1, y1, x2, y2 = self.cone_points[0]
            x3, y3, x4, y4 = self.cone_points[1]

            # find intersection
            mid_x0 = int(((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / (
                (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)))
            mid_y0 = int(((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / (
                (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)))

            mid_a = np.cos(self.mid_angle * np.pi / 180)
            mid_b = np.sin(self.mid_angle * np.pi / 180)

            # draw middle line
            x5 = int(mid_x0 + 1000 * (-mid_a))
            y5 = int(mid_y0 + 1000 * (mid_b))
            x6 = int(mid_x0 - 1000 * (-mid_a))
            y6 = int(mid_y0 - 1000 * (mid_b))

            cv2.circle(self.drawing, (mid_x0, mid_y0), 10, (0, 255, 0))
            cv2.line(self.drawing, (x5, y5), (x6, y6), (0, 0, 255), 2)

        print 'mid angle: {}'.format(self.mid_angle)
        return self.drawing

    def displayResults(self):
        print 'angle off: {}'.format(self.street_angle-self.mid_angle)
        cv2.imshow('full', self.drawing)
        cv2.waitKey(0)

    def main(self):
        self.findStreetAngle()
        self.findConeAngles()
        self.drawMidLine()
        self.displayResults()


def main():
    img_path = "pics/121317/suburban/"
    # img_path = "pics/121317/city/lgg4/"
    # img_path = "pics/121317/city/huawei/"
    # img_path = "pics/121917/city/huawei/"
    # img_path = "pics/121917/city/lgg4/"

    for p, d, f in os.walk(img_path):
        for img in f:
            if img[-4:] == '.png':
                print '----{}----'.format(img)
                Angle(p + img).main()

if __name__ == '__main__':
    main()
