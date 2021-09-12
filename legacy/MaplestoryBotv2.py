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

		return

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

#creating CharacterData class
class CharacterData:
	def __init__(self):
		self.skillsNum = 0
		self.buffsNum = 0
		self.resetSkillsNum = 0
		self.skills = []
		self.buffs = []
		self.resetSkills = []
		self.timer = []

		return

class Skill:
	def __init__(self, name, key):
		self.name = name
		self.key = key

		return

class Buff:
	def __init__(self, name, key, cooldown, waitTime, toggle):
		self.name = name
		self.key = key
		self.cooldown = cooldown
		self.waitTime = waitTime
		self.toggle = toggle

		return

class Potions:
	def __init__(self):
		#initializing variables
		self.minHP = int(890 + ((1054 - 890) * (char.hpThreshold / 100)))
		self.minMP = int(890 + ((1054 - 890) * (char.mpThreshold / 100)))
		self.hpKey = char.hpKey
		self.mpKey = char.mpKey

		return

	def checkPotions(self):
		im = pyautogui.screenshot()
		if(im.getpixel((self.minHP, 1039))[0] < 200):
			press(self.hpKey)
			wait(0.4)
		if(im.getpixel((self.minMP, 1055))[2] < 200):
			press(self.mpKey)
			wait(0.4)

		return

class Rune:
	def __init__(self):
		self.timer = time.perf_counter()
		self.status = 0
		self.x = None
		self.y = None

class RuneSolver:
	def __init__(self):
		#getting models directory
		modelsdir = os.path.join(maindir, "models")

		#loading models
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
			if(im.getpixel((potions.minHP, 1039))[0] < 200):
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

class AllGlobals:
	def __init__(self):
		self.prevPos = None

#main menu function
def menu():
	#resetting mapdata, char, route
	mapdata = MapData()
	char = CharacterData()
	route = RouteData()

	#prompt user with menu
	print("MENU")
	print("1. Run bot")
	print("2. Exit program")
	choice = input("Enter your choice: ")

	#user input checking
	while (choice != "1" and choice != "2"  and choice != ""):
		choice = input("Enter a valid option: ")

	#if running bot
	if (choice == "1" or choice == ""):
		runBot()

	#if exiting program
	if (choice == "2"):
		exitProgram()
		
	return

#pause menu function
def menuPause():
	#printing menu and receiving input
	print("PAUSE MENU")
	print("1. Continue Bot")
	print("2. Refresh Data")
	print("3. Exit Bot")
	choice = input(">> ")

	#checking if choice is valids
	while(choice != "1" and choice != "2" and choice != "3" and choice != ""):
		choice = input("Enter a valid input: ")

	#refresh data
	if(choice == "2"):
		charName = char.charName
		mapName = mapdata.mapName
		char = CharacterData()
		mapdata = MapData()
		route = RouteData()
		readCharacterFromFile(charName)
		readMapFromFile(mapName)
		readRouteFromFile(charName, mapName)

	#exit bot
	if(choice == "3"):
		print("Exiting bot")
		release('Left')
		release('Right')
		sys.exit()

	#continue bot
	print("Resuming bot")
	refresh()
	return

#run bot function
def runBot():
	#prompt user for character name
	charName = input("Enter character name: ")
	if(charName == ""):
		configure = ConfigParser()
		configure.read("default.ini")
		charName = configure.get("general", "character")

	#user input checking
	while (not(os.path.exists(os.path.join(chardir, charName + ".ini")))):
		charName = input("Enter a valid character name: ")

	#prompt user for map name
	mapName = input("Enter map name: ")
	if(mapName == ""):
		configure = ConfigParser()
		configure.read("default.ini")
		mapName = configure.get("general", "map")

	#user input checking
	while (not(os.path.exists(os.path.join(mapdir, mapName + ".ini")))):
		mapName = input("Enter a valid map name: ")

	#reading from file with input specified character and map
	readCharacterFromFile(charName)
	readMapFromFile(mapName)
	readRouteFromFile(charName, mapName)
	global potions
	potions = Potions()


	#ready user for bot
	while (True):
		choice = input("You will have 2 seconds to tab into the game. Are you ready to start? (y/n): ")
		while (choice != "y" and choice != "n" and choice != ""):
			choice = input("Enter a valid option (y/n): ")
		if (choice == "y" or choice == ""):
			break
	wait(2)

	#initial buffs
	if (char.autoPetFood == "on"):
		press(char.petFood)
		char.petTimer = time.perf_counter() + 300
		wait(0.2)
	initialBuffs()
	refresh()
	allglobals.prevPos = characterPos()

	#run sequence
	while (True):
		runSequence()
		refresh()

	return

#end program function
def exitProgram():
	#exiting program
	print("Exiting program")
	sys.exit()

	return

