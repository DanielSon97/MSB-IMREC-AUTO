import sys
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import random
import time
import pyautogui
import keyboard
import win32api, win32con
from configparser import ConfigParser
import tensorflow.keras
from PIL import Image, ImageOps, ImageGrab
import numpy as np
import cv2
pyautogui.FAILSAFE = False

#creating RouteData class
class RouteData:
	def __init__(self):
		self.routeNum = 0
		self.instructions = []

		return

	class Instruction:
		def __init__(self, leftX, rightX, Y):
			self.leftX = leftX
			self.rightX = rightX
			self.Y = Y
			self.sequence = []

			return

	#reading route data from file
	def readRouteFromFile(self, charName, mapName):
		#opening route data file
		configure = ConfigParser()
		configure.read("./route data/" + charName + "_" + mapName + ".ini")

		#reading general section
		self.charName = configure.get("general", "charName")
		self.mapName = configure.get("general", "mapName")

		#reading routes section
		lines = list(configure.items("routes"))
		self.routeNum = len(lines)
		for i in range(len(lines)):
			dataList = lines[i][1].split(', ')
			self.instructions.append(self.Instruction(int(dataList[0]), int(dataList[1]), int(dataList[2])))
			sequenceList = dataList[3].split("/")
			for j in range(len(sequenceList)):
				self.instructions[i].sequence.append(sequenceList[j])
		return

#creating MapData class
class MapData:
	def __init__(self):
		self.minX = 9
		self.minY = 61
		self.platformsNum = 0
		self.platforms = []
		self.ropesNum = 0
		self.ropes = []
		self.portalsNum = 0
		self.portals = []

	#creating Platform class
	class Platform:
		def __init__(self, leftX, rightX, Y):
			self.leftX = leftX
			self.rightX = rightX
			self.Y = Y

			return

	#creating Rope class
	class Rope:
		def __init__(self, X, bottomY, topY):
			self.X = X
			self.bottomY = bottomY
			self.topY = topY

			return

	#creating Portal class
	class Portal:
		def __init__(self, X1, Y1, X2, Y2):
			self.X1 = X1
			self.Y1 = Y1
			self.X2 = X2
			self.Y2 = Y2

			return

	#reading map data from file
	def readMapFromFile(self, mapName):
		#opening map file
		configure = ConfigParser()
		configure.read("./map data/" + mapName + ".ini")

		#reading general section
		self.mapName = configure.get("general", "mapName")
		self.minX = configure.getint("general", "minX")
		self.maxX = configure.getint("general", "maxX")
		self.minY = configure.getint("general", "minY")
		self.maxY = configure.getint("general", "maxY")
		self.width = configure.getint("general", "width")
		self.height = configure.getint("general", "height")
		self.cem_maxX = configure.getint("general", "cemMaxX")
		self.cem_maxY = configure.getint("general", "cemMaxY")
		self.cem_width = configure.getint("general", "cemWidth")
		self.cem_height = configure.getint("general", "cemHeight")
		self.map_coordX = configure.getint("general", "mapCoordX")
		self.map_coordY = configure.getint("general", "mapCoordY")

		#reading platforms section
		lines = list(configure.items("platforms"))
		self.platformsNum = len(lines)
		for i in range(len(lines)):
			dataList = lines[i][1].split(', ')
			self.platforms.append(self.Platform(int(dataList[0]), int(dataList[1]), int(dataList[2])))

		#reading ropes section
		lines = list(configure.items("ropes"))
		self.ropesNum = len(lines)
		for i in range(len(lines)):
			dataList = lines[i][1].split(', ')
			self.ropes.append(self.Rope(int(dataList[0]), int(dataList[1]), int(dataList[2])))
			
		#reading ropes section
		lines = list(configure.items("portals"))
		self.portalsNum = len(lines)
		for i in range(len(lines)):
			dataList = lines[i][1].split(', ')
			self.portals.append(self.Portal(int(dataList[0]), int(dataList[1]), int(dataList[2]), int(dataList[3])))

		return

