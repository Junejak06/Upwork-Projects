import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import undetected_chromedriver as uc
import ssl

# For SSL issue
ssl._create_default_https_context = ssl._create_unverified_context

# Read the Excel file from columns I to T
input_data = pd.read_excel("input.xlsx", usecols="I:T")

options = uc.ChromeOptions()
options.binary_location = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
driver = uc.Chrome(driver_executable_path=r"/usr/local/bin/chromedriver", options=options)

wait = WebDriverWait(driver, 10)

driver.get("https://www.bizbuysell.com/")

# Click on the 'X' button first
try:
    close_button = driver.find_element(By.XPATH, "/html[1]/body[1]/main[1]/div[1]/app-root[1]/app-bfs-home-page[1]/div[3]/div[1]/div[1]/app-bfs-home-search[1]/div[1]/div[1]/div[1]/mat-form-field[1]/div[1]/div[1]/div[1]/div[1]/span[1]/mat-icon[1]")
    close_button.click()
    time.sleep(2)
except:
    print("Error: Could not find the 'X' button or it was not necessary to click it.")

# Input "New York"
search_box = driver.find_element(By.XPATH, "/html[1]/body[1]/main[1]/div[1]/app-root[1]/app-bfs-home-page[1]/div[3]/div[1]/div[1]/app-bfs-home-search[1]/div[1]/div[1]/div[1]/mat-form-field[1]/div[1]/div[1]/div[1]/div[1]/input[1]")
search_box.send_keys("New York")
time.sleep(2)

# Wait for the dropdown option to be clickable and then click it
ny_option = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//div[normalize-space()='New York']"))
)
ny_option.click()

# Click on the search button using the absolute XPath
search_button = driver.find_element(By.CSS_SELECTOR, ".search-button.btn.filter.cta")
search_button.click()
time.sleep(5)

# Click on the filter option for industries
filter_xpath = "/html[1]/body[1]/main[1]/div[1]/app-root[1]/app-bfs-search-results[1]/div[1]/section[1]/div[1]/app-bfs-search-filter[1]/div[1]/app-bfs-industries[1]/button[1]"
driver.find_element(By.XPATH, filter_xpath).click()
time.sleep(2)

more_industries_xpath = "//div[@class='all-industries-option ng-tns-c91-5 ng-star-inserted']"
driver.find_element(By.XPATH, more_industries_xpath).click()
time.sleep(2)

all_data = []

# Base XPath for industry checkboxes
base_xpath = ("/html[1]/body[1]/main[1]/div[1]/app-root[1]/app-bfs-search-results[1]/div[1]/section[1]/div[1]/"
             "app-bfs-search-filter[1]/div[1]/app-bfs-industries[1]/div[1]/div[2]/div[1]/div[2]/table[1]/tbody[1]/tr[")

# Determine the number of checkboxes by counting the rows in the table (this could be adjusted based on the website's structure)
num_checkboxes = len(driver.find_elements(By.XPATH, base_xpath + "*]"))

