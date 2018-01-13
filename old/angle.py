# Description:
# This script detects a cone in an image of a map and finds the angle between the the cone lines

# General steps: 
# 1. Detect Cone using cv2.MatchTemplate()
# 2. Crop the cone
# 3. Filter cropped image (HSV then Canny)
# 4. Perform Hough Transform on Cannified image to detect lines
# 5. Do some math to find angle between lines

# Bugs (as of 1/5/18): 
# 1. When there is too much 'junk' in the image, it's hard to detect the proper lines (problem in city maps)
#       - need to manually check proper angles
# 2. Sometimes angle is off by 90 degrees (not that big a deal)
# 3. Sometimes cone line is too short and doesn't get detected (rare)

# TODO (1/5/18):
# 1. Find angle of street

from __future__ import division
import cv2
import numpy as np

def drawMidLine(img, angle, points):
    if len(angle) > 1 and angle[0] != angle[1]:
        mid_theta = 90 + ((angle[0] + angle[1]) / 2)

        x1, y1, x2, y2 = points[0]
        x3, y3, x4, y4 = points[1]

        mid_x0 = int(((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / (
                (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)))
        mid_y0 = int(((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / (
                (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)))

        cv2.circle(img, (int(mid_x0), int(mid_y0)), 10, (0, 255, 0))

        print "mid angle: ", mid_theta
        mid_a = np.cos(mid_theta * np.pi/180)
        mid_b = np.sin(mid_theta * np.pi/180) 

        x5 = int(mid_x0 + 1000 * (-mid_a))
        y5 = int(mid_y0 + 1000 * (mid_b))
        x6 = int(mid_x0 - 1000 * (-mid_a))
        y6 = int(mid_y0 - 1000 * (mid_b))

        cv2.line(img, (x5, y5), (x6, y6), (0, 0, 255), 2)

    return img


def cropCone(img, template):
    w, h, c = template.shape
    method = 'cv2.TM_CCORR_NORMED'
    res = cv2.matchTemplate(img, template, eval(method))
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    x = max_loc
    y = (x[0] + w, x[1] + h)

    crop = img[x[1] - 40:y[1] + 40, x[0] - 40:y[0] + 40]

    return crop

def filterImg(img):

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    h, s, v = cv2.split(hsv)
    edges = cv2.Canny(s, 80, 180, apertureSize=3)  

    return s, edges

def find_angle(crop, edges):
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 45, minLineLength=35, maxLineGap=10) # TODO: change these values

    img2 = crop.copy()
    angles = []
    points = []
    slopes = []

    for line in lines[0]:
        x1, y1, x2, y2 = line
        slope = (y1-y2)/(x2-x1)
        angle = np.arctan((y1-y2)/(x2-x1))*180/np.pi
        slopes.append(slope)
        angles.append(angle)
        points.append(line)
        cv2.line(img2,(x1,y1),(x2,y2),(0,255,0),2)

    print "angles found: ", angles
    return points, angles, img2

def main(i):
    # path = "pics/121317/suburban/" + str(i) + ".png"
    # path = "pics/121317/city/lgg4/" + str(i) + ".png"
    # path = "pics/121317/city/huawei/" + str(i) + ".png"
    # path = "pics/121917/city/huawei/" + str(i) + ".png"
    path = "pics/121917/city/lgg4/" + str(i) + ".png"
    print "image: ", i

    img = cv2.imread(path)
    cone_template = cv2.imread("pics/template/bluedot.png")

    crop = cropCone(img, cone_template)
    s, edges = filterImg(crop)
    points, angle, img_with_lines_detected = find_angle(crop, edges)

    drawing = drawMidLine(img_with_lines_detected, angle, points)

    # Display images
    full = cv2.vconcat([crop, cv2.cvtColor(s, cv2.COLOR_GRAY2BGR), cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR), drawing])
    cv2.imshow('full', full)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    for i in range(1,38):
        main(i)
        print '__________________________'

