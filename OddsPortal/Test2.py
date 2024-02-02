import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException, StaleElementReferenceException
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


options = uc.ChromeOptions()
options.headless = False
options.binary_location = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
driver = uc.Chrome(driver_executable_path=r"/usr/local/bin/chromedriver", options=options)

df = pd.DataFrame(columns=[
    "Team A", "Team B", "Final Result", "HT Score", "2nd Half Score", 
    "1X2 Full Time 1 Back", "1X2 Full Time 1 Lay", 
    "1X2 Full Time X Back", "1X2 Full Time X Lay", 
    "1X2 Full Time 2 Back", "1X2 Full Time 2 Lay",
    "Over/Under Fulltime 1.5 Back 1", "Over/Under Fulltime 1.5 Lay 1",	
    "Over/Under Fulltime 1.5 Back 2", "Over/Under Fulltime 1.5 Lay 2",
    "Over/Under Fulltime 2.5 Back 1", "Over/Under Fulltime 2.5 Lay 1",	
    "Over/Under Fulltime 2.5 Back 2", "Over/Under Fulltime 2.5 Lay 2",
    "Over/Under Fulltime 3.5 Back 1", "Over/Under Fulltime 3.5 Lay 1",	
    "Over/Under Fulltime 3.5 Back 2", "Over/Under Fulltime 3.5 Lay 2",
    "Over/Under Halftime 0.5 Back 1", "Over/Under Halftime 0.5 Lay 1",	
    "Over/Under Halftime 0.5 Back 2", "Over/Under Halftime 0.5 Lay 2",
    "Over/Under Halftime 1.5 Back 1", "Over/Under Halftime 1.5 Lay 1",	
    "Over/Under Halftime 1.5 Back 2", "Over/Under Halftime 1.5 Lay 2",
    "BTTS Fulltime Back 1", "BTTS Fulltime Lay 1",
    "BTTS Fulltime Back 2", "BTTS Fulltime Lay 2",

],)
excel_file = "match_data.xlsx"

def extract_odds(x, y):
    pyautogui.moveTo(x, y)  # Slower movemecnt to the target
    time.sleep(0.5)  # Brief pause before clicking
    pyautogui.click(button='right')  # Right-click on the element
    time.sleep(0.5)  # Brief pause after right-clicking
    pyautogui.hotkey('command', 'c')  # Use 'command' instead of 'ctrl' on macOS
    time.sleep(1)  # Wait for the clipboard to update
    return pyperclip.paste()

