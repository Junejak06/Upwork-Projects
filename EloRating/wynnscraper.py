import pyautogui
import time
import pyperclip
from bs4 import BeautifulSoup
import pandas as pd

# Set up pyautogui
pyautogui.PAUSE = 0.3

# Open Chrome via Spotlight search
pyautogui.hotkey('command', 'space', interval=0.25)
time.sleep(0.3)
pyautogui.write('Google Chrome')
time.sleep(0.3)
pyautogui.press('enter')

# Wait for Chrome to open
time.sleep(3)

# Navigate to the desired website
pyautogui.write('https://ny.wynnbet.com/competition/115')
pyautogui.press('enter')

# Give some time for the website to load
time.sleep(3)

# Right-click somewhere on the page to get the context menu
# Coordinates would vary based on your browser and screen resolution
pyautogui.click(500, 500, button='right')  
time.sleep(1)

# Press down arrow keys a certain number of times to reach "View Page Source"
# The exact number would vary based on your browser and its version
for _ in range(11):  # Assume "View Page Source" is the 10th option
    pyautogui.press('down')
    time.sleep(0.01)

pyautogui.press('enter')

# Allow page source to load
time.sleep(5)

# Select all
pyautogui.hotkey('command', 'a', interval=0.25)
time.sleep(0.5)

# Copy
pyautogui.hotkey('command', 'c', interval=0.25)
time.sleep(1)

# Extract data from clipboard
html_content = pyperclip.paste()

# Use BeautifulSoup to parse the content and get the URLs
soup = BeautifulSoup(html_content, 'html.parser')

base_url = 'https://ny.wynnbet.com'

# Find all links with the pattern "/event/<numbers>" and filter out the BYOB type
urls = [base_url + link.get('href') for link in soup.find_all('a', class_='eventItemName') if link.get('href') and '/event/' in link.get('href') and '?page-type=BYOB' not in link.get('href')]

# Deduplicate URLs since there might be repetitions
urls = list(set(urls))

# Print each URL on a new line
for url in urls:
    print(url)

# List to hold the final URLs
final_urls = []

# Convert the URLs list to a DataFrame
df = pd.DataFrame(urls, columns=['URL'])


# Function to check if the elements are present in the HTML content
def elements_present(html_content):
    required_elements = ["Passing", "Rushing", "Receiving"]
    return all(element in html_content for element in required_elements)

# Navigate to each URL, check the content, and generate the final URLs if the conditions are met
for _, row in df.iterrows():
    url = row['URL']
    
    # Open a new tab
    pyautogui.hotkey('command', 't', interval=0.25)
    time.sleep(3)  # Increased sleep time to ensure the browser is ready

    # Click on the address bar to ensure focus (coordinates may need adjustments)
    #pyautogui.click(300, 50)  # Assuming (300, 50) is roughly where the address bar is

    # Write the URL in the new tab and enter
    # Copy the URL to the clipboard
    pyperclip.copy(url)

    # Paste the URL from the clipboard
    pyautogui.hotkey('command', 'v')
    pyautogui.press('enter')
    time.sleep(3)

    # Retrieve the page source, same steps as before
    pyautogui.click(500, 500, button='right')
    time.sleep(1)
    for _ in range(11):
        pyautogui.press('down')
        time.sleep(0.01)
    pyautogui.press('enter')
    time.sleep(3)
    pyautogui.hotkey('command', 'a', interval=0.25)
    time.sleep(0.5)
    pyautogui.hotkey('command', 'c', interval=0.25)
    time.sleep(1)

    # Extract data from clipboard
    page_html_content = pyperclip.paste()

    # Check if all the required elements are present
    if elements_present(page_html_content):
        # Construct the new URLs and add them to the list
        final_urls.extend([url + "/passing?", url + "/rushing?", url + "/receiving?"])

    # Close the tab and move to the next URL
    pyautogui.hotkey('command', 'w', interval=0.25)
    time.sleep(1)

# Print the final URLs
for f_url in final_urls:
    print(f_url)
