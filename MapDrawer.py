import sys
import os
import pyautogui
import win32api, win32con
import time
from PIL import ImageGrab
from configparser import ConfigParser

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
		self.cem_maxX = 0
		self.cem_maxY = 0
		self.cem_width = 0
		self.cem_height = 0
		self.map_coordX = 0
		self.map_coordY = 0

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

#main menu
def menu():
	#resetting mapdata
	mapdata = MapData()

	#prompt user with menu
	print("MENU")
	print("1. Add new map data")
	print("2. Edit map data")
	print("3. Exit program")
	choice = int(input("Enter your choice: "))

	#user input checking
	while (choice != 1 and choice != 2 and choice != 3):
		choice = int(input("Enter a valid option: "))

	#if adding new map data
	if (choice == 1):
		menuAddMap()

	#if editing map data
	if (choice == 2):
		menuEditMap()

	#if exiting program
	if (choice == 3):
		exitProgram()
		
	return

#menu to add new map data
def menuAddMap():
	#prompt user for map name
	flag = True
	while (flag == True):
		mapName = input("Enter the name of the map: ")
		choice = input("Is " + mapName + " a good name? (y/n): ")
		
		#user input checking
		while (choice != "y" and choice != "n"):
			choice = input("Enter a valid option: ")

		#finalize map name
		if (choice == "y"):
			print("Map name will be saved as " + mapName + ".")
			mapdata.mapName = mapName
			flag = False

	#getting map size
	flag = True
	while (flag == True):
		#prompt user instructions
		print("Put minimap on the very top left corner without anything obstructing it.")
		choice = input("Is it ready? (y/n): ")
		
		#user input checking
		while (choice != "y" and choice != "n"):
			choice = input("Enter a valid option: ")

		#add new map
		if (choice == "y"):
			flag = False
			getMapSize()
			writeToFile()

	return

#menu to edit map data
def menuEditMap():
	#prompt user for map name
	mapName = input("Enter map name: ")
	if(mapName == ""):
		configure = ConfigParser()
		configure.read("default.ini")
		mapName = configure.get("general", "map")

	#user input checking
	while (not(os.path.exists(os.path.join(mapdir, mapName + ".ini")))):
		mapName = input("Enter a valid map name: ")

	#reading map data
	readFromFile(mapName)

	flag = True
	while (flag == True):
		#prompt user with menu
		print("1. Add platform")
		print("2. Add rope")
		print("3. Add portal")
		print("4. Add cemetary")
		print("5. Finish editing")
		choice = input("Enter you choice: ")

		#user input checking
		while (choice != "1" and choice != "2" and choice != "3" and choice != "4" and choice != "5"):
			choice = input("Enter a valid option: ")

		#if adding platform
		if (choice == "1"):
			addPlatform()

		#if adding rope
		if (choice == "2"):
			addRope()

		#if adding portal
		if (choice == "3"):
			addPortal()

		#if adding cemetary
		if(choice == "4"):
			addCemetary()

		#if finished editing
		if(choice == "5"):
			flag = False

	return

#end program function
def exitProgram():
	#exiting program
	print("Exiting program")
	sys.exit()

	return

