import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import ssl
import cv2
import numpy as np
import urllib.request
from PIL import Image
from io import BytesIO

# For SSL issue
ssl._create_default_https_context = ssl._create_unverified_context


options = uc.ChromeOptions()
options.binary_location = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
driver = uc.Chrome(driver_executable_path=r"/usr/local/bin/chromedriver", options=options)

# Go to the initial website
driver.get("https://property.singaporeexpats.com/")
time.sleep(5)  # give the page some time to load

# Click on the search button using its absolute XPath
search_button = driver.find_element(By.XPATH, "/html[1]/body[1]/div[2]/div[1]/div[1]/div[2]/div[2]/form[1]/div[1]/div[2]/div[2]/button[1]/i[1]")
search_button.click()
time.sleep(5)

# Find the image element and its URL
image_element = driver.find_element(By.CSS_SELECTOR, "img.lazyloaded")
image_url = image_element.get_attribute("src")

print(f"Image URL: {image_url}")

# Download the image using Pillow and convert to RGB
try:
    resp = urllib.request.urlopen(image_url)
    image_data = resp.read()
    pil_image = Image.open(BytesIO(image_data))
    
    # Convert to RGB before saving
    pil_image = pil_image.convert("RGB")
    pil_image.save("downloaded_image.jpg")
    
except Exception as e:
    print(f"Failed to download the image. Error: {e}")
    driver.quit()
    exit()

# Attempting watermark removal with a simple median blur. 
# Note: This is a basic method and might not work for all watermarks.
image_cv = cv2.imread("downloaded_image.jpg")
cleaned = cv2.medianBlur(image_cv, 5)
cv2.imwrite("cleaned_image.jpg", cleaned)

driver.quit()
