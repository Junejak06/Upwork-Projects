#!/usr/bin/env python
# coding: utf-8

# In[1]:


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

def pin_extension():
    pyautogui.moveTo(1690, 66, duration=0.7)
    pyautogui.click()
    pyautogui.moveTo(1613, 248, duration=0.7)
    pyautogui.click()
def search_img_from_extension(url):
    pyautogui.moveTo(1652, 66, duration=0.7)
    pyautogui.click()
    pyautogui.moveTo(1411, 194, duration=0.7)
    pyautogui.click()
    pyperclip.copy(str(url))
    pyautogui.hotkey('command', 'v')  # Select all (Ctrl + A)
    pyautogui.press('enter')
    pyautogui.moveTo(1603, 193, duration=0.7)
    pyautogui.click()
    
def close_tab():
    pyautogui.moveTo(588, 17, duration=0.7)
    pyautogui.click()
# Function to extract and join the matches
def extract_numbers_and_dot(input_str):
    return ''.join(re.findall(pattern, input_str))
    
def get_data_from_aliexpress( img_url):
    title, price, star_number, review_number, sold_number, shipping_price, main_url = "",0,0,0,0,0, ""
    html_text = driver.page_source
    soup = BeautifulSoup(html_text, 'html.parser')
    pdp_info_right = soup.find("div", class_="pdp-info-right")
    if pdp_info_right:
        title_div = pdp_info_right.find("h1")
        if title_div:
            title = title_div.text
        price_div = pdp_info_right.find('div', class_=lambda value: value and 'product-price-current' in value)
        if price_div:
            price = price_div.text
    target_div = soup.find('div', {'data-pl': 'product-reviewer'})
    if target_div:
        stars_div = target_div.find('strong')
        if stars_div:
            star_number = stars_div.text.strip()

        for element in target_div.find_all(True):
        # Check if "Reviews" string is present in the element's text
            if "Reviews" in element.get_text():
                reviews = element.text.strip()
                pattern = r"[\d]"
                review_number = int(extract_numbers_and_dot(reviews))
            elif "Sold" in element.get_text():
                sold = element.text.strip()
                pattern = r"[\d]"
                sold_number = int(extract_numbers_and_dot(sold))
    right_section = soup.find("div", class_="pdp-body-right")
    if right_section:
        for element in right_section.find_all(True):
        # Check if "Reviews" string is present in the element's text
            if "Free Shipping" in element.get_text():
                shipping_price = 0 
            elif "Shipping" in element.get_text():
                Shipping = element.text.strip()
                pattern = r"[\d.]"
                shipping_price = extract_numbers_and_dot(Shipping)
    main_url = driver.current_url
    dictionary = {
        "title":title, 
        "price":price, 
        "star_number":star_number, 
        "review_number":review_number, 
        "sold_number":sold_number, 
        "shipping_price":shipping_price, 
        "main_url":main_url, 
        "img_url":img_url     
    }
    return dictionary


# In[4]:


pin_extension()


# In[7]:


df = pd.read_csv('temu_filtered_products4400.csv')
urls = df['Product Image URL'].tolist()


# In[168]:


result_highest_raiting = []
result_cheapest_price = []
for img_url in urls[:2]:
    search_img_from_extension(img_url)
    time.sleep(70)
    driver.switch_to.window(driver.window_handles[-1])
    html_text = driver.page_source
    soup = BeautifulSoup(html_text, 'html.parser')
    product_divs = soup.find_all("div", class_="product-list-item grid")
    search_result_product = []
    for product_div in product_divs:
        price = product_div.find("span", class_="product-price-price").text
        pattern = r"[\d.]"
        cleaned_price = float(extract_numbers_and_dot(price))
        raiting_div = product_div.find("div", class_="rating")
        if raiting_div:
            try:
                raiting = float(raiting_div.text)
            except:
                raiting = 0
        else:
            raiting = 0

        url = product_div.find("a")["href"]
        search_result_product.append({
                "price" : cleaned_price,
                "raiting" : raiting,
                "url" : url
            })
    highest_raiting_item = max(search_result_product, key=lambda x: x['raiting'])
    cheapest_price_item = min(search_result_product, key=lambda x: x['price'])
    highest_raiting_url = highest_raiting_item['url']
    cheapest_price_url = cheapest_price_item['url']
    
    driver.get(highest_raiting_url)
    time.sleep(70)
    result_highest = get_data_from_aliexpress( img_url)
    result_highest_raiting.append(result_highest)
    driver.get(cheapest_price_url)
    time.sleep(70)
    result_cheapest = get_data_from_aliexpress( img_url)
    result_cheapest_price.append(result_cheapest)
    close_tab()
    driver.switch_to.window(driver.window_handles[0])
    


# In[32]:


highest_df = pd.DataFrame(result_highest_raiting)
cheapest_df = pd.DataFrame(result_cheapest_price)


# In[33]:


highest_df.to_excel("aliexperss_highest_df.xlsx")
cheapest_df.to_excel("aliexperss_cheapest_df.xlsx")


# In[ ]:




