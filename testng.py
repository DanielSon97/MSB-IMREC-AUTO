import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from PIL import Image, ImageOps, ImageGrab
import math
import time
import cv2
import sys
import tensorflow.keras
from keras.models import load_model
from PIL import Image, ImageOps
import numpy as np


np.set_printoptions(threshold=sys.maxsize)

def main():
	count = 6
	arrowsModel = tensorflow.keras.models.load_model("./models/arrows.h5", compile = False)
	directionModel = tensorflow.keras.models.load_model("./models/direction.h5", compile = False)
	#model = load_model("./models/arrows.h5")
	
	size = (224, 224)
	count = 0
	while(True):
		input("Press Enter")

		# #cropping image
		# img = ImageGrab.grab()
		# img = img.crop((670, 155, 1270, 300))
		# img.save("./imgs/base.png")

		img = Image.open("./imgs/base.png")
		img = np.array(img)

		#converting to hsv
		img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

		#converting to hue
		img = img[:, :, 0]

		# #denoise
		img = cv2.fastNlMeansDenoising(img, 7, 21)

		# #canny edge detection
		img = cv2.Canny(img, 150, 200)

		img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

		img = Image.fromarray(img)
		img.save("./imgs/canny.png")

		
		x = 0
		arrows = []
		while(x <= 525):
			y = 0
			while(y <= 80):
				data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
				cropped = img.crop((x, y, x + 75, y + 75))
				croppedImg = ImageOps.fit(cropped, size, Image.ANTIALIAS)
				image_array = np.asarray(croppedImg)
				normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
				cropped.save("./sections/section" + str(count) + ".png")
				data[0] = normalized_image_array
				prediction = arrowsModel.predict(data)
				if(prediction[0][0] > 0.80):
					cropped.save("./arrows/arrow" + str(count) + ".png")
					arrows.append(cv2.cvtColor(np.array(cropped), cv2.COLOR_RGB2GRAY))
					count = count + 1
					x = x + 40
					break

				
				y = y + 20
			x = x + 40

		print(len(arrows))

		for i in range(len(arrows)):
			image = arrows[i]
			contours, _ = cv2.findContours(image, cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
			print(len(contours))

		# if(len(arrows) == 4):
		# 	print("4 arrows found")
		# 	dataSolve = np.ndarray(shape=(4, 224, 224, 3), dtype=np.float32)
		# 	for i in range(len(arrows)):
		# 		dataSolve[i] = arrows[i]
				
		# 	prediction = directionModel.predict(dataSolve)
		# 	order = []

		# 	for i in range(len(arrows)):
		# 		maxVal = 0
		# 		maxIT = -1
		# 		for j in range(4):
		# 			if(maxVal < prediction[i][j]):
		# 				maxVal = prediction[i][j]
		# 				maxIT = j
		# 		if (maxIT == 0):
		# 			order.append("left")
		# 		elif (maxIT == 1):
		# 			order.append("right")
		# 		elif (maxIT == 2):
		# 			order.append("down")
		# 		elif (maxIT == 3):
		# 			order.append("up")

		# 	print(order)
		
		


		



main()