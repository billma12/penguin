import cv2
import numpy as np

def main():
    path = "pics/full/suburban/1.png"
    #path = "/Users/work/Desktop/1.jpg"
    image = cv2.imread(path)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # define the list of boundaries
    boundaries = [
        ([30, 180, 50], [255, 255, 180]), # red
        ([35, 180, 55], [255, 250, 195]), # blue
        ([40, 180, 60], [255, 255, 200]), # yellow
        ([45, 180, 65], [225, 255, 195]) # gray
    ]

    # loop over the boundaries
    for (lower, upper) in boundaries:
        # create NumPy arrays from the boundaries
        lower = np.array(lower, dtype = "uint8")
        upper = np.array(upper, dtype = "uint8")
     
        # find the colors within the specified boundaries and apply
        # the mask
        mask = cv2.inRange(image, lower, upper)
        output = cv2.bitwise_and(image, image, mask = mask)
     
        # show the images
        img = np.hstack([image, output])
        shrink = cv2.resize(img, (0,0), fx=0.3, fy=0.3)
        cv2.imshow("images", shrink)
        cv2.waitKey(0)

main()