#writing map data data to file
def writeToFile():
	#opening map file
	mapPath = os.path.join(mapdir, mapdata.mapName + ".ini")
	file = open(mapPath, "w")

	#writing general section
	file.write("[general]\n")
	file.write("mapName = " + str(mapdata.mapName) + "\n")
	file.write("minX = " + str(mapdata.minX) + "\n")
	file.write("maxX = " + str(mapdata.maxX) + "\n")
	file.write("minY = " + str(mapdata.minY) + "\n")
	file.write("maxY = " + str(mapdata.maxY) + "\n")
	file.write("width = " + str(mapdata.width) + "\n")
	file.write("height= " + str(mapdata.height) + "\n")
	file.write("cemMaxX = " + str(mapdata.cem_maxX) + "\n")
	file.write("cemMaxY = " + str(mapdata.cem_maxY) + "\n")
	file.write("cemWidth = " + str(mapdata.cem_width) + "\n")
	file.write("cemHeight = " + str(mapdata.cem_height) + "\n")
	file.write("mapCoordX = " + str(mapdata.map_coordX) + "\n")
	file.write("mapCoordY = " + str(mapdata.map_coordY) + "\n")
	file.write("\n")

	#writing platforms section
	file.write("[platforms]\n")
	for i in range(mapdata.platformsNum):
		file.write(str(i + 1) + " = " + str(mapdata.platforms[i].leftX) + ", " + str(mapdata.platforms[i].rightX) + ", " + str(mapdata.platforms[i].Y) + "\n")
	file.write("\n")

	#writing ropes section
	file.write("[ropes]\n")
	for i in range (mapdata.ropesNum):
		file.write(str(i + 1) + " = " + str(mapdata.ropes[i].X) + ", " + str(mapdata.ropes[i].bottomY) + ", " + str(mapdata.ropes[i].topY) + "\n")
	file.write("\n")

	#writing portals section
	file.write("[portals]\n")
	for i in range (mapdata.portalsNum):
		file.write(str(i + 1) + " = " + str(mapdata.portals[i].X1) + ", " + str(mapdata.portals[i].Y1) + ", " + str(mapdata.portals[i].X2) + ", " + str(mapdata.portals[i].Y2) + "\n")
	file.write("\n")

	#closing file
	file.close()

	#prompting user if successfully written
	print("Map data successfully written.")

	return

#reading map data from file
def readFromFile(mapName):
	#opening map file
	configure = ConfigParser()
	configure.read("./map data/" + mapName + ".ini")

	#reading general section
	mapdata.mapName = configure.get("general", "mapName")
	mapdata.minX = configure.getint("general", "minX")
	mapdata.maxX = configure.getint("general", "maxX")
	mapdata.minY = configure.getint("general", "minY")
	mapdata.maxY = configure.getint("general", "maxY")
	mapdata.width = configure.getint("general", "width")
	mapdata.height = configure.getint("general", "height")
	mapdata.cem_maxX = configure.getint("general", "cemMaxX")
	mapdata.cem_maxY = configure.getint("general", "cemMaxY")
	mapdata.cem_width = configure.getint("general", "cemWidth")
	mapdata.cem_height = configure.getint("general", "cemHeight")
	mapdata.map_coordX = configure.getint("general", "mapCoordX")
	mapdata.map_coordY = configure.getint("general", "mapCoordY")

	#reading platforms section
	lines = list(configure.items("platforms"))
	mapdata.platformsNum = len(lines)
	for i in range(len(lines)):
		dataList = lines[i][1].split(', ')
		mapdata.platforms.append(Platform(int(dataList[0]), int(dataList[1]), int(dataList[2])))

	#reading ropes section
	lines = list(configure.items("ropes"))
	mapdata.ropesNum = len(lines)
	for i in range(len(lines)):
		dataList = lines[i][1].split(', ')
		mapdata.ropes.append(Rope(int(dataList[0]), int(dataList[1]), int(dataList[2])))
		
	#reading ropes section
	lines = list(configure.items("portals"))
	mapdata.portalsNum = len(lines)
	for i in range(len(lines)):
		dataList = lines[i][1].split(', ')
		mapdata.portals.append(Portal(int(dataList[0]), int(dataList[1]), int(dataList[2]), int(dataList[3])))

	return

#function to add new platform
def addPlatform():
	#get left side of platform
	flag = True
	while (flag == True):
		print("Stand on the very left of the platform.")
		choice = input("Is it ready? (y/n): ")
		
		#user input checking
		while (choice != "y" and choice != "n"):
			choice = input("Enter a valid option: ")

		#mark left side of platform
		if (choice == "y"):
			flag = False
			pos = characterPos()
			leftX = pos[0]
			Y = pos[1]

	#get right side of platform
	flag = True
	while (flag == True):
		print("Stand on the very right of the platform.")
		choice = input("Is it ready? (y/n): ")
		
		#user input checking
		while (choice != "y" and choice != "n"):
			choice = input("Enter a valid option: ")

		#mark right side of platform
		if (choice == "y"):
			flag = False
			pos = characterPos()
			rightX = pos[0]

	#add new platform to list and write to file
	mapdata.platforms.append(Platform(leftX, rightX, Y))
	mapdata.platformsNum = mapdata.platformsNum + 1
	writeToFile()

	return