#creating CharacterData class
class CharacterData:
	def __init__(self):
		self.skillsNum = 0
		self.buffsNum = 0
		self.resetsNum = 0
		self.presetsNum = 0

		self.skills = {}
		self.buffs = []
		self.resets = []
		self.presets = {}

		self.buffTimers = []
		self.presetTimers = {}

		self.potions = None

		return

	class Skill:
		def __init__(self, key):
			self.key = key

			return

	class Buff:
		def __init__(self, name, key, cooldown, waitTime, timer):
			self.name = name
			self.key = key
			self.cooldown = cooldown
			self.waitTime = waitTime
			self.timer = timer

			return

	class Preset:
		def __init__(self, cooldown, instructions, timer):
			self.cooldown = cooldown
			self.instructions = instructions
			self.timer = timer

	class Potions:
		def __init__(self):
			#initializing variables
			self.minHP = int(890 + ((1054 - 890) * (char.hpThreshold / 100)))
			self.minMP = int(890 + ((1054 - 890) * (char.mpThreshold / 100)))

			return

		def checkPotions(self):
			im = pyautogui.screenshot()
			if(im.getpixel((self.minHP, 1039))[0] < 200):
				press(char.hpKey)
				wait(0.4)
			if(im.getpixel((self.minMP, 1055))[2] < 200):
				press(char.mpKey)
				wait(0.4)

			return

	#reading character data from file
	def readCharacterFromFile(self, charName):
		#opening character file
		configure = ConfigParser()
		configure.optionxform = lambda option: option
		configure.read("./character data/" + charName + ".ini")

		#reading general section
		self.charName = configure.get("general", "name")
		self.hpKey = configure.get("general", "hpKey")
		self.mpKey = configure.get("general", "mpKey")
		self.hpThreshold = configure.getint("general", "hpThreshold")
		self.mpThreshold = configure.getint("general", "mpThreshold")
		self.jumpKey = configure.get("general", "jumpKey")
		self.npcKey = configure.get("general", "npcKey")
		self.attackKey = configure.get("general", "attackKey")
		self.mapKey = configure.get("general", "mapKey")
		self.petFood = configure.get("general", "petFood")
		self.changeChannel = configure.get("general", "changeChannel")
		self.autoPetFood = configure.get("general", "autoPetFood")
		self.potions = self.Potions()
		self.ropeLiftExist = False

		#reading skills section
		lines = list(configure.items("skills"))
		for i in range(len(lines)):
			self.skills[lines[i][0]] = self.Skill(lines[i][1])
			if(lines[i][0] == "Rope Lift"):
				self.ropeLiftExist = True

		#reading buffs section
		count = 0
		lines = list(configure.items("buffs"))
		for i in range(len(lines)):
			dataList = lines[i][1].split(', ')
			if (dataList[3] == "on"):
				self.buffs.append(self.Buff(lines[i][0], dataList[0], float(dataList[1]), float(dataList[2]), time.perf_counter()))
				count = count + 1
		self.buffsNum = count

		#reading presets section
		lines = list(configure.items("presets"))
		for i in range(len(lines)):
			dataList = lines[i][1].split(', ')
			dataList2 = dataList[1].split('/')
			self.presets[lines[i][0]] = self.Preset(float(dataList[0]), dataList2, time.perf_counter())

		#reading reset skills section
		lines = list(configure.items("resets"))
		for i in range(len(lines)):
			self.resets.append(self.Skill(lines[i][1]))

		#setting pet food timer if needed
		if (self.autoPetFood == "on"):
			self.petTimer = time.perf_counter() + 900
			wait(0.2)

		return

	#function to cycle buffs and check for expired cooldowns
	def checkBuffs(self):
		if (self.autoPetFood == "on" and time.perf_counter() > self.petTimer):
			press(self.petFood)
			self.petTimer = time.perf_counter() + 900
			wait(0.2)

		for i in range(self.buffsNum):
			if(time.perf_counter() > self.buffs[i].timer):
				wait(1)
				release("Left")
				release("Right")
				wait(0.2)
				press(self.buffs[i].key)
				wait(self.buffs[i].waitTime)
				self.buffs[i].timer = (time.perf_counter() + self.buffs[i].cooldown)

		return

