import sys
import os
import pyautogui
import keyboard
import time

def main():
	key = input("Enter key to hold down: ")
	time.sleep(2)
	while (True):
		keyboard.press(key)
		time.sleep(0.05)
		keyboard.release(key)

main()