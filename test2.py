import numpy as np
from PIL import Image, ImageOps, ImageGrab
import math
import time
import cv2
import sys

np.set_printoptions(threshold=sys.maxsize)

def main():
	for i in range(21):
		#setting base image
		imageLink = "rune" + str(i) + ".png"
		
		#cropping image
		img = Image.open(imageLink)
		img = np.array(img)

		#converting to hsv
		img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

		#converting to hue
		img = img[:, :, 0]

		# #denoise
		img = cv2.fastNlMeansDenoising(img, 7, 21)

		# #canny edge detection
		img = cv2.Canny(img, 150, 200)
		save(img, "canny" + str(i) + ".png")


def save(img, saveName):
	saveImage = Image.fromarray(img)
	saveImage.save(saveName)

main()