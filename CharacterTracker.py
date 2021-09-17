import pyautogui
import os



#getting character position on minimapdata
def characterPos():
	charLoc = pyautogui.locate(charMarker, pyautogui.screenshot(region=(9, 61, 500, 500)))

	return charLoc


def main():
	global charMarker
	maindir = os.path.dirname(__file__)
	assetsdir = os.path.join(maindir, "assets")
	charMarker = os.path.join(assetsdir, "characterminimap.png")


	while(True):
		input("Press enter to track character.")
		print(characterPos())

main()