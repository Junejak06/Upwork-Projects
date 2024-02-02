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
import random

# For SSL issue
ssl._create_default_https_context = ssl._create_unverified_context

options = uc.ChromeOptions()
options.binary_location = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
driver = uc.Chrome(driver_executable_path=r"/usr/local/bin/chromedriver", options=options)

wait = WebDriverWait(driver, 10)
for _ in range(30):
    driver.get("https://www.vehicle-operator-licensing.service.gov.uk/view-details/licence/98731")
    
    # Wait for a random interval between 5 to 15 seconds
    time.sleep(random.uniform(5, 15))