#function to add new rope
def addRope():
	#get bottom of rope
	flag = True
	while (flag == True):
		print("Hang on the very bottom of the rope.")
		choice = input("Is it ready? (y/n): ")
		
		#user input checking
		while (choice != "y" and choice != "n"):
			choice = input("Enter a valid option: ")

		#mark bottom of rope
		if (choice == "y"):
			flag = False
			pos = characterPos()
			X = pos[0]
			bottomY = pos[1]

	#get top of rope
	flag = True
	while (flag == True):
		print("Climb to the top of the rope.")
		choice = input("Is it ready? (y/n): ")
		
		#user input checking
		while (choice != "y" and choice != "n"):
			choice = input("Enter a valid option: ")

		#mark top of rope
		if (choice == "y"):
			flag = False
			pos = characterPos()
			topY = pos[1]

	#add new rope to list and write to file
	mapdata.ropes.append(Rope(X, bottomY, topY))
	mapdata.ropesNum = mapdata.ropesNum + 1
	writeToFile()

	return

#function to add new portal
def addPortal():
	#get coordinates of first portal
	flag = True
	while (flag == True):
		print("Stand on one of the portals.")
		choice = input("Is it ready? (y/n): ")
		
		#user input checking
		while (choice != "y" and choice != "n"):
			choice = input("Enter a valid option: ")

		#mark first portal
		if (choice == "y"):
			flag = False
			pos = characterPos()
			X1 = pos[0]
			Y1 = pos[1]

	#get coordinates of second portal
	flag = True
	while (flag == True):
		print("Stand on the other portal.")
		choice = input("Is it ready? (y/n): ")
		
		#user input checking
		while (choice != "y" and choice != "n"):
			choice = input("Enter a valid option: ")

		#mark second portal
		if (choice == "y"):
			flag = False
			pos = characterPos()
			X2 = pos[0]
			Y2 = pos[1]

	#add new portal to list and write to file
	mapdata.portals.append(Portal(X1, Y1, X2, Y2))
	mapdata.portalsNum = mapdata.portalsNum + 1
	writeToFile()

	return

#adding cemetary
def addCemetary():
	#getting map size of cemetary
	flag = True
	while (flag == True):
		#prompt user instructions
		print("Go to cemetary town.")
		print("Put minimap on the very top left corner without anything obstructing it.")
		choice = input("Is it ready? (y/n): ")

		#user input checking
		while (choice != "y" and choice != "n"):
			choice = input("Enter a valid option: ")

		#find dimensions of cemetary map
		if (choice == "y"):
			flag = False
			#checking max x
			im = pyautogui.screenshot()
			rBorder = [221, 221, 221]
			for x in range(9, 600):
				pixel = im.getpixel((x, 74))
				#pixel = pyautogui.pixel(x, 74)
				if(pixel[0] == rBorder[0] and pixel[1] == rBorder[1] and pixel[2] == rBorder[2]):
					pixel1 = im.getpixel((x + 1, 74))
					if(pixel1[0] == rBorder[0] and pixel1[1] == rBorder[1] and pixel1[2] == rBorder[2]):
						pixel1 = im.getpixel((x, 75))
						if(pixel1[0] == rBorder[0] and pixel1[1] == rBorder[1] and pixel1[2] == rBorder[2]):
							pixel1 = im.getpixel((x + 1, 75))
							if(pixel1[0] == rBorder[0] and pixel1[1] == rBorder[1] and pixel1[2] == rBorder[2]):
								mapdata.cem_maxX = x - 1
								break

			#checking max y
			bBorder = [255, 255, 255]
			for y in range(61, 500):
				pixel = im.getpixel((65, y))
				if(pixel[0] == bBorder[0] and pixel[1] == bBorder[1] and pixel[2] == bBorder[2]):
					pixel1 = im.getpixel((65, y + 1))
					if(pixel1[0] == bBorder[0] and pixel1[1] == bBorder[1] and pixel1[2] == bBorder[2]):
						pixel = im.getpixel((66, y))
						if(pixel[0] == bBorder[0] and pixel[1] == bBorder[1] and pixel[2] == bBorder[2]):
							pixel1 = im.getpixel((66, y + 1))
							if(pixel1[0] == bBorder[0] and pixel1[1] == bBorder[1] and pixel1[2] == bBorder[2]):
								mapdata.cem_maxY = y - 1
								break

			#calculating width and height
			mapdata.cem_width = mapdata.cem_maxX - mapdata.minX
			mapdata.cem_height = mapdata.cem_maxY - mapdata.minY

	flag = True
	while (flag == True):
		print("Open up the map and place cursor on map point.")
		choice = input("You will have 2 seconds to tab into the game. Are you ready to start? (y/n): ")

		#user input checking
		while (choice != "y" and choice != "n"):
			choice = input("Enter a valid option: ")

		#find dimensions of cemetary map
		if (choice == "y"):
			flag = False
			time.sleep(2)
			maindir = os.path.dirname(__file__)
			assetsdir = os.path.join(maindir, "assets")
			navigationMarker = os.path.join(assetsdir, "navigation.png")
			navPos = pyautogui.locate(navigationMarker, pyautogui.screenshot())
			x, y = win32api.GetCursorPos()
			mapdata.map_coordX = x - navPos[0]
			mapdata.map_coordY = y - navPos[1]

	writeToFile()
	return

