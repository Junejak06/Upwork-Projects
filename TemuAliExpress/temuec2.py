import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from undetected_chromedriver import Chrome
from selenium.webdriver.chrome.options import Options
import re
import os



# File path for CSV on EC2
file_path = "/home/ubuntu/temu_filtered_products.csv"



# Remove old CSV if it exists
if os.path.exists(file_path):
    os.remove(file_path)

def append_to_csv(data, file_name):
    """Append data to a CSV file"""
    df = pd.DataFrame(data, columns=['Product Name', 'Product Price', 'Product Rating', 'Number of Reviews', 'Product Units Sold', 'Product Category', 'Product URL', 'Product Image URL'])
    df.to_csv(file_name, mode='a', index=False, header=not os.path.isfile(file_name))

# Set up Chrome options for headless mode and other required arguments for EC2
chrome_options = Options()
chrome_options.headless = False
chrome_options.binary_location = "/usr/bin/google-chrome-stable"

# Create a Chrome driver instance with the specified options
driver = Chrome(options=chrome_options)




wait = WebDriverWait(driver, 10)

driver.get("https://www.temu.com/channel/best-sellers.html?filter_items=1%3A1&scene=home_title_bar_recommend&refer_page_el_sn=201341&_x_sessn_id=jhcuhnhlbr&refer_page_name=5-Star%20Rated&refer_page_id=10443_1696611819011_q95oaps8cl&refer_page_sn=10443")

element = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//li[@id='splide01-slide02']//div[@class='_3FT75RMj']"))
)
element.click()

products = []
#processed_urls = set()
batch_size = 100  # Adjust this as needed

last_scraped_count = 0

while len(products) < 5000:
    product_elems = driver.find_elements(By.XPATH, "//div[@aria-label]")
    current_product_count = len(product_elems)
    
    for idx in range(last_scraped_count, current_product_count):
        product = product_elems[idx]
        
        # Get rating
        rating_elems = product.find_elements(By.XPATH, ".//div[contains(@aria-label, 'score')]")
        rating = float(rating_elems[0].get_attribute('aria-label').split(' ')[0]) if rating_elems else 0

        # Get number of reviews
        review_elems = product.find_elements(By.XPATH, ".//span[@class='_2W4Cqryh']")
        reviews = int(re.sub(r'[^\d]', '', review_elems[0].text)) if review_elems else 0

        # Filter out products that don't meet the criteria
        if rating < 4.5 or reviews <= 5000:
            continue

        # Get product name, price, units sold
        name = product.find_element(By.XPATH, ".//h3[@class='_2XmIMTf3']").text
        price = product.find_element(By.XPATH, ".//div[@class='_2Ci4uR69']").text
        units_sold_elems = product.find_elements(By.XPATH, ".//span[@class='EPO3q5u9']")
        units_sold = units_sold_elems[0].text if units_sold_elems else '0'

        # Get product URL
        try:
            product_url_elem = product.find_element(By.TAG_NAME, "a")
            product_url = product_url_elem.get_attribute('href')
        except NoSuchElementException:
            product_url = ''

        # Get product image
        try:
            image_elem = product.find_element(By.XPATH, ".//img")
            image_url = image_elem.get_attribute('src') or image_elem.get_attribute('data-src')
        except NoSuchElementException:
            image_url = ''

        # Get product category using JavaScript and try-except block
        try:
            category_script = "return arguments[0].innerText.trim().replace('in ', '');"
            category = driver.execute_script(category_script, product.find_element(By.XPATH, ".//div[@class='_2OyM96Bd']"))
        except NoSuchElementException:
            category = ''

        products.append([name, price, rating, reviews, units_sold, category, product_url, image_url])

        # Print the details of the product
        print(f"Product Name: {name}")
        print(f"Product Price: {price}")
        print(f"Product Rating: {rating}")
        print(f"Number of Reviews: {reviews}")
        print(f"Product Units Sold: {units_sold}")
        print(f"Product Category: {category}")
        print(f"Product URL: {product_url}")
        print(f"Product Image URL: {image_url}")
        print("-" * 50)

        if len(products) >= batch_size:
            append_to_csv(products, "temu_filtered_products.csv")
            products.clear()

        if len(products) >= 5000:
            break

    # Update the last_scraped_count for the next iteration
    last_scraped_count = current_product_count

    # Attempt to click the "See More" button (up to two times)
    see_more_attempts = 0
    while see_more_attempts < 2:
        try:
            see_more_btn = driver.find_element(By.XPATH, "//div[@class='_2U9ov4XG']")
            see_more_btn.click()
            time.sleep(2)
            break
        except NoSuchElementException:
            see_more_attempts += 1
            time.sleep(2)

df = pd.DataFrame(products, columns=['Product Name', 'Product Price', 'Product Rating', 'Number of Reviews', 'Product Units Sold', 'Product Category', 'Product URL', 'Product Image URL'])
df.to_csv("temu_filtered_products.csv", index=False)

display.stop()
driver.quit()