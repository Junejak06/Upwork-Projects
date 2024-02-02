import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import undetected_chromedriver as uc
import ssl

# Handle SSL issues
ssl._create_default_https_context = ssl._create_unverified_context

# Read the Excel file
input_data = pd.read_excel("input.xlsx", usecols="I:Y")

options = uc.ChromeOptions()
options.binary_location = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
driver = uc.Chrome(driver_executable_path=r"/usr/local/bin/chromedriver", options=options)
wait = WebDriverWait(driver, 10)
all_data = []

driver.get("https://www.bizbuysell.com/")

# Close popup
try:
    close_button = driver.find_element(By.XPATH, "/html[1]/body[1]/main[1]/div[1]/app-root[1]/app-bfs-home-page[1]/div[3]/div[1]/div[1]/app-bfs-home-search[1]/div[1]/div[1]/div[1]/mat-form-field[1]/div[1]/div[1]/div[1]/div[1]/span[1]/mat-icon[1]")
    close_button.click()
    time.sleep(2)
except NoSuchElementException:
    pass

# Input "New York" and search
search_box = driver.find_element(By.XPATH, "/html[1]/body[1]/main[1]/div[1]/app-root[1]/app-bfs-home-page[1]/div[3]/div[1]/div[1]/app-bfs-home-search[1]/div[1]/div[1]/div[1]/mat-form-field[1]/div[1]/div[1]/div[1]/div[1]/input[1]")
search_box.send_keys("New York")
time.sleep(2)

ny_option = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[normalize-space()='New York']")))
ny_option.click()
search_button = driver.find_element(By.CSS_SELECTOR, ".search-button.btn.filter.cta")
search_button.click()
time.sleep(5)

# Loop through listing pages
while True:
    # Loop through listings on the current page
    listings = driver.find_elements_by_class_name("listing-title-link")  # Assuming this class name for each listing
    for listing in listings:
        listing.click()
        data = {}

        # Extracting the additional data fields
        email = "NA"  # As specified by you

        # Using a dictionary to map the field names to their respective XPaths
        field_mappings = {
            "Price": "/html[1]/body[1]/form[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div[3]/div[1]/div[3]/div[1]/div[1]/div[1]/p[1]/b[1]",
            "Gross Revenue": "/html[1]/body[1]/form[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div[3]/div[1]/div[3]/div[1]/div[2]/div[1]/p[1]/b[1]",
            "Cash Flow": "/html[1]/body[1]/form[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div[3]/div[1]/div[3]/div[1]/div[1]/div[2]/p[1]/b[1]",
            "Inventory": "/html[1]/body[1]/form[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div[3]/div[1]/div[3]/div[1]/div[2]/div[2]/p[1]/b[1]",
            "EBITDA": "/html[1]/body[1]/form[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div[3]/div[1]/div[3]/div[1]/div[2]/div[1]/p[2]/b[1]"
        }

        for field, xpath in field_mappings.items():
            try:
                data[field] = driver.find_element(By.XPATH, xpath).text
            except NoSuchElementException:
                data[field] = "Not Available"

        all_data.append(data)
        driver.back()  # Going back to the listings page after extracting details from one listing

    # Navigate to the next page (considering there's a "Next" button to go to the next page of listings)
    try:
        next_button = driver.find_element(By.XPATH, "//a[normalize-space()='Next']")
        next_button.click()
        time.sleep(5)
    except NoSuchElementException:
        break  # End the loop if there's no next button, assuming we are on the last page

# Save data to Excel
df = pd.DataFrame(all_data)
df.to_excel("output_data.xlsx", index=False)
driver.quit()
