import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pyperclip
import undetected_chromedriver as uc
import pyautogui
import ssl
import re
import os

# For SSL issue
ssl._create_default_https_context = ssl._create_unverified_context

options = uc.ChromeOptions()
options.binary_location = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
extension_path = 'AliExpressSearch' # Replace with the actual path to your .crx file
options.add_argument(f'--load-extension={extension_path}')
driver = uc.Chrome(driver_executable_path=r"/usr/local/bin/chromedriver", options=options)

wait = WebDriverWait(driver, 3)

#driver.get('https://img.kwcdn.com/product/Fancyalgo/VirtualModelMatting/e47d6545d8f1cfc990d317e543ce7a16.jpg?imageView2/2/w/500/q/80/format/webp')


# Wait for a few seconds to ensure the browser is fully loaded (you can adjust the sleep duration if needed)
time.sleep(3)

# Simulate the first click
pyautogui.click(1324.0390625, 91.52655029296875)

# Wait for a bit (optional, you can adjust or remove this sleep duration)
time.sleep(1)

# Simulate the second click
pyautogui.click(1156.6461181640625, 226.22933959960938)


# Load the Excel file using pandas.
df = pd.read_csv('temu_filtered_products4400.csv')
print(df.columns)

# Get the URLs from column H.
urls = df['Product Image URL'].tolist()
url_to_search = urls[0]

pyperclip.copy(url_to_search)

# Wait for a bit to ensure everything is ready.
time.sleep(2)

# Click on the input field.
pyautogui.click(919.9638061523438, 184.40335083007812)

# Use hotkey to paste (Command+V for macOS, Ctrl+V for Windows/Linux).
pyautogui.hotkey('command', 'v' ,interval = 0.25)  # Use 'ctrl' instead of 'command' for Windows/Linux

# Press 'enter' to navigate to the URL.
pyautogui.press('enter')
# Wait for a moment.
time.sleep(2)

# Click to initiate the search or another action.
pyautogui.click(1264.200439453125, 182.48744201660156)

time.sleep(120)