#creating Markers class
class Markers:
	def __init__(self):
		#setting directory paths
		self.maindir = os.path.dirname(__file__)
		self.assetsdir = os.path.join(self.maindir, "assets")

		#initializing markers
		self.charMarker = os.path.join(self.assetsdir, "characterminimap.png")
		self.runeMarker = os.path.join(self.assetsdir, "runeminimap.png")
		self.navigationMarker = os.path.join(self.assetsdir, "navigation.png")
		self.okteleportMarker = os.path.join(self.assetsdir, "okteleport.png")
		self.okdeathMarker = os.path.join(self.assetsdir, "okdeath.png")
		self.cancelMarker = os.path.join(self.assetsdir, "cancel.png")
		self.dialogueMarker = os.path.join(self.assetsdir, "dialogue.png")
		self.changeChannelMarker = os.path.join(self.assetsdir, "changechannel.png")

#creating Rune class
class Rune:
	def __init__(self):
		self.timer = time.perf_counter()
		self.status = 0
		self.x = None
		self.y = None
		self.buffExistsMarker = os.path.join(markers.assetsdir, "buffexists.png")
		self.runeSolvedMarker = os.path.join(markers.assetsdir, "runesolved.png")
		self.runeCooldownMarker = os.path.join(markers.assetsdir, "runecooldown.png")
		modelsdir = os.path.join(markers.maindir, "models")
		self.arrowsdir = os.path.join(markers.maindir, "arrows")
		self.findArrow = tensorflow.keras.models.load_model(os.path.join(modelsdir, 'find_arrow.h5'), compile = False)
		self.solveArrow = tensorflow.keras.models.load_model(os.path.join(modelsdir, 'solve_arrow.h5'), compile = False)

	def solve(self):
		size = (224, 224)
		dataFind = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
		dataSolve = np.ndarray(shape=(4, 224, 224, 3), dtype=np.float32)
		arrowsList = []

		#get arrows
		x = 675
		counter = 1
		skipFlag = False

		#preprocess image
		image = ImageGrab.grab()
		image = np.asarray(image)
		image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

		#gaussian blur
		image = cv2.GaussianBlur(image, (3, 3), 0)

		#color transform
		image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

		#change to grayscale
		coefficients = (0.0445, 0.6568, 0.2987)
		image = cv2.transform(image, np.array(coefficients).reshape((1, 3)))
		
		#change back to color
		image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

		image = Image.fromarray(np.uint8(image)).convert('RGB')
		while (x < 1175 and counter < 5):
			im = pyautogui.screenshot()
			if(im.getpixel((char.potions.minHP, 1039))[0] < 200):
				return False
			
			y = 150
			while(y < 210):
				im = image.crop((x, y, x + 75, y + 75))
				im1 = ImageOps.fit(im, size, Image.ANTIALIAS)
				image_array = np.asarray(im1)
				normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
				dataFind[0] = normalized_image_array
				prediction = self.findArrow.predict(dataFind)
				if (prediction[0][0] > 0.80):
					arrowsList.append(image_array)
					counter = counter + 1
					skipFlag = True
					break
				y = y + 10
			if (skipFlag == True):
				x = x + 80
				skipFlag = False
			else:
				x = x + 20

		#if 4 arrows are not found, return false
		if (counter != 5):
			return False

		#preprocess
		for i in range(4):
			img = arrowsList[i]
			dataSolve[i] = (img.astype(np.float32) / 127.0) - 1

		#solve
		order = []
		prediction = self.solveArrow.predict(dataSolve)
		for i in range (counter - 1):
			#find max
			maxVal = 0
			maxIT = -1
			for j in range(4):
				if(maxVal < prediction[i][j]):
					maxVal = prediction[i][j]
					maxIT = j
			if (maxIT == 0):
				order.append("left")
			elif (maxIT == 1):
				order.append("right")
			elif (maxIT == 2):
				order.append("down")
			elif (maxIT == 3):
				order.append("up")

		return order

	#checking for rune and navigating to it if it exists
	def checkRune(self):
		#if rune does not exist
		if (time.perf_counter() > self.timer):
			runePos = pyautogui.locate(markers.runeMarker, pyautogui.screenshot(region=(mapdata.minX, mapdata.minY, mapdata.width, mapdata.height)))
			release("left")
			release("right")
			#if rune is found and rune cooldown is not on
			if (runePos != None and not(self.runeCooldown())):
				#mark rune position with offset
				self.x = runePos[0] + 2
				self.y = runePos[1] - 2

				#find rune platform
				for platformID in range(mapdata.platformsNum):
					if (self.y <= mapdata.platforms[platformID].Y + 2 and self.y >= mapdata.platforms[platformID].Y - 2 and self.x >= mapdata.platforms[platformID].leftX and self.x <= mapdata.platforms[platformID].rightX):
						break

				#try to solve 10 times
				for i in range(10):
					char.potions.checkPotions()
					#navigate to rune
					if (char.ropeLiftExist == "True"):
						moveTo(self.x, mapdata.platforms[platformID].Y)
						press(char.npcKey)
					else:
						charPos = bot.characterPos()
						if (charPos[1] == mapdata.platforms[platformID].Y and charPos[0] >= mapdata.platforms[platformID].leftX and charPos[0] <= mapdata.platforms[platformID].rightX):
							print("SAME PLATFORM")
							if (moveTo(self.x, mapdata.platforms[platformID].Y)):
								print("HERE1")
								press(char.npcKey)
							else:
								print("HERE2")
								return False
						else:
							return False


					print("Solving rune")
					wait(0.5)
					char.potions.checkPotions()
					order = self.solve()
					#if solver returns order
					if(order != False):
						for i in range(4):
							press(order[i])
							wait(0.05)
						wait(3)
						#if solver fails
						if(not(self.runeSolved())):
							for i in range(2):
								press(char.attackKey)
								wait(1)
						#if solved passes
						else:
							self.timer = time.perf_counter() + 850
							return True
					#if solver does not return order
					else:
						if(not(self.runeSolved())):
							for i in range(3):
								press(char.attackKey)
								wait(1)
						else:
							self.timer = time.perf_counter() + 850
							return True
					char.potions.checkPotions()
				print("Rune failed 10 times. changing channel")
				#if rune try failed 10 times change channel
				errorcheck.changeChannel()
				self.timer = time.perf_counter() + 15
				return

	def runeSolved(self):
		x = 1900
		failCounter = 0
		while(x >= 500 and failCounter <= 3):
			pyautogui.moveTo(x, 15, duration = 0.1)
			#if buff exists check if rune solved buff is active
			if (not(pyautogui.locate(self.buffExistsMarker, pyautogui.screenshot(region=(1000, 31, 500, 3))) == None)):
				if (not(pyautogui.locate(self.runeSolvedMarker, pyautogui.screenshot(region=(1000, 63, 500, 1))) == None)):
					print("RUNE SOLVED")
					return True
				x = x - 32
			else:
				failCounter = failCounter + 1
				x = x - 32

		return False

	def runeCooldown(self):
		x = 1900
		failCounter = 0
		while(x >= 500 and failCounter <= 3):
			pyautogui.moveTo(x, 15, duration = 0.1)
			#if buff exists check if rune cooldown buff is active
			if (not(pyautogui.locate(self.buffExistsMarker, pyautogui.screenshot(region=(1000, 31, 500, 3))) == None)):
				line = pyautogui.screenshot(region=(1000, 63, 500, 1))
				if (not(pyautogui.locate(self.runeCooldownMarker, pyautogui.screenshot(region=(1000, 63, 500, 1))) == None)):
					print("RUNE ON COOLDOWN")
					return True
				x = x - 32
			else:
				failCounter = failCounter + 1
				x = x - 32

		return False
		

	###	while(True):
	###		pyautogui.moveTo(deathFlag[0] + 3, deathFlag[1] + 3, duration = 1)

