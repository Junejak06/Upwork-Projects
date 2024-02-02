import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import undetected_chromedriver as uc
import ssl
import re
import os

# For SSL issue
ssl._create_default_https_context = ssl._create_unverified_context

options = uc.ChromeOptions()
options.binary_location = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
driver = uc.Chrome(driver_executable_path=r"/usr/local/bin/chromedriver", options=options)

# Set up the DataFrame to store categories and subcategories
data = pd.DataFrame(columns=["Category", "Sub Category"])

# Define URL
url = "https://www.temu.com/channel/best-sellers.html?filter_items=1%3A1&scene=home_title_bar_recommend&refer_page_el_sn=201341&_x_sessn_id=jhcuhnhlbr&refer_page_name=5-Star%20Rated&refer_page_id=10443_1696611819011_q95oaps8cl&refer_page_sn=10443"

try:
    # Open the website
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    
    # Click on the specified element
    element_to_click = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@class='KKUw6o-W pWw9Mlj4']")))
    element_to_click.click()
    
    # Wait for the page to load (adjust time accordingly)
    time.sleep(5)  
    
    # Extract categories
    categories = driver.find_elements(By.XPATH, "//a[@class='_3VEjS46S _2bnUWSV9 _1EgFSCGE']")[1:]  # skipping the first category
    
    # Iterate over categories
    for category in categories:
        category_name = category.text
        category.click()  # click to reveal subcategories
        time.sleep(2)  # wait for subcategories to load
        
        # Extract subcategories
        subcategories = driver.find_elements(By.XPATH, "//div[@class='_2ydisBcI _4SDhTEck']//div")
        
        # Iterate over subcategories
        for subcategory in subcategories:
            subcategory_name = subcategory.get_attribute("title")
            if subcategory_name:  # check if title attribute is not None
                # Append to the DataFrame
                data = data.append({
                    "Category": category_name,
                    "Sub Category": subcategory_name
                }, ignore_index=True)
        # Navigate back if needed
        # driver.back()
        time.sleep(2)
    
    # Save to CSV
    data.to_csv("categories_subcategories.csv", index=False)
    
except Exception as e:
    print("An error occurred:", str(e))

finally:
    # Close the browser
    driver.quit()
