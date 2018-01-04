import cv2
import numpy as np
from matplotlib import pyplot as plt

def draw_line(img, edges):
	lines = cv2.HoughLines(edges, 1, np.pi/180, 30)
	final = img.copy()

	max_theta = 0
	min_theta = 2*np.pi
	max_line = (0,0)
	min_line = (0,0)
	degree = 180/np.pi

	# find min,max angles
	for rho,theta in lines[0]:
		print("degree is: ", theta*degree)
		if theta > max_theta:
			max_theta = theta
			max_line = (rho, theta)
		if theta < min_theta:
			min_theta = theta
			min_line = (rho, theta)

	# draw min line
	min_theta = min_line[1]
	min_rho = min_line[0]

	min_a = np.cos(min_theta) 
	min_b = np.sin(min_theta) 
	min_x0 = min_a*min_rho
	min_y0 = min_b*min_rho


	x1 = int(min_x0 + 1000*(-min_b))
	y1 = int(min_y0 + 1000*(min_a))
	x2 = int(min_x0 - 1000*(-min_b))
	y2 = int(min_y0 - 1000*(min_a))

	cv2.line(final,(x1,y1),(x2,y2),(0,0,255),2)

	# draw max_line
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

	# draw middle_line
	mid_theta = ((max_theta-np.pi) + min_theta) / 2
	print("max degree: {} min degree: {} mid degree: {}".format(max_theta*degree, min_theta*degree, mid_theta*degree))
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

	# print angle on img
	cv2.putText(final, "{0:.4f}".format(mid_theta*degree), (30,80), cv2.FONT_HERSHEY_SIMPLEX, 1.5, 255)
	
	return final


def search(i):
	# path = "pics/full/suburban/" + str(i) + ".png"
	path = "pics/full/city/" + str(i) + ".png"
	# path = "pics/121917/city/" + str(i) + ".png"
	color_img = cv2.imread(path)
	img = cv2.imread(path)
	img2 = img.copy()
	template = cv2.imread("pics/full/suburban/cone3.png")
	w, h, c = template.shape

	# All the 6 methods for comparison in a list
	methods = ['cv2.TM_CCORR_NORMED']

	for meth in methods:
	    img = img2.copy()
	    method = eval(meth)

	    # Apply template Matching
	    res = cv2.matchTemplate(img,template,method)
	    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

	    # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
	    if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
	        top_left = min_loc
	    else:
	        top_left = max_loc
	    bottom_right = (top_left[0] + w, top_left[1] + h)

	    cv2.rectangle(img,top_left, bottom_right, 255, 2)
	    cv2.imshow("img", cv2.resize(img, (0,0), fx=0.5, fy=0.5))
	    cv2.waitKey(0)

	print("img: ", i, top_left, bottom_right)

	small = cv2.resize(img, (0,0), fx=0.5, fy=0.5)

	crop = color_img[top_left[1]-15:bottom_right[1]+15,top_left[0]-15:bottom_right[0]+15]
	

	hsv = cv2.cvtColor(crop, cv2.COLOR_RGB2HSV)
	h,s,v = cv2.split(hsv)
	edges = cv2.Canny(s, 80, 180, apertureSize = 3) # TODO: change these values

	# cv2.imshow('bluedot_detection', edges)
	# cv2.waitKey(0)
	
	'''
	final = draw_line(crop, edges)

	full = cv2.vconcat([crop, cv2.cvtColor(s, cv2.COLOR_GRAY2BGR), cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR), final])
	cv2.imshow('bluedot_detection', full)
	cv2.waitKey(0)
	'''

for i in range(1,33):
	search(i)