#creating ErrorCheck class
class ErrorCheck:
	def __init__(self):
		self.prevPos = None
		self.failCounter = 0

	#checking each error
	def checkAllErrors(self):
		print("CHECKING DEATH")
		if (not(self.checkDeath())):
			print("Fail")
			print("CHECKING DIALOGUE")
			if (not(self.checkDialogue())):
				print("Fail")
				print("CHECKING CEMETERY")
				if (not(self.checkCemetery())):
					print("Fail")
					print("CHECKING OTHER MAP")
					if (not(self.checkOtherMap())):
						print("Fail")
						print("CHECKING ROPE")
						if (not(self.checkRope())):
							print("Fail")
							print("Unsolved Error Detected")
							return False
		return True

	#checking death
	def checkDeath(self):
		#moving mouse out of the way
		pyautogui.moveTo(10, 10, duration = 1)

		#check for buff freezer
		cancelFlag = pyautogui.locate(markers.cancelMarker, pyautogui.screenshot())
		if (not(cancelFlag == None)):
			pyautogui.moveTo(cancelFlag[0] + 3, cancelFlag[1] + 3, duration = 1)
			pyautogui.click()
			wait(1)

		#check for death
		deathFlag = pyautogui.locate(markers.okdeathMarker, pyautogui.screenshot())
		if (deathFlag == None):
			return False
		else:
			pyautogui.moveTo(deathFlag[0] + 3, deathFlag[1] + 3, duration = 1)
			pyautogui.click()
			self.mapChangeCheck()
			return True

	#checking rope
	def checkRope(self):
		#check if player is on rope
		charPos = bot.characterPos()
		for i in range (mapdata.ropesNum):
			if (mapdata.ropes[i].X == charPos[0] and mapdata.ropes[i].bottomY >= charPos[1] and mapdata.ropes[i].topY <= charPos[1]):
				release("Right")
				wait(0.1)
				release("Left")
				wait(0.1)
				release("down")
				wait(0.1)
				hold("Up")
				wait(5)
				release("Up")
				return True

		return False

	#checking if dialogue has been entered
	def checkDialogue(self):
		#check if dialogue has occurred
		dialogueFlag = pyautogui.locate(markers.dialogueMarker, pyautogui.screenshot())
		if (dialogueFlag == None):
			return False
		else:
			pyautogui.moveTo(dialogueFlag [0] + 3, dialogueFlag [1] + 3, duration = 1)
			pyautogui.click()
			wait(1)
			return True

	#checking if player is at the cemetery		
	def checkCemetery(self):
		#check map size
		im = pyautogui.screenshot()
		rBorder = [221, 221, 221]
		x = mapdata.cem_maxX
		pixel = im.getpixel((x + 1, 74))
		if (pixel[0] == rBorder[0] and pixel[1] == rBorder[1] and pixel[2] == rBorder[2]):
			pixel = im.getpixel((x + 2, 74))
			if (pixel[0] == rBorder[0] and pixel[1] == rBorder[1] and pixel[2] == rBorder[2]):
				pixel = im.getpixel((x + 1, 75))
				if (pixel[0] == rBorder[0] and pixel[1] == rBorder[1] and pixel[2] == rBorder[2]):
					pixel = im.getpixel((x + 2, 75))
					if (pixel[0] == rBorder[0] and pixel[1] == rBorder[1] and pixel[2] == rBorder[2]):
						print("CEMETERY DETECTED")
						char.potions.checkPotions()
						wait(1)
						pyautogui.moveTo(10, 10, duration = 1)
						wait(1)
						press(char.mapKey)
						wait(1)
						navPos = pyautogui.locate(markers.navigationMarker, pyautogui.screenshot())
						if (navPos == None):
							return False
						pyautogui.moveTo(mapdata.map_coordX + navPos[0], mapdata.map_coordY + navPos[1], duration = 1)
						pyautogui.click()
						wait(0.10)
						pyautogui.click()
						wait(1)
						okPos = pyautogui.locate(markers.okteleportMarker, pyautogui.screenshot())
						if (okPos == None):
							return False
						else:
							pyautogui.moveTo(okPos[0] + 3, okPos[1] + 3, duration = 1)
							pyautogui.click()
							self.mapChangeCheck()
							wait(2)
							for i in range(5):
								press(char.attackKey)
								wait(1)
							for i in range(len(char.resets)):
								wait(2)
								press(char.resets[i].key)
							return True

		return False

	#checking if player has entered another map
	def checkOtherMap(self):
		im = pyautogui.screenshot()
		rBorder = [221, 221, 221]
		bBorder = [255, 255, 255]
		x = mapdata.maxX
		y = mapdata.maxY
		pixel = im.getpixel((x + 1, 74))
		pixel2 = im.getpixel((65, y + 1))
		if (not(pixel[0] == rBorder[0]) or not(pixel[1] == rBorder[1]) or not(pixel[2] == rBorder[2]) or not(pixel2[0] == bBorder[0]) or not(pixel2[1] == bBorder[1]) or not(pixel2[2] == bBorder[2])):
			print("OTHER MAP DETECTED")
			press(char.mapKey)
			pyautogui.moveTo(10, 10, duration = 1)
			wait(1)
			navPos = pyautogui.locate(markers.navigationMarker, pyautogui.screenshot())
			if (navPos == None):
				return False
			pyautogui.moveTo(mapdata.map_coordX + navPos[0], mapdata.map_coordY + navPos[1], duration = 1)
			pyautogui.click()
			wait(0.10)
			pyautogui.click()
			wait(1)
			okPos = pyautogui.locate(markers.okteleportMarker, pyautogui.screenshot())
			if (okPos == None):
				return False
			else:
				pyautogui.moveTo(okPos[0] + 3, okPos[1] + 3, duration = 1)
				pyautogui.click()
				self.mapChangeCheck()
				wait(2)
				for i in range(5):
					press(char.attackKey)
					wait(1)
				return True

		return False

	#check when changing from black to map has occurred
	def mapChangeCheck(self):
		#check if character has exited current map
		overTimer = time.perf_counter() + 5

		exitFlag = False
		while (exitFlag == False):
			if (overTimer < time.perf_counter()):
				return False
			im = pyautogui.screenshot(region=(8, 1073, 1, 1))
			pixel = im.getpixel((0, 0))
			if(not(pixel[0] == 221) and not(pixel[1] == 221) and not(pixel[2] == 221)):
				exitFlag = True

		while (True):
			im = pyautogui.screenshot(region=(8, 1073, 1, 1))
			pixel = im.getpixel((0, 0))
			if(pixel[0] == 221 and pixel[1] == 221 and pixel[2] == 221):
				return True

	#change channel to a random channel
	def changeChannel(self):
		release("Left")
		wait(0.1)
		release("Right")
		#getting random variables	
		verticalChange = random.randint(1,5)
		horizontalChange = random.randint(1,4)

		#loop to attempt channel change until succeed
		while (True):
			#check death
			if (self.checkDeath()):
				print("Death occurred while changing channel")
				self.changeChannel()
				self.checkCemetery()
				print("Cemetery left after changing channel")
				return True
			press(char.changeChannel)
			wait(1)
			for i in range(verticalChange):
				press("Down")
				wait(0.05)
			for i in range(horizontalChange):
				press("Right")
				wait(0.05)
			buttonPos = pyautogui.locate(markers.changeChannelMarker, pyautogui.screenshot())
			if (not(buttonPos == None)):
				pyautogui.moveTo(buttonPos[0] + 3, buttonPos[1] + 3, duration = 1)
				pyautogui.click()
				if (self.mapChangeCheck()):
					print("Successfully changed channel")
					return True

