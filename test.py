import keyboard
import time

def main():
	while(True):
		press('Q')
		time.sleep(3)
		print("LOOP")

def press(key):
	keyboard.press(key)
	time.sleep(0.05)
	keyboard.release(key)

main()