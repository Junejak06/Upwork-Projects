import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import ssl

# For SSL issue
ssl._create_default_https_context = ssl._create_unverified_context

# Read the Excel file
input_data = pd.read_excel("input.xls", header=None)
links = [str(link) for link in input_data.iloc[:, 0].tolist()]

options = uc.ChromeOptions()
options.binary_location = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
driver = uc.Chrome(driver_executable_path=r"/usr/local/bin/chromedriver", options=options)

# Function to scroll to an element
def scroll_to_element(element):
    driver.execute_script("arguments[0].scrollIntoView();", element)

all_results = []

for link in links:
    print(f"Navigating to: {link}")

    try:
        driver.get(link)
        time.sleep(10)

        profiles = driver.find_elements(By.XPATH, "/html[1]/body[1]/div[1]/div[1]/div[4]/main[1]/div[1]/div[1]/div[1]/div[5]/div[1]/div[5]/div[1]/div[1]/div[9]/figure[1]/div[1]/div[1]/figcaption[1]")
        current_index = 0

        while current_index < len(profiles):
            try:
                profile = profiles[current_index]
                profile_name = profile.text
                scroll_to_element(profile)
                driver.execute_script("arguments[0].click();", profile)
                time.sleep(6)
                
                twitter_link = "No Twitter account with this profile"
                try:
                    # Attempt to fetch Twitter link
                    twitter_element = driver.find_element(By.XPATH, "//a[contains(@href,'twitter.com') and @target='_blank']")
                    twitter_link = twitter_element.get_attribute("href")
                except:
                        # If fetching Twitter link fails, try fetching x.com link
                    try:
                        xcom_element = driver.find_element(By.XPATH, "//a[contains(@href,'x.com') and @target='_blank']")
                        twitter_link = xcom_element.get_attribute("href")
                    except:
                        pass
                
                print(f"Profile Name: {profile_name}")
                print(f"Twitter Link: {twitter_link}")
                print("-" * 50)

                all_results.append({"Profile Name": profile_name, "Twitter URL": twitter_link})
                driver.back()
                time.sleep(6)
                current_index += 1
                profiles = driver.find_elements(By.XPATH, "/html[1]/body[1]/div[1]/div[1]/main[1]/div[1]/div[1]/div[1]/div[5]/div[1]/div[5]/div[1]/div[1]/div[9]/figure[1]/div[2]/div[1]/ul[1]/li/div[2]/div[1]/span[1]/div[1]/span[1]/a[1]/div[1]")

            except IndexError:
                print("Encountered an IndexError, retrying...")
                time.sleep(5)
                profiles = driver.find_elements(By.XPATH, "/html[1]/body[1]/div[1]/div[1]/main[1]/div[1]/div[1]/div[1]/div[5]/div[1]/div[5]/div[1]/div[1]/div[9]/figure[1]/div[2]/div[1]/ul[1]/li/div[2]/div[1]/span[1]/div[1]/span[1]/a[1]/div[1]")
                continue

            except Exception as e:
                print(f"Error processing profile {profile_name}. Error: {str(e)}")
                current_index += 1
                continue
        
    except Exception as e:
        print(f"Link-level Error processing {link}. Error: {str(e)}")
        continue

driver.quit()

# Save results to an Excel file
output_df = pd.DataFrame(all_results)
output_df.to_excel("Twitter profiles.xlsx", index=False)