#creating OtherPlayerCheck class
class OtherPlayerCheck:
	def __init__(self):
		self.timer = time.perf_counter()
		self.stayTimer = time.perf_counter()
		self.status = 0
		self.randomMarker = os.path.join(markers.assetsdir, "randomplayer.png")
		self.buddyMarker = os.path.join(markers.assetsdir, "buddyplayer.png")
		self.guildMarker = os.path.join(markers.assetsdir, "buddyplayer.png")

		return

	def checkOtherPlayer(self):
		#when timer runs out, check for players
		if (self.timer < time.perf_counter()):
			if (not(pyautogui.locate(self.randomMarker, pyautogui.screenshot(region=(mapdata.minX, mapdata.minY, mapdata.width, mapdata.height))) == None) or (not(pyautogui.locate(self.buddyMarker, pyautogui.screenshot(region=(mapdata.minX, mapdata.minY, mapdata.width, mapdata.height))) == None)) or (not(pyautogui.locate(self.guildMarker, pyautogui.screenshot(region=(mapdata.minX, mapdata.minY, mapdata.width, mapdata.height))) == None))):
				print("Another player has been detected")
				release("Left")
				release("Right")
				count = 0
				#check 6 times over 30 seconds to see if player remains
				for i in range(15): 
					wait(2)
					if (not(pyautogui.locate(self.randomMarker, pyautogui.screenshot(region=(mapdata.minX, mapdata.minY, mapdata.width, mapdata.height))) == None) or not(pyautogui.locate(self.buddyMarker, pyautogui.screenshot(region=(mapdata.minX, mapdata.minY, mapdata.width, mapdata.height))) == None) or not(pyautogui.locate(self.guildMarker, pyautogui.screenshot(region=(mapdata.minX, mapdata.minY, mapdata.width, mapdata.height))) == None)):
						count = count + 1
				if (count >= 10):
					print("Changing channel")
					print("Number of times another player showed up is:", count)
					errorcheck.changeChannel()
					return True
			
			self.timer = time.perf_counter() + 15