def extract_match_data(driver):
    try:
        #Extract team names and scores
        team_a = driver.find_element(By.XPATH, "//span[contains(@class, 'order-first')]").text
        team_b = driver.find_element(By.XPATH, "//span[contains(@class, 'truncate') and not(contains(@class, 'order-first'))]").text
        time.sleep(2)
        result_section = driver.find_element(By.XPATH, "//div[@class='flex flex-wrap']").text

        if "Final result" in result_section:
            final_result, scores = result_section.split("Final result")[1].strip().split(" (")
            ht_score, second_half_score = scores.strip(")").split(", ")
        else:
            result_lines = result_section.split("\n")
            final_result = result_lines[1] if len(result_lines) > 1 else "Result not available"
            ht_score, second_half_score = "", ""  # No scores available

        # Scroll to the odds section
        odds_section_xpath = "//div[@data-v-298208b0 and contains(@class, 'border-black-borders')]"
        odds_section = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, odds_section_xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView();", odds_section)

        # #Extract odds using pyautogui
        time.sleep(5)  # Wait for a few seconds to ensure the page is stable
        back_1 = extract_odds(818.70, 393.13)
        back_x = extract_odds(878.78, 393.22)
        back_2 = extract_odds(937.25, 393.34)
        lay_1 = extract_odds(817.85, 443.01)
        lay_x = extract_odds(875.53, 443.64)
        lay_2 = extract_odds(938.09, 443.38)

        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)

        #time.sleep(180)

        over_under_element = driver.find_element(By.XPATH, "//div[text()='Over/Under']")
        driver.execute_script("arguments[0].click();", over_under_element)
        time.sleep(1)
        pyautogui.scroll(-12)
        time.sleep(1)
        

        specific_element_xpath = "//p[normalize-space()='Over/Under +1.5']"
        specific_element = driver.find_element(By.XPATH, specific_element_xpath)
        specific_element.click()
        time.sleep(1) 
        

        odds_section_xpath = "//div[@data-v-298208b0]//p[contains(text(), 'Betting Exchanges')]"
        odds_section = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, odds_section_xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView();", odds_section)
        time.sleep(3)

        #time.sleep(2)
        back_1_1_5_fulltime = extract_odds(878.43, 154.66)
        back_2_1_5_fulltime = extract_odds(938.66, 154.53)
        lay_1_1_5_fulltime = extract_odds(878.57, 205.87)
        lay_2_1_5_fulltime = extract_odds(938.54, 204.02)

        driver.back()
        time.sleep(2)
        specific_element.click()

        specific_element_xpath_2_5 = "//p[normalize-space()='Over/Under +2.5']"
        specific_element_2_5 = driver.find_element(By.XPATH, specific_element_xpath_2_5)
        specific_element_2_5.click()
        time.sleep(1)

        odds_section_xpath_2_5 = "//div[@data-v-298208b0]//p[contains(text(), 'Betting Exchanges')]"
        odds_section_2_5 = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, odds_section_xpath_2_5))
        )
        driver.execute_script("arguments[0].scrollIntoView();", odds_section_2_5)
        time.sleep(3)

        back_1_2_5_fulltime = extract_odds(878.43, 154.66)
        back_2_2_5_fulltime = extract_odds(938.66, 154.53)
        lay_1_2_5_fulltime = extract_odds(878.57, 205.87)
        lay_2_2_5_fulltime = extract_odds(938.54, 204.02) 

        driver.back()
        time.sleep(2)
        specific_element_2_5.click()

        specific_element_xpath_3_5 = "//p[normalize-space()='Over/Under +3.5']"
        specific_element_3_5 = driver.find_element(By.XPATH, specific_element_xpath_3_5)
        specific_element_3_5.click()
        time.sleep(1)

        odds_section_xpath_3_5 = "//div[@data-v-298208b0]//p[contains(text(), 'Betting Exchanges')]"
        odds_section_3_5 = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, odds_section_xpath_3_5))
        )
        driver.execute_script("arguments[0].scrollIntoView();", odds_section_3_5)
        time.sleep(3)

        back_1_3_5_fulltime = extract_odds(878.43, 154.66)
        back_2_3_5_fulltime = extract_odds(938.66, 154.53)
        lay_1_3_5_fulltime = extract_odds(878.57, 205.87)
        lay_2_3_5_fulltime = extract_odds(938.54, 204.02)

        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)

        ht_under_element = driver.find_element(By.XPATH, "/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/main[1]/div[2]/div[2]/div[5]/div[1]/div[2]")
        ht_under_element.click()
        time.sleep(3)

        pyautogui.scroll(-2)
        time.sleep(1)
        

        specific_element_xpath_0_5_ht = "//p[normalize-space()='Over/Under +0.5']"
        specific_element_0_5_ht = driver.find_element(By.XPATH, specific_element_xpath_0_5_ht)
        specific_element_0_5_ht.click()
        time.sleep(1) 
        

        odds_section_xpath_0_5_ht = "//div[@data-v-298208b0]//p[contains(text(), 'Betting Exchanges')]"
        odds_section_0_5_ht = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, odds_section_xpath_0_5_ht))
        )
        driver.execute_script("arguments[0].scrollIntoView();", odds_section_0_5_ht)
        time.sleep(3)

        #time.sleep(2)
        back_1_0_5_halftime = extract_odds(878.43, 154.66)
        back_2_0_5_halftime = extract_odds(938.66, 154.53)
        lay_1_0_5_halftime = extract_odds(878.57, 205.87)
        lay_2_0_5_halftime = extract_odds(938.54, 204.02)

        driver.back()
        time.sleep(2)
        specific_element_0_5_ht.click()

        specific_element_xpath_1_5_ht = "//p[normalize-space()='Over/Under +1.5']"
        specific_element_1_5_ht = driver.find_element(By.XPATH, specific_element_xpath_1_5_ht)
        specific_element_1_5_ht.click()
        time.sleep(1)

        odds_section_xpath_1_5_ht = "//div[@data-v-298208b0]//p[contains(text(), 'Betting Exchanges')]"
        odds_section_1_5_ht = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, odds_section_xpath_1_5_ht))
        )
        driver.execute_script("arguments[0].scrollIntoView();", odds_section_1_5_ht)
        time.sleep(3)

        back_1_1_5_halftime = extract_odds(878.43, 154.66)
        back_2_1_5_halftime = extract_odds(938.66, 154.53)
        lay_1_1_5_halftime = extract_odds(878.57, 205.87)
        lay_2_1_5_halftime = extract_odds(938.54, 204.02) 

        time.sleep(3)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)

        both_teams_under_element = driver.find_element(By.XPATH, "//div[text()='Both Teams to Score']")
        driver.execute_script("arguments[0].click();", both_teams_under_element)
        time.sleep(3)

        odds_section_xpath_btts = "//div[@data-v-298208b0]//p[contains(text(), 'Betting Exchanges')]"
        odds_section_btts = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, odds_section_xpath_btts))
        )
        driver.execute_script("arguments[0].scrollIntoView();", odds_section_btts)
        time.sleep(3)

        #time.sleep(2)
        back_1_btts = extract_odds(878.43, 154.66)
        back_2_btts = extract_odds(938.66, 154.53)
        lay_1_btts = extract_odds(878.57, 205.87)
        lay_2_btts = extract_odds(938.54, 204.02)

        time.sleep(2)




        
        return {
            "Team A": team_a,
            "Team B": team_b,
            "Final Result": final_result,
            "HT Score": ht_score,
            "2nd Half Score": second_half_score,
            "1X2 Full Time 1 Back": back_1,
            "1X2 Full Time X Back": back_x,
            "1X2 Full Time 2 Back": back_2,
            "1X2 Full Time 1 Lay": lay_1,
            "1X2 Full Time X Lay": lay_x,
            "1X2 Full Time 2 Lay": lay_2,
            "Over/Under Fulltime 1.5 Back 1": back_1_1_5_fulltime,	
            "Over/Under Fulltime 1.5 Lay 1": lay_1_1_5_fulltime,
            "Over/Under Fulltime 1.5 Back 2": back_2_1_5_fulltime,
            "Over/Under Fulltime 1.5 Lay 2" : lay_2_1_5_fulltime,
            "Over/Under Fulltime 2.5 Back 1": back_1_2_5_fulltime,	
            "Over/Under Fulltime 2.5 Lay 1": lay_1_2_5_fulltime,
            "Over/Under Fulltime 2.5 Back 2": back_2_2_5_fulltime,
            "Over/Under Fulltime 2.5 Lay 2" : lay_2_2_5_fulltime,
            "Over/Under Fulltime 3.5 Back 1": back_1_3_5_fulltime,	
            "Over/Under Fulltime 3.5 Lay 1": lay_1_3_5_fulltime,
            "Over/Under Fulltime 3.5 Back 2": back_2_3_5_fulltime,
            "Over/Under Fulltime 3.5 Lay 2" : lay_2_3_5_fulltime,
            "Over/Under Halftime 0.5 Back 1": back_1_0_5_halftime,	
            "Over/Under Halftime 0.5 Lay 1": lay_1_0_5_halftime,
            "Over/Under Halftime 0.5 Back 2": back_2_0_5_halftime,
            "Over/Under Halftime 0.5 Lay 2" : lay_2_0_5_halftime,
            "Over/Under Halftime 1.5 Back 1": back_1_1_5_halftime,	
            "Over/Under Halftime 1.5 Lay 1": lay_1_1_5_halftime,
            "Over/Under Halftime 1.5 Back 2": back_2_1_5_halftime,
            "Over/Under Halftime 1.5 Lay 2" : lay_2_1_5_halftime,
            "BTTS Fulltime Back 1": back_1_btts,	
            "BTTS Fulltime Lay 1": lay_1_btts,
            "BTTS Fulltime Back 2": back_2_btts,
            "BTTS Fulltime Lay 2" : lay_2_btts


         }
            
    except NoSuchElementException as e:
        print(f"Element not found: {e}")
        return None
    except TimeoutException:
        print("Timed out waiting for page elements to load.")
        return None

