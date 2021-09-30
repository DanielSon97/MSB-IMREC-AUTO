import numpy as np
from PIL import Image, ImageOps, ImageGrab
import math
import time
import cv2
import sys

np.set_printoptions(threshold=sys.maxsize)

def main():

	count = 0

	for i in range(1,21):
		image = Image.open("canny" + str(i) + ".png")
		x = 0
		while(x <= 525):
			y = 0
			while(y <= 80):
				cropped = image.crop((x, y, x + 75, y + 75))
				save(cropped, "./sections/" + str(count) + ".png")
				count = count + 1
				y = y + 20
			x = x + 40











def save(img, saveName):
	img.save(saveName)

main()