
from selenium import webdriver
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import ssl
import time
import shutil
import os
import glob

# For SSL issue
ssl._create_default_https_context = ssl._create_unverified_context

options = uc.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--window-size=1920x1080')
options.binary_location = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
driver = uc.Chrome(driver_executable_path=r"/usr/local/bin/chromedriver", options=options)

# Navigate to the given Google Drive link
driver.get("https://drive.google.com/file/d/1XXk2LO0CsNADBB1LRGOV5rUpyZdEZ8s2/view")

# Wait for a few seconds to ensure the page has loaded
time.sleep(5)

# Click the download button using the provided HTML class
download_button = driver.find_element(By.CSS_SELECTOR, "div[aria-label='Download']")
download_button.click()

# Let the browser be open for a while
time.sleep(20)  # 2 minutes, you can adjust as needed

# Get the path to the default downloads directory
downloads_path = os.path.expanduser("~") + "/Downloads/"

# Use glob to search for the downloaded file based on a pattern
matching_files = glob.glob(downloads_path + "2023_LoL_esports_match_data_from_OraclesElixir*.csv")

# Print the matching files for debugging
print("Matching Files:", matching_files)

# If no files matched, we don't want to proceed
if not matching_files:
    print("No matching files found in Downloads directory.")
    exit()

# Sort to get the latest file
matching_files.sort()

# The last item in the sorted list is our most recent download
source_file_path = matching_files[-1]  # The last item

# Get the destination path (directory of the script)
destination_path = os.getcwd() + "/2023_LoL_esports_match_data_from_OraclesElixir.csv"

# Print paths for debugging
print("Source File Path:", source_file_path)
print("Destination Path:", destination_path)

# Move the file (will overwrite if the file already exists)
shutil.move(source_file_path, destination_path)

print("File has been moved.")

# Optionally, close the driver after a few seconds
# time.sleep(5)
# driver.close()