#creating Menu class
class Menu:
	#function to initialize character data/map data/route data
	def initializeInfo(self):
		#initializing default file
		configureDefault = ConfigParser()
		configureDefault.read("default.ini")

		#prompt user for character name
		charName = input("Enter character name: ")
		if(charName == ""):
			charName = configureDefault.get("general", "character")

		#prompt user for map name
		mapName = input("Enter map name: ")
		if(mapName == ""):
			mapName = configureDefault.get("general", "map")

		#reading from file with input specified character and map
		mapdata.readMapFromFile(mapName)
		char.readCharacterFromFile(charName)
		route.readRouteFromFile(charName, mapName)

		return

	#run bot function
	def runBot(self):
		#initializing info
		self.initializeInfo()

		#ready user for bot
		input("You will have 2 seconds to tab into the game. Are you ready to start? (Enter anything to continue): ")
		wait(2)

		#starting bot
		bot.start()

		return

	#pause menu function
	def menuPause(self):
		#printing menu and receiving input
		print("PAUSE MENU")
		print("1. Continue Bot")
		print("2. Refresh Data")
		print("3. Exit Bot")
		choice = input(">> ")

		#checking if choice is valid
		while(choice != "1" and choice != "2" and choice != "3" and choice != ""):
			choice = input("Enter a valid input: ")

		#resume bot
		if(choice == "1" or choice == ""):
			print("Resuming bot")
			bot.refresh()

			return

		#refresh data
		if(choice == "2"):
			global char
			global mapdata
			global route
			charName = char.charName
			mapName = mapdata.mapName
			char = CharacterData()
			mapdata = MapData()
			route = RouteData()
			char.readCharacterFromFile(charName)
			mapdata.readMapFromFile(mapName)
			route.readRouteFromFile(charName, mapName)

			print("Resuming bot")
			bot.refresh()

			return

		#exit bot
		if(choice == "3"):
			print("Exiting bot")
			release('Left')
			release('Right')
			sys.exit()

		return

