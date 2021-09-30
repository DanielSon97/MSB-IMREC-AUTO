import numpy as np
from PIL import Image, ImageOps, ImageGrab
import math
import time
import cv2
import sys

np.set_printoptions(threshold=sys.maxsize)

def main():
	count = 6
	
	while(True):
		input("Press Enter")	
		#cropping image
		img = ImageGrab.grab()
		img = img.crop((670, 155, 1270, 300))
		img.save("rune" + str(count) + ".png")
		count = count + 1

main()