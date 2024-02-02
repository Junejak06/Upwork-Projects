import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc
import time

# Set up the Chrome WebDriver
options = uc.ChromeOptions()
options.headless = False
options.add_argument("--window-size=1920,1080")
options.binary_location = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
driver = uc.Chrome(driver_executable_path=r"/usr/local/bin/chromedriver", options=options)

# Connect to SQLite database
conn = sqlite3.connect('matches.db')
c = conn.cursor()

# Create table to store match data
c.execute('''CREATE TABLE IF NOT EXISTS matches
             (league_name text, start_time text, match_time text, home_team text, away_team text, score text, home_possession text, away_possession text)''')

def extract_basic_match_info(match):
    start_time = match.find_element(By.XPATH, ".//span[contains(@class, 'time')]").text.strip()
    home_team_name = match.find_element(By.XPATH, ".//span[@itemprop='homeTeam']").text.strip()
    away_team_name = match.find_element(By.XPATH, ".//span[@itemprop='awayTeam']").text.strip()
    score_home = match.find_element(By.XPATH, ".//span[@class='score-home minitext']").text.strip()
    score_away = match.find_element(By.XPATH, ".//span[@class='score-away minitext']").text.strip()
    score = f"{score_home} - {score_away}"

    match_time_elements = match.find_elements(By.XPATH, ".//span[contains(@class, 'status minitext')]")
    match_time = match_time_elements[0].text.strip() if match_time_elements else 'N/A'

    return start_time, home_team_name, away_team_name, score, match_time

def extract_additional_match_info(match, driver):
    # Hover to reveal pop-up
    hover_element = match.find_element(By.XPATH, ".//span[@class='v-tt-box']//span[@class='score-away minitext']")
    ActionChains(driver).move_to_element(hover_element).perform()

    # Extract additional details from pop-up
    try:
        possession_home = driver.find_element(By.XPATH, "//span[@class='possessionHome']").text.strip()
        possession_away = driver.find_element(By.XPATH, "//span[@class='possessionAway']").text.strip()
    except StaleElementReferenceException:
        # Handle stale element by re-locating it
        possession_home = "N/A"
        possession_away = "N/A"

    return possession_home, possession_away

def scrape_matches(league, driver, c):
    league_name = league.find_element(By.XPATH, ".//a[contains(@class, 'compe-name')]").text.strip()
    print(f"Processing league: {league_name}")

    matches = league.find_elements(By.XPATH, ".//a[contains(@class, 'match-container')]")
    for match in matches:
        start_time, home_team_name, away_team_name, score, match_time = extract_basic_match_info(match)

        if match_time != '-':
            possession_home, possession_away = extract_additional_match_info(match, driver)

            c.execute("INSERT INTO matches VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                      (league_name, start_time, match_time, home_team_name, away_team_name, score, possession_home, possession_away))
            print(f"Saved: League: {league_name}, Start Time: {start_time}, Match Time: {match_time}, Home Team: {home_team_name}, Away Team: {away_team_name}, Score: {score}, Home Possession: {possession_home}, Away Possession: {possession_away}")

def extract_data(driver):
    # Navigate to the webpage
    driver.get("https://www.aiscore.com/")

    # Click the Football tab
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Football']"))).click()
    time.sleep(3)

    # Extract initial visible matches
    initial_leagues = driver.find_elements(By.XPATH, "//div[contains(@class, 'comp-container')]")
    for league in initial_leagues:
        scrape_matches(league, driver, c)

    # Scroll until "Today's Upcoming Matches" is found
    while not driver.find_elements(By.XPATH, "//div[@class='status-tip-page']/span[contains(text(), \"Today's Upcoming Matches\")]"):
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(1)

        leagues_after_scroll = driver.find_elements(By.XPATH, "//div[contains(@class, 'comp-container')]")
        for league in leagues_after_scroll:
            if league.find_elements(By.XPATH, ".//div[@class='status-tip-page']/span[contains(text(), \"Today's Upcoming Matches\")]"):
                break
            scrape_matches(league, driver, c)

    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("Script finished.")

# Call the function with the driver instance
extract_data(driver)