#reading character data from file
def readCharacterFromFile(charName):
	#opening character file
	charPath = os.path.join(chardir, charName + ".ini")
	configure = ConfigParser()
	configure.read(charPath)

	#reading general section
	char.charName = configure.get("general", "name")
	char.hpKey = configure.get("general", "hpKey")
	char.mpKey = configure.get("general", "mpKey")
	char.hpThreshold = configure.getint("general", "hpThreshold")
	char.mpThreshold = configure.getint("general", "mpThreshold")
	char.jumpKey = configure.get("general", "jumpKey")
	char.npcKey = configure.get("general", "npcKey")
	char.attackKey = configure.get("general", "attackKey")
	char.mapKey = configure.get("general", "mapKey")
	char.petFood = configure.get("general", "petFood")
	char.autoPetFood = configure.get("general", "autoPetFood")
	char.skillsNum = configure.getint("general", "skillsNum")
	char.buffsNum = configure.getint("general", "buffsNum")
	char.resetSkillsNum = configure.getint("general", "resetSkillsNum")
	char.ropeLiftExist = False

	#reading skills section
	for i in range(char.skillsNum):
		dataList = [value for value in configure["skills"]["skill" + str(i + 1)].split(', ')]
		char.skills.append(Skill(dataList[0], dataList[1]))
		if (char.skills[i].name == "Rope Lift"):
			char.ropeLiftExist = True

	#reading buffs section
	for i in range(char.buffsNum):
		dataList = [value for value in configure["buffs"]["buff" + str(i + 1)].split(', ')]
		char.buffs.append(Buff(dataList[0], dataList[1], float(dataList[2]), float(dataList[3]), dataList[4]))

	#reading reset skills section
	for i in range(char.resetSkillsNum):
		dataList = [value for value in configure["resets"]["skill" + str(i + 1)].split(', ')]
		char.resetSkills.append(Skill(dataList[0], dataList[1]))

	return

#reading map data from file
def readMapFromFile(mapName):
	#opening map file
	mapPath = os.path.join(mapdir, mapName + ".ini")
	configure = ConfigParser()
	configure.read(mapPath)

	#reading general section
	mapdata.mapName = configure.get("general", "mapName")
	mapdata.minX = configure.getint("general", "minX")
	mapdata.maxX = configure.getint("general", "maxX")
	mapdata.minY = configure.getint("general", "minY")
	mapdata.maxY = configure.getint("general", "maxY")
	mapdata.width = configure.getint("general", "width")
	mapdata.height = configure.getint("general", "height")
	mapdata.platformsNum = configure.getint("general", "platformsNum")
	mapdata.ropesNum = configure.getint("general", "ropesNum")
	mapdata.portalsNum = configure.getint("general", "portalsNum")
	mapdata.cem_maxX = configure.getint("general", "cemMaxX")
	mapdata.cem_maxY = configure.getint("general", "cemMaxY")
	mapdata.cem_width = configure.getint("general", "cemWidth")
	mapdata.cem_height = configure.getint("general", "cemHeight")
	mapdata.map_coordX = configure.getint("general", "mapCoordX")
	mapdata.map_coordY = configure.getint("general", "mapCoordY")

	#reading platforms section
	for i in range(mapdata.platformsNum):
		dataList = [int(value) for value in configure["platforms"]["platform" + str(i + 1)].split(', ')]
		mapdata.platforms.append(Platform(dataList[0], dataList[1], dataList[2]))

	#reading ropes section
	for i in range(mapdata.ropesNum):
		dataList = [int(value) for value in configure["ropes"]["rope" + str(i + 1)].split(', ')]
		mapdata.ropes.append(Rope(dataList[0], dataList[1], dataList[2]))
		
	#reading portals section
	for i in range(mapdata.portalsNum):
		dataList = [int(value) for value in configure["portals"]["portal" + str(i + 1)].split(', ')]
		mapdata.portals.append(Portal(dataList[0], dataList[1], dataList[2], dataList[3]))

	return

#reading route data from file
def readRouteFromFile(charName, mapName):
	#opening route data file
	routePath = os.path.join(routedir, charName + "_" + mapName + ".ini")
	configure = ConfigParser()
	configure.read(routePath)

	#reading general section
	route.charName = configure.get("general", "charName")
	route.mapName = configure.get("general", "mapName")
	route.routeNum = configure.getint("general", "routeNum")

	#reading routes section
	for i in range(route.routeNum):
		rangeList = [int(value) for value in configure["routes"]["route" + str(i + 1) + "range"].split(", ")]
		route.instructions.append(Instruction(rangeList[0], rangeList[1], rangeList[2]))
		sequenceList = [value for value in configure["routes"]["route" + str(i + 1) + "sequence"].split(", ")]
		for j in range(len(sequenceList)):
			route.instructions[i].sequence.append(sequenceList[j])

	return

