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
import requests
import re
import os

# For SSL issue
ssl._create_default_https_context = ssl._create_unverified_context

def create_new_driver():
    options = uc.ChromeOptions()
    options.binary_location = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    driver = uc.Chrome(driver_executable_path=r"/usr/local/bin/chromedriver", options=options)
    return driver

def get_zip_codes_from_file(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip()]
def handle_captcha():
    try:
        # Adjust this locator if needed to properly detect CAPTCHA on your target site
        captcha_element = driver.find_element(By.ID, 'captchaForm')
        if captcha_element:
            print("CAPTCHA detected. Please solve it manually in the browser and press Enter to continue.")
            input()  # Wait for user to hit Enter after solving CAPTCHA
    except NoSuchElementException:
        pass  # CAPTCHA not detected


#options = uc.ChromeOptions()
#options.binary_location = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
#driver = uc.Chrome(driver_executable_path=r"/usr/local/bin/chromedriver", options=options)
#options.add_argument(f"user-agent={user_agent}")
# Navigate to the website
# Read zip codes from a txt file
zip_codes = get_zip_codes_from_file(
    'zipcode.txt')  # Ensure this file exists in the same directory with one zip code per line

all_data = []

for zip_code in zip_codes:
    driver = create_new_driver()
    driver.get("https://kbopub.economie.fgov.be/kbopub/zoekactiviteitform.html")
    time.sleep(2)

    # Enter NACE code
    nace_code_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@id='nacecodes']"))
    )
    nace_code_input.send_keys("56301")  # Replace with your NACE code

    # Click on the radio button
    radio_button = driver.find_element(By.XPATH, "//input[@id='post']")
    radio_button.click()

    # Enter the zip code
    zip_code_input = driver.find_element(By.XPATH, "//input[@id='postnummer1']")
    zip_code_input.send_keys(zip_code)

    # Click on the search button
    search_button = driver.find_element(By.XPATH, "//input[@name='actionLu']")
    search_button.click()

    while True:
        handle_captcha()
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table = soup.find('table', {'id': 'activiteitlist'})
        rows = table.tbody.find_all('tr')

        for row in rows:
            ondernemingsnummer = row.find('a', href=True).text.strip()
            link = "https://kbopub.economie.fgov.be/kbopub/" + row.find('a', href=True)['href']
            naam = row.find('td', {'class': 'benaming'}).get_text(strip=True)
            adres = row.find('td', {'class': 'nowrap'}).get_text(strip=True, separator=' ')
            all_data.append((ondernemingsnummer, naam, adres))

        try:
            next_button = driver.find_element(By.XPATH, "//span[@class='pagelinks']/a[text()='Volgende']")
            next_button.click()
            time.sleep(2)
            handle_captcha()
        except NoSuchElementException:
            break

    driver.quit()

df = pd.DataFrame(all_data, columns=['Ondernemingsnummer', 'Naam', 'Adres'])
df.to_excel("output 10.xlsx", index=False)



