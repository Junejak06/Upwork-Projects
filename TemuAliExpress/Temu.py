import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import ssl
from selenium.common.exceptions import NoSuchElementException
import re

# For SSL issue
ssl._create_default_https_context = ssl._create_unverified_context

options = uc.ChromeOptions()
options.headless = False

options.binary_location = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
driver = uc.Chrome(driver_executable_path=r"/usr/local/bin/chromedriver", options=options)

wait = WebDriverWait(driver, 10)  # Setting up a default wait time of 10 seconds

def append_to_csv(data, filename):
    # Convert the list of data to a DataFrame
    df = pd.DataFrame(data, columns=['Product Name', 'Product Price', 'Product Rating', 'Number of Reviews', 'Product Units Sold', 'Product Category', 'Product URL', 'Product Image URL'])
    
    # Append to CSV, without writing the header if the file already exists
    df.to_csv(filename, mode='a', header=not pd.io.common.file_exists(filename), index=False)

driver.get("https://www.temu.com/")


# XPath for the 'Best Sellers' link
best_sellers_xpath = "//span[@title='Best Sellers']"

# Click on the 'Best Sellers' link
driver.find_element(By.XPATH, best_sellers_xpath).click()

# Wait for the next page to load or for subsequent actions
time.sleep(5)

driver.find_element(By.XPATH, "//li[@id='splide01-slide02']//div[@class='_3FT75RMj']").click()

# Wait for 10 seconds to allow the page to load or for the next actions to be ready
time.sleep(5)

products = []
#processed_urls = set()
batch_size = 100  # Adjust this as needed

last_scraped_count = 0

while len(products) < 200:
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
            # Find the element
            category_elem = product.find_element(By.XPATH, ".//div[@class='_2OyM96Bd']")

            # Execute JavaScript to get the inner text of the element directly
            category = driver.execute_script("return arguments[0].innerText;", category_elem)
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
            append_to_csv(products, "temu_200.csv")
            products.clear()

        if len(products) >= 200:
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
df.to_csv("temu_200.csv", index=False)

driver.quit()