#function to run buffs at bot start
def initialBuffs():
	for i in range(char.buffsNum):
		if(char.buffs[i].toggle == "on"):
			press(char.buffs[i].key)
			wait(char.buffs[i].waitTime)
			char.timer.append(time.perf_counter() + char.buffs[i].cooldown)
		else:
			char.timer.append(time.perf_counter() + char.buffs[i].cooldown)

	return

#function to cycle buffs and check for expired cooldowns
def checkBuffs():
	for i in range(char.buffsNum):
		if (char.buffs[i].toggle == "on"):
			if(time.perf_counter() > char.timer[i]):
				wait(0.4)
				press(char.buffs[i].key)
				wait(char.buffs[i].waitTime)
				char.timer[i] = (time.perf_counter() + char.buffs[i].cooldown)

	return

#function to check pet food timer
def checkPetFood():
	if (char.autoPetFood == "on"):
		if (time.perf_counter() > char.petTimer):
			press(char.petFood)
			char.petTimer = time.perf_counter() + 300
			wait(0.2)

	return

#checking for rune and navigating to it if it exists
def checkRune():
	#if rune does not exist
	if (rune.status == 0 and time.perf_counter() > rune.timer):
		runePos = pyautogui.locate(runeMarker, pyautogui.screenshot(region=(mapdata.minX, mapdata.minY, mapdata.width, mapdata.height)))
		#if rune does not exist, check in 1 min
		if (runePos == None):
			rune.timer = time.perf_counter() + 10
		#if rune is found
		else:
			#mark rune position with offset
			rune.x = runePos[0] + 2
			rune.y = runePos[1] - 2
			#find rune platform
			for i in range(mapdata.platformsNum):
				if (rune.y <= mapdata.platforms[i].Y + 2 and rune.y >= mapdata.platforms[i].Y - 2 and rune.x >= mapdata.platforms[i].leftX and rune.x <= mapdata.platforms[i].rightX):
					rune.platformID = i
					rune.status = 1
					break

	#if rune exists already and rope lift does not exist
	elif (rune.status == 1):
		charPos = characterPos()
		#if on same platform, move to it, else skip for now
		if (charPos[1] == mapdata.platforms[rune.platformID].Y and charPos[0] >= mapdata.platforms[rune.platformID].leftX and charPos[0] <= mapdata.platforms[rune.platformID].rightX):
			isRunePlatform = True
		else:
			release("left")
			release("right")
			isRunePlatform = False
		while (isRunePlatform == True):
			potions.checkPotions()
			charPos = characterPos()
			#if standing on rune, solve it
			if (charPos[0] >= rune.x - 1 and charPos[0] <= rune.x + 1):
				release("left")
				release("right")
				press(char.npcKey)
				wait(0.5)
				result = runesolver.solve()
				#if solved
				if (result != False):
					for i in range(4):
						press(result[i])
						wait(0.05)
					rune.status = 0
					rune.timer = time.perf_counter() + 5
					return
				else:
					press(char.jumpKey)
					rune.status = 0
					rune.timer = time.perf_counter() + 5
					return False

			#if left of rune, move right
			elif (charPos[0] < rune.x):
				release("left")
				hold("right")
			#if right of
			elif (charPos[0] > rune.x):
				release("right")
				hold("left")
				
	return

def checkCemetary():
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
					print("CEMETARY DETECTED")
					potions.checkPotions()
					wait(1)
					press(char.mapKey)
					wait(3)
					pyautogui.moveTo(10, 10, duration = 1)
					navPos = pyautogui.locate(navigationMarker, pyautogui.screenshot())
					if (navPos == None):
						return False
					wait(1)
					pyautogui.moveTo(mapdata.map_coordX + navPos[0], mapdata.map_coordY + navPos[1], duration = 1)
					pyautogui.click()
					wait(0.10)
					pyautogui.click()
					wait(1)
					press("Enter")
					wait(5)
					for i in range(char.resetSkillsNum):
						wait(2)
						press(char.resetSkills[i].key)
					return True

	return False

def checkRope():
	#check if player is on rope
	charPos = characterPos()
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
			return

	return

def checkDeath():
	#check if player has died
	deathFlag = pyautogui.locate(deathMarker, pyautogui.screenshot())
	if (deathFlag == None):
		return False
	else:
		pyautogui.moveTo(deathFlag[0] + 3, deathFlag[1] + 3, duration = 1)
		pyautogui.click()
		wait(1)
		return True

def checkDialogue():
	#check if dialogue has occurred
	dialogueFlag = pyautogui.locate(dialogueMarker, pyautogui.screenshot())
	if (dialogueFlag  == None):
		return False
	else:
		pyautogui.moveTo(dialogueFlag [0] + 3, dialogueFlag [1] + 3, duration = 1)
		pyautogui.click()
		wait(1)
		return True

