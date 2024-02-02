import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
import undetected_chromedriver as uc
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

options = uc.ChromeOptions()
options.headless = True
options.add_argument("--disable-popup-blocking")
# options.add_argument('--disable-gpu')
# options.add_argument('--no-sandbox')
# options.add_argument('--disable-setuid-sandbox')
# options.add_argument('--disable-dev-shm-usage')
# options.add_argument("--start-maximized")
# options.add_argument("--window-size=1920,1080")
options.binary_location = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
driver = uc.Chrome(driver_executable_path=r"/usr/local/bin/chromedriver", options=options)
driver.get("https://www.flashscore.co.uk/football/england/premier-league-2022-2023/results/")

columns = ['Home Team', 'Away Team', 'Match Score', 'Goal Time', 'Goal Score']
goals_df = pd.DataFrame(columns=columns)


main_window = driver.current_window_handle

# Load all matches by clicking 'See more matches'
while True:
    try:
        load_more = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'event__more--static')]")))
        driver.execute_script("arguments[0].scrollIntoView();", load_more)
        # Use JavaScript to click to avoid interception
        driver.execute_script("arguments[0].click();", load_more)
        time.sleep(2)
    except (NoSuchElementException, TimeoutException):
        print("All matches are loaded.")
        break
    except ElementClickInterceptedException:
        print("ElementClickInterceptedException occurred while clicking 'See more matches'. Trying again.")
        continue  # Retry clicking in case of interception


# Process each match
try:
    matches = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'event__match')]")))
    for match in matches:
        driver.execute_script("arguments[0].scrollIntoView();", match)
        driver.execute_script("arguments[0].click();", match)
        time.sleep(2)

        # Switch to the match detail window
        if len(driver.window_handles) > 1:
            new_window = driver.window_handles[-1]
            driver.switch_to.window(new_window)

        # Extract home team, away team, and score for each match
        home_team_xpath = "//div[contains(@class, 'duelParticipant__home')]//div[contains(@class, 'participant__participantName')]"
        away_team_xpath = "//div[contains(@class, 'duelParticipant__away')]//div[contains(@class, 'participant__participantName')]"
        score_xpath = "//div[contains(@class, 'duelParticipant__score')]//div[contains(@class, 'detailScore__wrapper')]"

        home_team = driver.find_element(By.XPATH, home_team_xpath).text
        away_team = driver.find_element(By.XPATH, away_team_xpath).text
        score = driver.find_element(By.XPATH, score_xpath).text

        # Scroll through the match detail page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for the page to load after scrolling

        # Find all goal score elements
        goal_score_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'smv__incident')]")
        for element in goal_score_elements:
            try:
                # Check if the goal time and goal score elements are present
                if element.find_elements(By.XPATH, ".//div[contains(@class, 'smv__timeBox')]") and \
                        element.find_elements(By.XPATH,
                                              ".//div[contains(@class, 'smv__incidentHomeScore') or contains(@class, 'smv__incidentAwayScore')]"):
                    # Extract goal time and goal score using XPath
                    goal_time = element.find_element(By.XPATH, ".//div[contains(@class, 'smv__timeBox')]").text
                    goal_score = element.find_element(By.XPATH,
                                                      ".//div[contains(@class, 'smv__incidentHomeScore') or contains(@class, 'smv__incidentAwayScore')]").text

                    # Append goal information to DataFrame
                    goal_data = {
                        'Home Team': home_team,
                        'Away Team': away_team,
                        'Match Score': score,
                        'Goal Time': goal_time,
                        'Goal Score': goal_score
                    }
                    goals_df = pd.concat([goals_df, pd.DataFrame([goal_data])], ignore_index=True)
                    print(goals_df)

            except NoSuchElementException:
                # Skip if goal time or goal score element is not found
                continue

        # Close the match detail window and switch back
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(main_window)
        else:
            driver.back()

except Exception as e:
    print(f"An error occurred while processing matches: {e}")

driver.quit()

goals_df.to_csv("match_goals_details_11.csv", index=False)