#creating Bot class
class Bot:
	def __init__(self):
		self.prevPos = None
		self.movementStuckCount = 0

	#run bot function
	def start(self):
		#initial refresh
		self.prevPos = self.characterPos()
		self.refresh()

		#run sequence
		while(True):
			self.runSequence()
			self.refresh()

		return

	#function to refresh and check variables in between sequences
	def refresh(self):
		#check if pause key is pressed
		if(keyboard.is_pressed("F8")):
			menu.menuPause()

		#potion check
		char.potions.checkPotions()

		#check buffs
		char.checkBuffs()

		#check rune
		rune.checkRune()

		#check other players
		otherplayercheck.checkOtherPlayer()

		return

	#function to run a sequence step
	def runSequence(self):
		#get player location
		charPos = self.characterPos()

		# #check if position is repeated
		if (self.prevPos == charPos):
			self.movementStuckCount = self.movementStuckCount + 1
			if (self.movementStuckCount >= 5):
				errorcheck.checkAllErrors()
		else:
			self.movementStuckCount = 0

		#setting previous position
		self.prevPos = charPos

		#finding section
		section = self.findSection(charPos)
		if (section == None):
			return

		#run sequence of the section
		for i in range(len(route.instructions[section].sequence)):
			exec(route.instructions[section].sequence[i])

		return

	#getting character position on mini map
	def characterPos(self):
		charPos = pyautogui.locate(markers.charMarker, pyautogui.screenshot(region=(mapdata.minX, mapdata.minY, mapdata.width, mapdata.height)))
		failCounter = 0
		#if character is not found
		while (charPos == None):
			charPos = pyautogui.locate(markers.charMarker, pyautogui.screenshot(region=(mapdata.minX, mapdata.minY, mapdata.width, mapdata.height)))
			#repeat 50 times. then if character is still not found
			if (failCounter >= 50):
				#check if player icon can be found outside of map size
				charPos = pyautogui.locate(markers.charMarker, pyautogui.screenshot(region=(mapdata.minX, mapdata.minY, 600, 500)))
				if (not(charPos == None)):
					print("Not in current map dimensions")
					errorcheck.checkAllErrors()
				else:
					failCounter = 0
			failCounter = failCounter + 1

		return charPos

	#finds the section of the character positioning
	def findSection(self, charPos):
		for i in range (route.routeNum):
			if (route.instructions[i].Y == charPos[1]):
				if (route.instructions[i].leftX <= charPos[0] and route.instructions[i].rightX >= charPos[0]):
					return i

		for i in range (route.routeNum):
			if (route.instructions[i].Y == charPos[1]):
				if (route.instructions[i].leftX - 1 <= charPos[0] and route.instructions[i].rightX + 1 >= charPos[0]):
					return i
			
		return None

