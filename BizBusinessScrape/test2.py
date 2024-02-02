import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc
import ssl

# For SSL issue
ssl._create_default_https_context = ssl._create_unverified_context

def force_click_element(xpath):
    element = driver.find_element(By.XPATH, xpath)
    driver.execute_script("arguments[0].click();", element)

input_data = pd.read_excel("input.xlsx", usecols="I:T")

options = uc.ChromeOptions()
options.binary_location = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
driver = uc.Chrome(driver_executable_path=r"/usr/local/bin/chromedriver", options=options)

wait = WebDriverWait(driver, 10)

driver.get("https://www.bizbuysell.com/")

actions = ActionChains(driver)

try:
    close_button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html[1]/body[1]/main[1]/div[1]/app-root[1]/app-bfs-home-page[1]/div[3]/div[1]/div[1]/app-bfs-home-search[1]/div[1]/div[1]/div[1]/mat-form-field[1]/div[1]/div[1]/div[1]/div[1]/span[1]/mat-icon[1]")))
    close_button.click()
    time.sleep(2)
except:
    print("Error: Could not find the 'X' button or it was not necessary to click it.")

search_box = driver.find_element(By.XPATH, "/html[1]/body[1]/main[1]/div[1]/app-root[1]/app-bfs-home-page[1]/div[3]/div[1]/div[1]/app-bfs-home-search[1]/div[1]/div[1]/div[1]/mat-form-field[1]/div[1]/div[1]/div[1]/div[1]/input[1]")
search_box.send_keys("New York")
time.sleep(2)

ny_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[normalize-space()='New York']")))
ny_option.click()

search_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".search-button.btn.filter.cta")))
search_button.click()
time.sleep(5)

filter_xpath = "/html[1]/body[1]/main[1]/div[1]/app-root[1]/app-bfs-search-results[1]/div[1]/section[1]/div[1]/app-bfs-search-filter[1]/div[1]/app-bfs-industries[1]/button[1]"

try:
    force_click_element(filter_xpath)
except:
    print("Error: Could not click the filter button using JS click.")
time.sleep(2)

more_industries_xpath = "//div[@class='all-industries-option ng-tns-c91-5 ng-star-inserted']"

try:
    force_click_element(more_industries_xpath)
except:
    print("Error: Could not click the more industries button using JS click.")
time.sleep(2)

num_industries = len(driver.find_elements(By.CLASS_NAME, "all-industry-cards"))

apply_button_xpath = ("/html[1]/body[1]/main[1]/div[1]/app-root[1]/app-bfs-search-results[1]/div[1]/"
                      "section[1]/div[1]/app-bfs-search-filter[1]/div[1]/app-bfs-industries[1]/div[1]/"
                      "div[2]/div[1]/div[5]/button[1]")

# Handle the rest of the checkboxes
for i in range(0, num_industries):
    try:
        force_click_element(filter_xpath)
        time.sleep(2)

        force_click_element(more_industries_xpath)
        time.sleep(2)

        industry_xpath = f"/html[1]/body[1]/main[1]/div[1]/app-root[1]/app-bfs-search-results[1]/div[1]/section[1]/div[1]/app-bfs-search-filter[1]/div[1]/app-bfs-industries[1]/div[1]/div[2]/div[1]/div[2]/table[1]/tbody[1]/tr[{i}]/td[1]"

        # Unselecting previously selected industry
        if i > 1:
            previous_industry_xpath = f"/html[1]/body[1]/main[1]/div[1]/app-root[1]/app-bfs-search-results[1]/div[1]/section[1]/div[1]/app-bfs-search-filter[1]/div[1]/app-bfs-industries[1]/div[1]/div[2]/div[1]/div[2]/table[1]/tbody[1]/tr[{i-1}]/td[1]"
            force_click_element(previous_industry_xpath)
            time.sleep(2)

        force_click_element(industry_xpath)
        time.sleep(2)

        force_click_element(apply_button_xpath)
        time.sleep(5)
        
    except NoSuchElementException:
        print(f"Could not process industry checkbox with xpath {industry_xpath}. Skipping to the next one.")
        continue

driver.quit()