driver.get("https://www.oddsportal.com/")

# Wait for the page to load
#WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

# Click the login button
login_button_xpath = "//div[@class='loginModalBtn bg-black-main border-white-main text-white-main hover:secondary-btn-hover mb-1 mt-1 flex h-6 w-[78px] cursor-pointer items-center justify-center self-center border text-sm uppercase']"
try:
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, login_button_xpath))
    )
    login_button.click()
except TimeoutException:
    print("Login button not found or page took too long to load")

# Enter username
username_input_xpath = "//input[@id='login-username-sign']"
try:
    username_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, username_input_xpath))
    )
    username_input.send_keys("hjuneja")
except TimeoutException:
    print("Username input field not found")

# Enter password
password_input_xpath = "//input[@id='login-password-sign-m']"
try:
    password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, password_input_xpath))
    )
    password_input.send_keys("Juneja@1")
except TimeoutException:
    print("Password input field not found")

# Click the submit button
submit_button_xpath = "//input[@name='login-submit']"
try:
    submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, submit_button_xpath))
    )
    submit_button.click()
except TimeoutException:
    print("Submit button not found")

# def process_matches_on_page(page_url, df, excel_file):
#     driver.get(page_url)
#     WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
#     time.sleep(2)  # Allow time for any dynamic content to load