def checkOtherMap():
	#check if character has entered another map
	im = pyautogui.screenshot()
	rBorder = [221, 221, 221]
	bBorder = [255, 255, 255]
	x = mapdata.maxX
	y = mapdata.maxY
	pixel = im.getpixel((x + 1, 74))
	pixel2 = im.getpixel((65, y + 1))
	if (not(pixel[0] == rBorder[0]) or not(pixel[1] == rBorder[1]) or not(pixel[2] == rBorder[2]) or not(pixel2[0] == bBorder[0]) or not(pixel2[1] == bBorder[1]) or not(pixel2[2] == bBorder[2])):
		press(char.mapKey)
		wait(3)
		pyautogui.moveTo(10, 10, duration = 1)
		navPos = pyautogui.locate(navigationMarker, pyautogui.screenshot())
		if (navPos == None):
			return False
		wait(1)
		pyautogui.moveTo(mapdata.map_coordX + navPos[0], mapdata.map_coordY + navPos[1], duration = 1)
		pyautogui.click()
		wait(0.10)
		pyautogui.click()
		wait(1)
		press("Enter")
		wait(5)
		return True

	return False

#function to refresh and check variables in between sequences
def refresh():
	#check if pause key is pressed
	if(keyboard.is_pressed("F8")):
		menuPause()

	#potion check
	potions.checkPotions()

	#check pet food
	checkPetFood()

	#check rune
	checkRune()

	#check buffs
	checkBuffs()

	return

#function to run a sequence step
def runSequence():
	#get player location
	charPos = characterPos()
	if (allglobals.prevPos == charPos):
		solvedIdleFlag = checkDeath()
		if (solvedIdleFlag == False):
			solvedIdleFlag = checkDialogue()
			if (solvedIdleFlag == False):
				solveIdleFlag = checkCemetary()
				if (solvedIdleFlag == False):
					solveIdleFlag = checkOtherMap()
					if (solvedIdleFlag == False):
						checkRope()

	allglobals.prevPos = charPos
	section = findSection(charPos)
	if (section == None):
		return

	#run sequence of the section
	wait(0.1)
	for i in range(len(route.instructions[section].sequence)):
		exec(route.instructions[section].sequence[i])

	return

#getting character position on minimapdata
def characterPos():
	charPos = pyautogui.locate(charMarker, pyautogui.screenshot(region=(mapdata.minX, mapdata.minY, mapdata.width, mapdata.height)))
	failCounter = 0
	while (charPos == None):
		charPos = pyautogui.locate(charMarker, pyautogui.screenshot(region=(mapdata.minX, mapdata.minY, mapdata.width, mapdata.height)))
		if (failCounter >= 50):
			#check if player icon can be found in map
			charPos = pyautogui.locate(charMarker, pyautogui.screenshot(region=(mapdata.minX, mapdata.minY, 600, 500)))
			if (not(charPos == None)):
				solvedIdleFlag = checkCemetary()
				if (solvedIdleFlag == False):
					checkOtherMap()
			else:
				failCounter = 0
		failCounter = failCounter + 1

	return charPos

#finds the section of the character positioning
def findSection(charPos):
	for i in range (route.routeNum):
		if (route.instructions[i].Y == charPos[1] and route.instructions[i].leftX <= charPos[0] and route.instructions[i].rightX >= charPos[0]):
			return i

	for i in range (route.routeNum):
		if (route.instructions[i].Y == charPos[1] and route.instructions[i].leftX - 1 <= charPos[0] and route.instructions[i].rightX + 1 >= charPos[0]):
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
	for i in range(char.skillsNum):
		if (name == char.skills[i].name):
			press(char.skills[i].key)
			return

#main function
def main():
	#setting global directory pats
	global maindir
	global mapdir
	global chardir
	global routedir
	global assets

	maindir = os.path.dirname(__file__)
	mapdir = os.path.join(maindir, "map data")
	chardir = os.path.join(maindir, "character data")
	routedir = os.path.join(maindir, "route data")
	assetsdir = os.path.join(maindir, "assets")

	#initializing global classes
	global mapdata
	global char
	global route
	global rune
	global runesolver
	global allglobals
	mapdata = MapData()
	char = CharacterData()
	route = RouteData()
	rune = Rune()
	runesolver = RuneSolver()
	allglobals = AllGlobals()

	#initializing global markers
	global charMarker
	global runeMarker
	global navigationMarker
	global deathMarker
	global dialogueMarker
	charMarker = os.path.join(assetsdir, "characterminimap.png")
	runeMarker = os.path.join(assetsdir, "runeminimap.png")
	navigationMarker = os.path.join(assetsdir, "navigation.png")
	deathMarker = os.path.join(assetsdir, "okdeath.png")
	dialogueMarker = os.path.join(assetsdir, "dialogue.png")

	#prompting user with menu
	while(True):
		menu()

	return

main()