import cv2
import numpy as np
from matplotlib import pyplot as plt

img = cv2.imread('cone.jpg', 0)
edges = cv2.Canny(img, 100,200, apertureSize = 3)

lines = cv2.HoughLines(edges,1,np.pi/180,39)
for rho,theta in lines[0]:
    a = np.cos(theta)
    b = np.sin(theta)
    x0 = a*rho
    y0 = b*rho
    x1 = int(x0 + 1000*(-b))
    y1 = int(y0 + 1000*(a))
    x2 = int(x0 - 1000*(-b))
    y2 = int(y0 - 1000*(a))

    cv2.line(img,(x1,y1),(x2,y2),(0,0,255),2)

print(lines) #gives me angles

cv2.imshow('image', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