#     # Scroll to load all matches on the page
#     last_height = driver.execute_script("return document.body.scrollHeight")
#     while True:
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(3)  # Wait for the page to load

#         new_height = driver.execute_script("return document.body.scrollHeight")
#         if new_height == last_height:
#             break
#         last_height = new_height

#     # Get all match URLs on the current page
#     match_elements = driver.find_elements(By.XPATH, "//a[contains(@class,'border-black-borders flex cursor-pointer flex-col border-b')]")
#     match_urls = [element.get_attribute('href') for element in match_elements]

match_urls = [
    "https://www.oddsportal.com/football/czech-republic/fortuna-liga/mlada-boleslav-slovacko-f1Mg7S0E/",
    "https://www.oddsportal.com/football/czech-republic/fortuna-liga/bohemians-1905-slavia-prague-QoMqWgHg/",
    "https://www.oddsportal.com/football/czech-republic/fortuna-liga/mlada-boleslav-sparta-prague-baKiUXo6/",
    "https://www.oddsportal.com/football/czech-republic/fortuna-liga/plzen-mfk-karvina-Cvt9xdvQ/",
    "https://www.oddsportal.com/football/czech-republic/fortuna-liga/ostrava-jablonec-8ARvXZ1m/",
    "https://www.oddsportal.com/football/czech-republic/fortuna-liga/hradec-kralove-teplice-byx5wxPJ/",
    "https://www.oddsportal.com/football/czech-republic/fortuna-liga/liberec-sparta-prague-AaTCslLT/",
    "https://www.oddsportal.com/football/czech-republic/fortuna-liga/plzen-bohemians-1905-zNYmmhih/",
    "https://www.oddsportal.com/football/czech-republic/fortuna-liga/ostrava-mlada-boleslav-tKydoWL4/",
    "https://www.oddsportal.com/football/czech-republic/fortuna-liga/ceske-budejovice-jablonec-GxU8rU5N/",
    "https://www.oddsportal.com/football/czech-republic/fortuna-liga/teplice-fk-pardubice-nLKvw8Tp/",
    "https://www.oddsportal.com/football/czech-republic/fortuna-liga/liberec-fk-pardubice-tvb9yeht/",
    "https://www.oddsportal.com/football/czech-republic/fortuna-liga/fk-pardubice-bohemians-1905-IovEHupA/",
    "https://www.oddsportal.com/football/czech-republic/fortuna-liga/mfk-karvina-zlin-8zXQEwUS/",
    "https://www.oddsportal.com/football/czech-republic/fortuna-liga/teplice-plzen-AqJhAcxp/"
]

def process_matches(match_urls, df, excel_file):
    for url in match_urls:
        driver.get(url)
        match_data = extract_match_data(driver)
        if match_data:
            new_row = pd.DataFrame([match_data])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_excel(excel_file, index=False)
            print(match_data)
        time.sleep(1)  # Adjust time as necessary
    return df

df = process_matches(match_urls, df, excel_file)


# Base URL and page processing
# base_url = "https://www.oddsportal.com/football/australia/a-league-2022-2023/results/#/page/"

# for page_number in range(1, 5):
#     df = process_matches_on_page(base_url + str(page_number), df, excel_file)

# Save the DataFrame to Excel
#df.to_excel("match_data.xlsx", index=False)

# Close the browser
driver.quit()