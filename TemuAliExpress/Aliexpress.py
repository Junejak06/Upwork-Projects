
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


def accept_cookies(driver):
    try:
        cookies_popup = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//div[@class='at-widgets-panel at-widgets-history']//div[@class='at-widgets-panel__content at-widgets-panel__content--radius-left']"))
        )
        cookies_popup.click()
    except TimeoutException:
        print("No cookies popup found")

def allow_permissions(driver):
    try:
        allow_button = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//div[@class=' _1-SOk']"))
        )
        allow_button.click()
    except TimeoutException:
        print("No permissions popup found")

options = uc.ChromeOptions()
options.binary_location = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
extension_path = 'AliExpressSearch' # Replace with the actual path to your .crx file
options.add_argument(f'--load-extension={extension_path}')
driver = uc.Chrome(driver_executable_path=r"/usr/local/bin/chromedriver", options=options)

def scroll_up_for_seconds(seconds=3):
    end_time = time.time() + seconds  # Calculate end time
    while time.time() < end_time:  # Keep scrolling until end_time
        pyautogui.scroll(1)  # 1 indicates scroll up; use a higher value for faster scrolling
        time.sleep(0.1)  # Pause slightly between scrolls to control speed and duration
wait = WebDriverWait(driver, 3)

def move_mouse_to(x, y):
    """
    Move the mouse to the specified coordinates.

    :param x: int, x-coordinate
    :param y: int, y-coordinate
    """
    pyautogui.moveTo(x, y)

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
time.sleep(1)

# Click on the input field.
pyautogui.click(919.9638061523438, 184.40335083007812)

# Use hotkey to paste (Command+V for macOS, Ctrl+V for Windows/Linux).
pyautogui.hotkey('command', 'v' ,interval = 0.25)  # Use 'ctrl' instead of 'command' for Windows/Linux

# Press 'enter' to navigate to the URL.
pyautogui.press('enter')
# Wait for a moment.
time.sleep(1)

# Click to initiate the search or another action.
pyautogui.click(1264.200439453125, 182.48744201660156)

time.sleep(7)


# Coordinates should be set based on where the right-click should happen
x, y = 327.38531494140625, 808.716064453125 # Replace with actual x, y coordinates

# Right-click
pyautogui.rightClick(x, y)

for _ in range(13):  # Adjusting the range as per your requirement
    pyautogui.press('down')
    #time.sleep(0.1)  # A short pause between each down press to ensure it registers
pyautogui.press('enter')

# Pause to ensure the source code page opens
time.sleep(5)

move_mouse_to(924.4344482421875, 164.0634002685547)

scroll_up_for_seconds(3)

pyautogui.rightClick(924.4344482421875, 164.0634002685547)

for _ in range(2):  # Adjusting the range as per your requirement
    pyautogui.press('down')
    time.sleep(0.1)  # A short pause between each down press to ensure it registers
pyautogui.press('enter')

time.sleep(2)

# Copy all content (Command+A and Command+C) with a small pause between
pyautogui.hotkey('command', 'a' ,interval=0.25)

pyautogui.hotkey('command', 'c' ,interval=0.25)
 # interval to make sure the copy operation is complete
time.sleep(1)
# Get copied content and parse it
page_source = pyperclip.paste()
soup = BeautifulSoup(page_source, 'html.parser')
# Instead of directly opening the links, store them first

links_to_open = []

# Extract prices and find the cheapest
prices_elements = soup.find_all('span', class_='product-price-price')
prices = [float(el.get_text().replace('US $', '')) for el in prices_elements]

prices_elements = soup.find_all('span', class_='product-price-price')
prices = [(float(el.get_text().replace('US $', '')), el) for el in prices_elements]

try:
    cheapest = min(prices, key=lambda x: x[0])
    cheapest_price = cheapest[0]
    cheapest_price_el = cheapest[1]
    
    print(f"Cheapest price: US ${cheapest_price:.2f}")

    # Finding a preceding link
    preceding_el = cheapest_price_el.find_previous('a', href=True)
    if preceding_el:
        cheapest_link = preceding_el['href']
        links_to_open.append(cheapest_link)
    else:
        print("Couldn't find a link corresponding to the cheapest price.")
except ValueError:
    print("No valid prices found.")
except Exception as e:
    print(f"An error occurred: {str(e)}")

# Extract ratings and find the highest
ratings_elements = soup.find_all('div', class_='rating')  # Replace 'rating' with actual class name
ratings = [(float(el.get_text()), el) for el in ratings_elements]

try:
    highest_rating = max(ratings, key=lambda x: x[0])
    highest_rating_value = highest_rating[0]
    highest_rating_el = highest_rating[1]
    
    print(f"Highest rating: {highest_rating_value}")

    # Finding a preceding link
    preceding_el = highest_rating_el.find_previous('a', href=True)
    if preceding_el:
        highest_rating_link = preceding_el['href']
        links_to_open.append(highest_rating_link)
    else:
        print("Couldn't find a link corresponding to the highest rating.")
except ValueError:
    print("No valid ratings found.")
except Exception as e:
    print(f"An error occurred: {str(e)}")

# Now open and process each link:
for link in links_to_open:
    # Open a new tab
    driver.execute_script("window.open('');")
    
    # Switch to the new tab (it's always the last one)
    driver.switch_to.window(driver.window_handles[-1])
    
    # Load the link in the new tab
    driver.get(link)
    time.sleep(7)
    
    # Handle popups
    accept_cookies(driver)
    allow_permissions(driver)

    time.sleep(3)

driver.close()