#getting mini map dimensions
def getMapSize():
	#checking max x
	im = pyautogui.screenshot()
	rBorder = [221, 221, 221]
	for x in range(9, 600):
		pixel = im.getpixel((x, 74))
		#pixel = pyautogui.pixel(x, 74)
		if(pixel[0] == rBorder[0] and pixel[1] == rBorder[1] and pixel[2] == rBorder[2]):
			pixel1 = im.getpixel((x + 1, 74))
			if(pixel1[0] == rBorder[0] and pixel1[1] == rBorder[1] and pixel1[2] == rBorder[2]):
				pixel1 = im.getpixel((x, 75))
				if(pixel1[0] == rBorder[0] and pixel1[1] == rBorder[1] and pixel1[2] == rBorder[2]):
					pixel1 = im.getpixel((x + 1, 75))
					if(pixel1[0] == rBorder[0] and pixel1[1] == rBorder[1] and pixel1[2] == rBorder[2]):
						mapdata.maxX = x - 1
						break

	#checking max y
	bBorder = [255, 255, 255]
	for y in range(61, 500):
		pixel = im.getpixel((65, y))
		if(pixel[0] == bBorder[0] and pixel[1] == bBorder[1] and pixel[2] == bBorder[2]):
			pixel1 = im.getpixel((65, y + 1))
			if(pixel1[0] == bBorder[0] and pixel1[1] == bBorder[1] and pixel1[2] == bBorder[2]):
				pixel = im.getpixel((66, y))
				if(pixel[0] == bBorder[0] and pixel[1] == bBorder[1] and pixel[2] == bBorder[2]):
					pixel1 = im.getpixel((66, y + 1))
					if(pixel1[0] == bBorder[0] and pixel1[1] == bBorder[1] and pixel1[2] == bBorder[2]):
						mapdata.maxY = y - 1
						break

	#calculating width and height
	mapdata.width = mapdata.maxX - mapdata.minX
	mapdata.height = mapdata.maxY - mapdata.minY

	return

#getting character position on minimapdata
def characterPos():
	charLoc = pyautogui.locate(charMarker, pyautogui.screenshot(region=(mapdata.minX, mapdata.minY, mapdata.width, mapdata.height)))
	while (charLoc == None):
		charLoc = pyautogui.locate(charMarker, pyautogui.screenshot(region=(mapdata.minX, mapdata.minY, mapdata.width, mapdata.height)))

	return charLoc

#main function
def main():
	#setting global directory pats
	global maindir
	global mapdir
	global assets

	maindir = os.path.dirname(__file__)
	mapdir = os.path.join(maindir, "map data")
	assetsdir = os.path.join(maindir, "assets")

	#initializing global MapData class
	global mapdata
	mapdata = MapData()

	#initializing global character marker
	global charMarker
	charMarker = os.path.join(assetsdir, "characterminimap.png")

	#prompting user with menu
	while(True):
		menu()

	return

main()