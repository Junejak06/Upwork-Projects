import pandas as pd
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
import ssl
import os
import openpyxl

# For SSL issue
ssl._create_default_https_context = ssl._create_unverified_context

options = uc.ChromeOptions()
options.binary_location = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
driver = uc.Chrome(driver_executable_path=r"/usr/local/bin/chromedriver", options=options)

# Read the CSV file
df = pd.read_csv('sp500_forecasts.csv')

# Function to scrape Yahoo Finance data using Selenium
def scrape_yahoo_finance(symbol):
    try:
        driver.get(f"https://finance.yahoo.com/quote/{symbol}?p={symbol}&.tsrc=fin-srch")
        time.sleep(2)  # Allow time for the page to load

        # Scrape P/E Ratio
        pe_element = driver.find_element(By.XPATH, "//td[span='PE Ratio (TTM)']/following-sibling::td")
        pe_ratio = pe_element.text.strip()

        # Scrape EPS
        eps_element = driver.find_element(By.XPATH, "//td[span='EPS (TTM)']/following-sibling::td")
        eps = eps_element.text.strip()

        return pe_ratio, eps
    except (NoSuchElementException, TimeoutException) as e:
        print(f"Error scraping data for {symbol}: {e}")
        return None, None

# Function to convert percentage to decimal and handle negative values
def convert_to_decimal(percentage_string):
    if percentage_string == 'N/A':
        return 0
    return float(percentage_string.strip('+%')) / 100

# Function to calculate intrinsic value using EPS, P/E, and growth rate
def calculate_intrinsic_value(eps, pe_ratio, median_estimate):
    try:
        if eps == 'N/A' or pe_ratio == 'N/A':
            return 'N/A'
        growth_rate = convert_to_decimal(median_estimate)
        return float(eps) * (1 + growth_rate) * float(pe_ratio)
    except Exception as e:
        print(f"Error calculating intrinsic value: {e}")
        return 'N/A'

# Add new columns to DataFrame
df['P/E'] = ''
df['EPS'] = ''
df['Intrinsic Value'] = ''

# Iterate over stock symbols and scrape data
for index, row in df.iterrows():
    symbol = row['Symbol']
    median_estimate = row['Median Estimate']
    pe, eps = scrape_yahoo_finance(symbol)
    if pe and eps:
        df.at[index, 'P/E'] = pe
        df.at[index, 'EPS'] = eps
        intrinsic_value = calculate_intrinsic_value(eps, pe, median_estimate)
        df.at[index, 'Intrinsic Value'] = intrinsic_value
        print(f"Symbol: {symbol}, P/E Ratio: {pe}, EPS: {eps}, Intrinsic Value: {intrinsic_value}")

# Close the browser
driver.quit()

# Save the updated DataFrame to a new CSV file
df.to_csv('updated_sp500_forecasts.csv', index=False)
