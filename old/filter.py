import cv2
import numpy as np
import matplotlib.pyplot as plt

def draw_line(img, edges):
	lines = cv2.HoughLines(edges, 1, np.pi/180, 40)
	final = img.copy()

	max_theta = 0
	min_theta = 2*np.pi
	max_line = (0,0)
	min_line = (0,0)
	degree = 180/np.pi

	# find min,max angles
	for rho,theta in lines[0]:
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

def filter(pic):
	path = "pics/121917/city/" + str(pic) + ".png"
	#path = "pics/full/suburban/" + str(pic) + ".png"
	img = cv2.imread(path)
	h,w,c = img.shape
	crop = img[h//2-200:h//2+200,w//2-200:w//2+200]
	

	hsv = cv2.cvtColor(crop, cv2.COLOR_RGB2HSV)
	h,s,v = cv2.split(hsv)
	edges = cv2.Canny(s, 30, 100, apertureSize = 3) # TODO: change these values
	final = draw_line(crop, edges)
	cv2.putText(crop, "ORIGINAL", (30,80), cv2.FONT_HERSHEY_SIMPLEX, 1.5, 255)
	cv2.putText(s, "HSV FILTER", (30,80), cv2.FONT_HERSHEY_SIMPLEX, 1.5, 255)
	cv2.putText(edges, "CANNY EDGE", (30,80), cv2.FONT_HERSHEY_SIMPLEX, 1.5, 255)
	full = cv2.vconcat([crop, cv2.cvtColor(s, cv2.COLOR_GRAY2BGR), cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR), final])
	shrink = cv2.resize(full, (0,0), fx=0.5, fy=0.5)
	cv2.imshow('img', shrink)
	cv2.waitKey(0)

for num in range(1,21):
	filter(num)