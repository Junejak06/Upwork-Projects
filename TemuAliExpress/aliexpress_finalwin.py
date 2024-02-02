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
options.headless = False
#options.binary_location = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
extension_path = r'C:\Users\Administrator\Desktop\TemuAliExpress\AliExpressSearch' # Replace with the actual path to your .crx file
options.add_argument(f'--load-extension={extension_path}')
driver = uc.Chrome(options=options)

# Maximize the browser window
driver.maximize_window()

def pin_extension():
    pyautogui.moveTo(1308, 57, duration=0.7)
    pyautogui.click()
    pyautogui.moveTo(1247, 204, duration=0.7)
    pyautogui.click()

def search_img_from_extension(url):
    pyautogui.moveTo(1270, 55, duration=0.7)
    pyautogui.click()
    pyautogui.moveTo(1107, 154, duration=0.7)
    pyautogui.click()
    pyperclip.copy(str(url))
    pyautogui.hotkey('ctrl', 'v')  # Select all (Ctrl + A)
    pyautogui.press('enter')
    pyautogui.moveTo(1251, 159, duration=0.7)
    pyautogui.click()

def close_tab():
    pyautogui.moveTo(471, 18, duration=0.7)
    pyautogui.click()

# Function to extract and join the matches
def extract_numbers_and_dot(input_str):
    return ''.join(re.findall(pattern, input_str))

def get_data_from_aliexpress(img_url):
    title, price, star_number, review_number, sold_number, shipping_price, main_url = "", 0, 0, 0, 0, 0, ""
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
        "title": title,
        "price": price,
        "star_number": star_number,
        "review_number": review_number,
        "sold_number": sold_number,
        "shipping_price": shipping_price,
        "main_url": main_url,
        "img_url": img_url
    }
    return dictionary

pin_extension()

df = pd.read_csv('temu_filtered_products4400.csv')
urls = df['Product Image URL'].tolist()

result_highest_raiting = []
result_cheapest_price = []
max_attempts = 2  # Maximum number of attempts to retrieve highest rating

for img_url in urls[:5]:
    search_img_from_extension(img_url)
    time.sleep(8)
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
            "price": cleaned_price,
            "raiting": raiting,
            "url": url
        })

    highest_raiting_item = None
    cheapest_price_item = None
    attempts = 0

    while attempts < max_attempts:
        try:
            highest_raiting_item = max(search_result_product, key=lambda x: x['raiting'])
            cheapest_price_item = min(search_result_product, key=lambda x: x['price'])
            break
        except ValueError as e:
            print(f"Error: {e}")
            print("Retrying to retrieve highest rating and cheapest price...")
            time.sleep(3)  # Wait for a moment before retrying
            attempts += 1

    if highest_raiting_item:
        highest_raiting_url = highest_raiting_item['url']
        driver.get(highest_raiting_url)
        time.sleep(3)
        result_highest = get_data_from_aliexpress(img_url)
        result_highest_raiting.append(result_highest)

    if cheapest_price_item:
        cheapest_price_url = cheapest_price_item['url']
        driver.get(cheapest_price_url)
        time.sleep(3)
        result_cheapest = get_data_from_aliexpress(img_url)
        result_cheapest_price.append(result_cheapest)

    # Before starting the loop:
    if not os.path.exists('highest_raiting_scraped_data.csv'):
        pd.DataFrame(columns=["title", "price", "star_number", "review_number", "sold_number", "shipping_price", "main_url", "img_url"]).to_csv('highest_raiting_scraped_data.csv', index=False)

    if not os.path.exists('cheapest_price_scraped_data.csv'):
        pd.DataFrame(columns=["title", "price", "star_number", "review_number", "sold_number", "shipping_price", "main_url", "img_url"]).to_csv('cheapest_price_scraped_data.csv', index=False)

    # Inside the loop after fetching data:

    if highest_raiting_item:
        highest_raiting_url = highest_raiting_item['url']
        driver.get(highest_raiting_url)
        time.sleep(3)
        result_highest = get_data_from_aliexpress(img_url)
        # Save the new result to CSV after each scrape
        highest_df = pd.DataFrame([result_highest])
        highest_df.to_csv('highest_raiting_scraped_data.csv', mode='a', header=False, index=False)
        result_highest_raiting.append(result_highest)

    if cheapest_price_item:
        cheapest_price_url = cheapest_price_item['url']
        driver.get(cheapest_price_url)
        time.sleep(3)
        result_cheapest = get_data_from_aliexpress(img_url)
        # Save the new result to CSV after each scrape
        cheapest_df = pd.DataFrame([result_cheapest])
        cheapest_df.to_csv('cheapest_price_scraped_data.csv', mode='a', header=False, index=False)
        result_cheapest_price.append(result_cheapest)

    close_tab()
    driver.switch_to.window(driver.window_handles[0])
# Rest of your code...
