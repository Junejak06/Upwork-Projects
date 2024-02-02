import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
import undetected_chromedriver as uc
import ssl
import re
from bs4 import BeautifulSoup
from captchasolver import ocr_from_image
import base64
import urllib.parse
# For SSL issue
ssl._create_default_https_context = ssl._create_unverified_context
import shutil
import glob
import os

def delete_file_if_exists(file_path):
    """Delete a file if it exists."""
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"Deleted {file_path}.")
        except Exception as e:
            print(f"Error deleting {file_path}. Reason: {e}")

def move_latest_download_to_cwd(pattern):
    """Move the latest downloaded file matching the pattern to the current working directory."""
    
    # Get the path to the default downloads directory
    downloads_path = os.path.expanduser("~") + "/Downloads/"

    # Use glob to search for the downloaded file based on the pattern
    matching_files = glob.glob(downloads_path + pattern)
    
    # If no files matched, return None
    if not matching_files:
        print(f"No matching files found in Downloads directory for pattern '{pattern}'.")
        return None
    
    # Sort to get the latest file
    matching_files.sort()

    # The last item in the sorted list is our most recent download
    source_file_path = matching_files[-1]  # The last item

    # Get the destination path (directory of the script)
    destination_path = os.path.join(os.getcwd(), os.path.basename(source_file_path))

    # Move the file (will overwrite if the file already exists)
    shutil.move(source_file_path, destination_path)
    
    return destination_path

options = uc.ChromeOptions()
options.binary_location = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
driver = uc.Chrome(driver_executable_path=r"/usr/local/bin/chromedriver", options=options)

# Navigate to the provided URL
driver.get('https://mahatenders.gov.in/nicgep/app?page=FrontEndTendersByOrganisation&service=page')

# Set a wait time to ensure the page has loaded properly
wait = WebDriverWait(driver, 10)

# Organization name to search for; replace this with the desired name
organization_name = "Municipal Corporation of Greater Mumbai"  # Example organization name

try:
    # Wait until the table has loaded, and then locate the td containing the organization name
    org_td_element = wait.until(EC.presence_of_element_located((By.XPATH, f"//td[text()='{organization_name}']")))

    # From the td with the organization name, find the parent (tr) and then locate the link with the class `DirectLink`
    link_element = org_td_element.find_element(By.XPATH, ".//following-sibling::td//a[contains(@id, 'DirectLink')]")

    # Click the link
    link_element.click()
    time.sleep(5)

except (NoSuchElementException, TimeoutException):
    print(f"Organization named '{organization_name}' was not found or there was a timeout.")
# Fetch all tender links first
# Assuming other setup code here...
wait = WebDriverWait(driver, 10)

# Fetch all tender links first
all_tender_links = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//tr/td/a[starts-with(@id, 'DirectLink')]")))

def get_link_by_index(index):
    # Determine the ID of the link dynamically based on its index
    if index == 0:
        link_id = "DirectLink"
    else:
        link_id = f"DirectLink_{index}"
    
    # Locate and return the link element
    return driver.find_element(By.ID, link_id)

    
