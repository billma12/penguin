'''
Description:
    This script detects a cone in an image of a map and finds the angle
    between the the cone lines. Also finds the angle of streets
General steps:
    1. Detect and crop cone
    2. Filter cropped image (HSV then Canny)
    3. Perform Hough Transform on Cannified image to detect lines
    4. Do some math to find angle between lines
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

        return s, canny

    def filterImgStreet(self):
        bw = cv2.cvtColor(self.crop, cv2.COLOR_BGR2GRAY)
        canny = cv2.Canny(bw, 25, 80, apertureSize=3)

        return canny


class Angle(MapImage):

    def __init__(self, img_path):
        MapImage.__init__(self, img_path)
        self.cone = self.cropCone()
        self.s, self.canny_cone = self.filterImgCone()
        self.canny_street = self.filterImgStreet()
        self.drawing = self.cone.copy()
        self.cone_angles = []
        self.cone_points = []
        self.street_angles = []
        self.mid_angle = 0
        self.street_angle = 0

    def findConeAngles(self):
        lines = cv2.HoughLinesP(self.canny_cone, 1, np.pi /
                                180, 35, minLineLength=42, maxLineGap=10)

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
                # if angle > 92 or angle < 88:
                #    if abs(angle) > 2 and abs(angle) < 88:
                self.cone_angles.append([angle, length, line])
                self.cone_points.append(line)
                cv2.line(self.drawing, (x1, y1),
                         (x2, y2), (0, 255, 0), 2)

        self.cone_angles = sorted(self.cone_angles, key=lambda x: x[1])[::-1]

        angles = []
        for i in range(0, len(self.cone_angles)):
            angles.append(self.cone_angles[i][0])

        if len(self.cone_angles) > 1:
            an = self.cone_angles[0][0]
            for i, ang in enumerate(self.cone_angles):
                if abs(ang[0] - an) > 2:
                    break

            x1, y1, x2, y2 = self.cone_angles[i][2]
            x3, y3, x4, y4 = self.cone_angles[i - 1][2]

            cv2.line(self.drawing, (x1, y1),
                     (x2, y2), (0, 255, 255), 2)
            cv2.line(self.drawing, (x3, y3),
                     (x4, y4), (0, 255, 255), 2)

            self.cone_angles = [self.cone_angles[i], self.cone_angles[i - 1]]
            print 'cone angles: {} {}'.format(self.cone_angles[0][0], self.cone_angles[1][0])

        print 'other possible cone angles: {}'.format(angles)

    def findStreetAngle(self):
        lines = cv2.HoughLinesP(self.canny_street, 1, np.pi /
                                180, 25, minLineLength=75, maxLineGap=8)

        for line in lines[0]:
            x1, y1, x2, y2 = line
            if x2 == x1:
                angle = 90
            else:
                angle = np.arctan((y1 - y2) / (x2 - x1)) * 180 / np.pi

            # assume street b/t 50 and 120 degrees
            if abs(angle) > 50 and abs(angle) < 120:
                dist_from_center = np.sqrt(
                    (x1 - self.crop_center[0])**2 + (y1 - self.crop_center[1])**2)
                length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                if angle < 0:
                    self.street_angles.append([angle + 180, dist_from_center, length, line])
                else:
                    self.street_angles.append([angle, dist_from_center, length, line])

        self.street_angles = sorted(self.street_angles, key=lambda x: x[2])[::-1]

        x1, y1, x2, y2 = self.street_angles[0][3]
        cv2.line(self.drawing, (x1, y1), (x2, y2), (255, 0, 255), 2)
        self.street_angle = self.street_angles[0][0]
        print 'street angle: {}'.format(self.street_angle)

        i = 1
        angles = []
        while i < len(self.street_angles):
            if i == 4:
                break
            x1, y1, x2, y2 = self.street_angles[i][3]
            angles.append(self.street_angles[i][0])
            cv2.line(self.drawing, (x1, y1), (x2, y2), (255, 0, 0), 2)
            i = i + 1

        print 'other possible street angles: {}'.format(angles)

    def drawMidLine(self):
        if len(self.cone_angles) > 1:
            self.mid_angle = 90 + \
                ((self.cone_angles[0][0] + self.cone_angles[1][0]) / 2)

            # sometimes angle is off by 90 degrees
            if self.cone_angles[0][0] * self.cone_angles[1][0] > 0:
                self.mid_angle = self.mid_angle + 90
                if self.mid_angle > 180:
                    self.mid_angle = self.mid_angle - 180

            x1, y1, x2, y2 = self.cone_angles[0][2]
            x3, y3, x4, y4 = self.cone_angles[1][2]

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
        print 'angle off: {}'.format(self.street_angle - self.mid_angle)
        full = cv2.hconcat((cv2.cvtColor(self.canny_cone, cv2.COLOR_GRAY2BGR), self.drawing))
        cv2.imshow('full', full)
        cv2.waitKey(0)

    def demo(self):
        full = cv2.hconcat((self.cone, cv2.cvtColor(self.s, cv2.COLOR_GRAY2BGR), cv2.cvtColor(self.canny_cone, cv2.COLOR_GRAY2BGR), self.drawing))
        cv2.imshow('full', full)
        cv2.waitKey(0)

    def main(self):
        self.findStreetAngle()
        self.findConeAngles()
        self.drawMidLine()
        self.displayResults()
        # self.demo()


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