#function to wait x seconds
def wait(x):
	time.sleep(x)

#function to press a key
def press(key):
	keyboard.press(key)
	wait(0.05)
	keyboard.release(key)

#function to hold a key
def hold(key):
	if(not(keyboard.is_pressed(key))):
		keyboard.press(key)

#function to release a key
def release(key):
	keyboard.release(key)

#function to jump
def jump():
	press(char.jumpKey)

#function to attack
def attack():
	press(char.attackKey)

#function to use skill
def useSkill(name):
	press(char.skills[name].key)

def usePreset(name):
	if (time.perf_counter() > char.presets[name].timer):
		for i in range(len(char.presets[name].instructions)):
			exec(char.presets[name].instructions[i])
		char.presets[name].timer = time.perf_counter() + char.presets[name].cooldown

#function to move to a position
def moveTo(x, y):
	overTimer = time.perf_counter() + 20
	if (char.ropeLiftExist == False):
		while(True):
			if (overTimer < time.perf_counter()):
				errorcheck.checkAllErrors()
				overTimer = time.perf_counter() + 20

			charPos = bot.characterPos()
			if(charPos[0] < x - 2):
				release("Left")
				hold("Right")
			elif(charPos[0] > x + 2):
				release("Right")
				hold("Left")
			elif(charPos[0] < x):
				release("Left")
				press("Right")
				wait(0.1)
			elif(charPos[0] > x):
				release("Right")
				press("Left")
				wait(0.1)
			else:
				release("Left")
				release("Right")
				wait(0.1)
				charPos = bot.characterPos()
				if (charPos[0] == x and charPos[1] == y):
					return True
				else:
					return False
	else:
		while(True):
			if (overTimer < time.perf_counter()):
				errorcheck.checkAllErrors()
				overTimer = time.perf_counter() + 20

			charPos = bot.characterPos()
			if(charPos[0] < x - 3):
				release("Left")
				hold("Right")
			elif(charPos[0] > x + 2):
				release("Right")
				hold("Left")
			elif(charPos[0] < x):
				release("Left")
				press("Right")
				wait(0.1)
			elif(charPos[0] > x):
				release("Right")
				press("Left")
				wait(0.1)
			else:
				release("Left")
				release("Right")
				if(charPos[1] < y - 2):
					press("Right")
					wait(0.1)
					hold("Down")
					wait(0.1)
					press(char.jumpKey)
					wait(0.2)
					release("Down")
				elif(charPos[1] > y + 2):
					useSkill("Rope Lift")
					wait(4)
				else:
					wait(0.1)
					return True

#main function
def main():
	#initializing global classes

	global menu
	global bot
	global markers
	global char
	global mapdata
	global route
	global rune
	global otherplayercheck
	global errorcheck

	menu = Menu()
	bot = Bot()
	markers = Markers()
	char = CharacterData()
	mapdata = MapData()
	route = RouteData()
	rune = Rune()
	otherplayercheck = OtherPlayerCheck()
	errorcheck = ErrorCheck()


	#prompting user with menu and running bot
	menu.runBot()

	return

main()