# Use a for loop to iterate over checkboxes
for i in range(1, num_checkboxes + 1):
    try:
        # If it's not the first iteration, unselect the previous checkbox
        if i > 1:
            driver.find_element(By.XPATH, base_xpath + f"{i-1}]/td[1]").click()
            time.sleep(2)

        # Select the current checkbox
        driver.find_element(By.XPATH, base_xpath + f"{i}]/td[1]").click()
        time.sleep(2)

        # Click apply button
        apply_button_xpath = ("/html[1]/body[1]/main[1]/div[1]/app-root[1]/app-bfs-search-results[1]/div[1]/"
                              "section[1]/div[1]/app-bfs-search-filter[1]/div[1]/app-bfs-industries[1]/div[1]/"
                              "div[2]/div[1]/div[5]/button[1]")
        driver.find_element(By.XPATH, apply_button_xpath).click()
        time.sleep(5)

        # Continue with listing navigation and scraping code from previous responses
        listing_id = 1  # Start from the first listing

        while True:
            try:
                # Click the first listing in the industry using the absolute XPath
                listing_xpath = ("/html[1]/body[1]/main[1]/div[1]/app-root[1]/app-bfs-search-results[1]/div[1]/"
                                "section[2]/app-bfs-listing-container[1]/div[1]/app-listing-diamond[1]/a[1]/"
                                "div[1]/div[1]/div[1]/div[1]/div[1]/swiper[1]/div[3]/div[1]")
                driver.find_element(By.XPATH, listing_xpath).click()
                time.sleep(5)

                # Scrape data from the listing
                title = driver.find_element(By.XPATH, "//h1[@class='bfsTitle']").text
                location_text = driver.find_element(By.XPATH, "//h2[@class='gray']").text
                city, state = location_text.split(",")[0], location_text.split(",")[1].strip().split(" ")[0]
                country = "USA"
                url = driver.current_url
                source = "bizquest"

                # Scrape Listed By (Firm)
                try:
                    firm_xpath = ("/html[1]/body[1]/form[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div[3]/div[2]/"
                                  "div[1]/div[1]/div[1]/div[1]/div[2]/div[3]/h4[1]/span[1]")
                    listed_by_firm_element = wait.until(EC.presence_of_element_located((By.XPATH, firm_xpath)))
                    listed_by_firm = listed_by_firm_element.text
                except TimeoutException:
                    listed_by_firm = "No Firm Listed"
                
                print("Listed By (Firm):", listed_by_firm)

                # Scrape Listed By (Name) - First Way
                try:
                    name_xpath_1 = ("/html[1]/body[1]/form[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div[3]/div[2]/"
                                   "div[1]/div[1]/div[1]/div[1]/div[2]/div[3]/h3[1]/a[1]")
                    listed_by_name_element = wait.until(EC.presence_of_element_located((By.XPATH, name_xpath_1)))
                    listed_by_name = listed_by_name_element.text
                except TimeoutException:
                    try:
                        # Scrape Listed By (Name) - Second Way
                        name_xpath_2 = ("/html[1]/body[1]/form[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div[3]/div[2]/"
                                       "div[1]/div[1]/div[1]/div[1]/div[2]/div[3]/h3[1]")
                        listed_by_name_element = wait.until(EC.presence_of_element_located((By.XPATH, name_xpath_2)))
                        listed_by_name = listed_by_name_element.text
                    except TimeoutException:
                        listed_by_name = "No Name Listed"
                
                print("Listed By (Name):", listed_by_name)

                # Click to reveal phone number
                view_telephone_xpath = ("/html[1]/body[1]/form[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div[3]/div[2]/"
                                        "div[1]/div[1]/div[1]/div[1]/div[2]/div[3]/h3[1]/div[1]/a[1]")
                driver.find_element(By.XPATH, view_telephone_xpath).click()
                time.sleep(2)

                phone_xpath = ("/html[1]/body[1]/form[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div[3]/div[2]/div[1]/"
                               "div[1]/div[1]/div[1]/div[2]/div[3]/h3[1]/div[1]/label[1]/a[1]")
                phone = driver.find_element(By.XPATH, phone_xpath).text
                print(f"Phone Number: {phone}")

                # ... (continue scraping other data)

                data = {
                    "Title": title,
                    "City": city,
                    "State": state,
                    "Country": country,
                    "URL": url,
                    "Listed By (Firm)": listed_by_firm,
                    "Listed By (Name)": listed_by_name,
                    "Phone": phone
                }

                all_data.append(data)

                # Go back to the listings
                driver.back()
                time.sleep(5)

                # Move on to the next listing
                listing_id += 1

            except NoSuchElementException:
                print("Could not process a listing. Skipping to the next one.")
                listing_id += 1
                continue

            # Click the next page if available
            try:
                next_page_xpath = ("/html[1]/body[1]/main[1]/div[1]/app-root[1]/app-bfs-search-results[1]/div[1]/"
                                   "section[2]/div[1]/app-pagination[1]/div[1]/pagination-template[1]/ul[1]/li[7]/a[1]")
                driver.find_element(By.XPATH, next_page_xpath).click()
                time.sleep(5)
            except NoSuchElementException:
                break  # No next page available

    except NoSuchElementException:
        print("Could not process an industry checkbox. Skipping to the next one.")
        continue

# Store the data in a pandas DataFrame and then write to an Excel file
df = pd.DataFrame(all_data)
df.to_excel("output.xlsx", index=False)

driver.close()