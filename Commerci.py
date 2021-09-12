import sys
import os
import pyautogui
import keyboard
import win32api, win32con
import time

def main():
	while(True):
		press('A')
		time.sleep(1)
		keyboard.press('Left')
		time.sleep(0.2)
		keyboard.release('Left')
		time.sleep(0.1)
		press('A')
		time.sleep(1)
		keyboard.press('Right')
		time.sleep(0.2)
		keyboard.release('Right')
		time.sleep(0.1)


#function to press a key
def press(key):
	keyboard.press(key)
	time.sleep(0.05)
	keyboard.release(key)

main()