# Iterate through each tender
# Now iterate through these links
for idx in range(len(all_tender_links)):
    try:
        link_element = get_link_by_index(idx)
        link_element.click()
        
        # Extract and print the tender data
        print("Processing Tender:")

        # Extract the page's HTML source
        html_source = driver.page_source

        # Parse the extracted HTML using BeautifulSoup
        soup = BeautifulSoup(html_source, 'html.parser')
        
        # Extract the data as you did before
        organisation_chain = soup.select_one("td.td_caption:contains('Organisation Chain') + td.td_field b").text
        tender_reference_number = soup.select_one("td.td_caption:contains('Tender Reference Number') + td.td_field b").text
        tender_id = soup.select_one("td.td_caption:contains('Tender ID') + td.td_field b").text
        form_of_contract = soup.select_one("td.td_caption:contains('Form Of Contract') + td.td_field").text
        no_of_covers = soup.select_one("td.td_caption:contains('No. of Covers') + td.td_field").text
        tender_fee = soup.select_one("td.td_caption:contains('Tender Fee in ₹') + td.td_field").text
        emd_amount = soup.select_one("td.td_caption:contains('EMD Amount in ₹') + td.td_field").text
        title = soup.select_one("td.td_caption:contains('Title') + td.td_field b").text
        tender_value = soup.select_one("td.td_caption:contains('Tender Value in ₹') + td.td_field").text
        product_category = soup.select_one("td.td_caption:contains('Product Category') + td.td_field").text
        bid_opening_place = soup.select_one("td.td_caption:contains('Bid Opening Place') + td.td_field").text
        published_date = soup.select_one("td.td_caption:contains('Published Date') + td.td_field").text
        bid_opening_date = soup.select_one("td.td_caption:contains('Bid Opening Date') + td.td_field").text
        bid_submission_start_date = soup.select_one("td.td_caption:contains('Bid Submission Start Date') + td.td_field").text
        bid_submission_end_date = soup.select_one("td.td_caption:contains('Bid Submission End Date') + td.td_field").text
        tender_inviting_authority_name = soup.select_one("td.td_caption:contains('Name') + td.td_field").text
        tender_inviting_authority_address = soup.select_one("td.td_caption:contains('Address') + td.td_field").text

        # Click on the link to start the PDF download process
        pdf_download_link = driver.find_element(By.ID, "docDownoad")
        pdf_download_link.click()

        # Check if CAPTCHA is required
        try:
            wait.until(EC.presence_of_element_located((By.ID, "captchaImage")))
            # CAPTCHA is required, solve it as you did before
            captcha_img_elem = wait.until(EC.visibility_of_element_located((By.ID, "captchaImage")))
            src_data = captcha_img_elem.get_attribute("src")
            base64_data = src_data.split(",")[1]
            decoded_data = urllib.parse.unquote(base64_data)
            image_data = base64.b64decode(decoded_data)
            with open("downloaded_captcha.png", 'wb') as img_file:
                img_file.write(image_data)
            recognized_text = ocr_from_image("downloaded_captcha.png")

            # Input the recognized text into the captcha field
            captcha_input = driver.find_element(By.ID, "captchaText")

            max_attempts = 3  # Maximum number of attempts to solve CAPTCHA
            attempts = 0

            while attempts < max_attempts:
                # Check if recognized_text is empty
                if not recognized_text:
                    recognized_text = "A"  # If empty, set it to "A"

                captcha_input = driver.find_element(By.ID, "captchaText")
                captcha_input.clear()
                captcha_input.send_keys(recognized_text)

                # Click on the Submit button
                submit_btn = driver.find_element(By.ID, "Submit")
                submit_btn.click()

                try:
                    # Use explicit wait for the error message element
                    wait = WebDriverWait(driver, 10)  # Waiting for 10 seconds
                    error_message = wait.until(EC.presence_of_element_located((By.XPATH, "//td[@class='td_space']/span[@class='error']")))
                    error_text = error_message.text
                    if "Invalid Captcha" in error_text:
                        print("CAPTCHA solving failed. Trying again.")
                        driver.refresh()
                        
                        # Locate the CAPTCHA image element and solve it again using explicit wait
                        captcha_img_elem = wait.until(EC.presence_of_element_located((By.ID, "captchaImage")))
                        src_data = captcha_img_elem.get_attribute("src")
                        base64_data = src_data.split(",")[1]
                        decoded_data = urllib.parse.unquote(base64_data)
                        image_data = base64.b64decode(decoded_data)
                        with open("downloaded_captcha.png", 'wb') as img_file:
                            img_file.write(image_data)
                        recognized_text = ocr_from_image("downloaded_captcha.png")
                    else:
                        print("CAPTCHA solved successfully!")
                        try:
                            pdf_download_link = driver.find_element(By.XPATH, "//*[@id='DirectLink_0']")
                            pdf_download_link.click()
                        except NoSuchElementException:
                            print("PDF Download link not found!")
                        break
                except NoSuchElementException:
                    print("CAPTCHA solved successfully!")
                    
                except StaleElementReferenceException:
                    print("Element reference became stale. Retrying.")
                    attempts += 1

            if attempts == max_attempts:
                print("CAPTCHA solving failed after maximum attempts.")
        except TimeoutException:
            # CAPTCHA is not required, proceed with downloading PDF
            print("CAPTCHA is not required for this tender.")

        pdf_download_link = driver.find_element(By.ID, "docDownoad")
        pdf_download_link.click()

        # For the PDF file:
        pdf_path = move_latest_download_to_cwd("*.pdf")

        # Click the "Back" link to go back to the list of tenders
        back_link = driver.find_element(By.XPATH, "//a[@id='DirectLink_11' and @title='Back']")
        back_link.click()
        time.sleep(5)  # Wait for the page to go back

        # Since we've navigated back, we need to fetch the links again
        #all_tender_links = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//tr/td/a[starts-with(@id, 'DirectLink')]")))

    except NoSuchElementException:
        print("No more tenders found or Error processing tender: NoSuchElementException")
        continue # Exit the loop when there are no more tenders


# Close the browser
driver.quit()
