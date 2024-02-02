import pyautogui
import time

# Set up pyautogui
pyautogui.PAUSE = 0.5

# Open Chrome via Spotlight search
pyautogui.hotkey('command', 'space', interval=0.25)
time.sleep(0.5)
pyautogui.write('Google Chrome')
time.sleep(0.5)
pyautogui.press('enter')

# Wait for Chrome to open
time.sleep(3)

# Navigate to the desired website
pyautogui.write('https://ny.wynnbet.com/sportsbook')
pyautogui.press('enter')

# Give some time for the website to load
time.sleep(5)

# Locate the NFL button using a screenshot
x, y = pyautogui.locateCenterOnScreen('nfl_button.png')
if x and y:
    # Click the button if found
    pyautogui.click(x, y)
else:
    print("Couldn't find the NFL button on the screen.")
