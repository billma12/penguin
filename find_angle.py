import cv2
import numpy as np
import matplotlib.pyplot as plt

img2 = cv2.imread("pics/full/suburban/1.png")

#CROP
height, width, channels = img2.shape
print(height)
img = img2[height//2-200:height//2+200,0:1440]

#FILTER
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
h,s,v = cv2.split(hsv)
edges = cv2.Canny(s, 80,180, apertureSize = 3) # TODO: change these values
lines = cv2.HoughLines(edges, 1, np.pi/180, 35)

max_theta = 0
min_theta = 2*np.pi
max_line = (0,0)
min_line = (0,0)


#find min,max angles
for rho,theta in lines[0]:
	if theta > max_theta:
		max_theta = theta
		max_line = (rho, theta)
	if theta < min_theta:
		min_theta = theta
		min_line = (rho, theta)

#print("max line, mine line: ", max_line, min_line)

# MIN_LINE
min_theta = min_line[1]
min_rho = min_line[0]
degree = 180/np.pi

# print(max_line[1]*degree, min_line[1]*degree, theta*degree)
min_a = np.cos(min_theta) 
min_b = np.sin(min_theta) 
min_x0 = min_a*min_rho
min_y0 = min_b*min_rho


x1 = int(min_x0 + 1000*(-min_b))
y1 = int(min_y0 + 1000*(min_a))
x2 = int(min_x0 - 1000*(-min_b))
y2 = int(min_y0 - 1000*(min_a))

final = img.copy()
cv2.line(final,(x1,y1),(x2,y2),(0,0,255),2)

# MAX LINE
max_theta = max_line[1]
max_rho = max_line[0]

max_a = np.cos(max_theta) 
max_b = np.sin(max_theta) 
max_x0 = max_a*max_rho
max_y0 = max_b*max_rho

x3 = int(max_x0 + 1000*(-max_b))
y3 = int(max_y0 + 1000*(max_a))
x4 = int(max_x0 - 1000*(-max_b))
y4 = int(max_y0 - 1000*(max_a))

cv2.line(final,(x3,y3),(x4,y4),(0,0,255),2)

# MIDDLE LINE
print(max_theta*degree, min_theta*degree)
mid_theta = (max_theta + min_theta) / 2
mid_x0 = ((x1*y2-y1*x2)*(x3-x4) - (x1-x2)*(x3*y4-y3*x4))/((x1-x2)*(y3-y4)-(y1-y2)*(x3-x4))
mid_y0 = ((x1*y2-y1*x2)*(y3-y4) - (y1-y2)*(x3*y4-y3*x4))/((x1-x2)*(y3-y4)-(y1-y2)*(x3-x4))

cv2.circle(final,(mid_x0,mid_y0),10,(0,255,0))

mid_a = np.cos(mid_theta) 
mid_b = np.sin(mid_theta) 

x5 = int(mid_x0 + 1000*(-mid_b))
y5 = int(mid_y0 + 1000*(mid_a))
x6 = int(mid_x0 - 1000*(-mid_b))
y6 = int(mid_y0 - 1000*(mid_a))

cv2.line(final,(x5,y5),(x6,y6),(0,0,255),2)

# PRINT PICTURE
small = cv2.resize(img, (480,768))


cv2.putText(final, str(mid_theta*degree), (30,80), cv2.FONT_HERSHEY_SIMPLEX, 1, 255)

'''
cv2.imshow('image', crop)
cv2.waitKey(0)
cv2.destroyAllWindows()
'''

# Display Original, HSV, Canny, Final Images
f, axes = plt.subplots(4, 1, figsize = (8,8))
axes[0].imshow(img)
axes[1].imshow(s, cmap="Greys_r")
axes[2].imshow(edges, cmap="Greys_r")
axes[3].imshow(final)
plt.setp(axes, xticks=[], yticks=[])
plt.tight_layout()
plt.show()