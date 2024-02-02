import os
import glob
import shutil
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import undetected_chromedriver as uc
import ssl
import re
from bs4 import BeautifulSoup
from captchasolver import ocr_from_image
import base64
import urllib.parse
# For SSL issue
ssl._create_default_https_context = ssl._create_unverified_context


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
        print(
            f"No matching files found in Downloads directory for pattern '{pattern}'.")
        return None

    # Sort to get the latest file
    matching_files.sort()

    # The last item in the sorted list is our most recent download
    source_file_path = matching_files[-1]  # The last item

    # Get the destination path (directory of the script)
    destination_path = os.path.join(
        os.getcwd(), os.path.basename(source_file_path))

    # Move the file (will overwrite if the file already exists)
    shutil.move(source_file_path, destination_path)

    return destination_path


file_name = 'tenders_data.csv'
try:
    existing_data = pd.read_csv(file_name)
except FileNotFoundError:
    existing_data = pd.DataFrame(columns=[
        "Organisation Chain", "Tender Reference Number", "Tender ID", "Form Of Contract", "No. of Covers",
        "Tender Fee", "EMD Amount", "Title", "Tender Value", "Product Category", "Bid Opening Place",
        "Published Date", "Bid Opening Date", "Bid Submission Start Date", "Bid Submission End Date",
        "Tender Inviting Authority Name", "Tender Inviting Authority Address", "PDF File Path"
    ])


options = uc.ChromeOptions()
options.binary_location = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
driver = uc.Chrome(
driver_executable_path=r"/usr/local/bin/chromedriver", options=options)


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


tenders_processed = 0  # To count the number of tenders processed
tender_index = 0


while True:  # This loop will continue until there are no more tenders to process or a set limit is reached

    try:
        link_id = 'DirectLink' if tender_index == 0 else f'DirectLink_{tender_index}'
        tender_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, link_id))
        )
        tender_link.click()
    except NoSuchElementException:
        print(f"All tenders processed. Total: {tenders_processed}.")
        break
    except TimeoutException:
        print(f"Timeout waiting for next tender. Total tenders processed: {tenders_processed}.")
        break
    except Exception as e:
        print(f"An error occurred: {str(e)}. Continuing to the next tender.")
        tender_index += 1
        continue

    # Click on the desired link using Selenium
    link_element = driver.find_element(By.XPATH, "//a[@id='DirectLink']")
    link_element.click()

    time.sleep(5)

    # Extract the page's HTML source
    html_source = driver.page_source

    # Parse the extracted HTML using BeautifulSoup
    soup = BeautifulSoup(html_source, 'html.parser')

    # 1. Organisation Chain
    organisation_chain = soup.select_one("td.td_caption:contains('Organisation Chain') + td.td_field b").text

    # 2. Tender Reference Number
    tender_reference_number = soup.select_one("td.td_caption:contains('Tender Reference Number') + td.td_field b").text

    # 3. Tender ID
    tender_id = soup.select_one("td.td_caption:contains('Tender ID') + td.td_field b").text

    # 4. Form Of Contract
    form_of_contract = soup.select_one("td.td_caption:contains('Form Of Contract') + td.td_field").text

    # 5. No. of Covers
    no_of_covers = soup.select_one("td.td_caption:contains('No. of Covers') + td.td_field").text

    # 6. Tender Fee in ₹
    tender_fee = soup.select_one("td.td_caption:contains('Tender Fee in ₹') + td.td_field").text

    # 7. EMD Amount in ₹
    emd_amount = soup.select_one("td.td_caption:contains('EMD Amount in ₹') + td.td_field").text

    # 8. Title
    title = soup.select_one("td.td_caption:contains('Title') + td.td_field b").text

    # 9. Tender Value in ₹
    tender_value = soup.select_one("td.td_caption:contains('Tender Value in ₹') + td.td_field").text

    # 10. Product Category
    product_category = soup.select_one("td.td_caption:contains('Product Category') + td.td_field").text

    # 11. Bid Opening Place
    bid_opening_place = soup.select_one("td.td_caption:contains('Bid Opening Place') + td.td_field").text

    # 12. Published Date
    published_date = soup.select_one("td.td_caption:contains('Published Date') + td.td_field").text

    # 13. Bid Opening Date
    bid_opening_date = soup.select_one("td.td_caption:contains('Bid Opening Date') + td.td_field").text

    # 14. Bid Submission Start Date
    bid_submission_start_date = soup.select_one("td.td_caption:contains('Bid Submission Start Date') + td.td_field").text

    # 15. Bid Submission End Date
    bid_submission_end_date = soup.select_one("td.td_caption:contains('Bid Submission End Date') + td.td_field").text

    # 17. Name (Tender Inviting Authority)
    tender_inviting_authority_name = soup.select_one("td.td_caption:contains('Name') + td.td_field").text

    # 18. Address (Tender Inviting Authority)
    tender_inviting_authority_address = soup.select_one("td.td_caption:contains('Address') + td.td_field").text

    # Click on the link to start the PDF download process
    pdf_download_link = driver.find_element(By.ID, "docDownoad")
    pdf_download_link.click()

    # Wait for the next page (with the captcha) to load
    # You can adjust the waiting condition based on a unique element on the captcha page
    wait.until(EC.presence_of_element_located((By.ID, "captchaImage")))


    #Find the captcha image element
    captcha_img_elem = wait.until(EC.visibility_of_element_located((By.ID, "captchaImage")))

    # Extract base64 encoded data from src attribute
    src_data = captcha_img_elem.get_attribute("src")
    base64_data = src_data.split(",")[1]

    decoded_data = urllib.parse.unquote(base64_data)
    image_data = base64.b64decode(decoded_data)

    with open("downloaded_captcha.png", 'wb') as img_file:
        img_file.write(image_data)
    recognized_text = ocr_from_image("downloaded_captcha.png")

    # Input the recognized text into the captcha field
    captcha_input = driver.find_element(By.ID, "captchaText")
    captcha_input.send_keys(recognized_text)

    # Click on the Submit button
    submit_btn = driver.find_element(By.ID, "Submit")
    submit_btn.click()

    # For the PDF file:
    pdf_path = move_latest_download_to_cwd("*.pdf")

    img_file_path = "downloaded_captcha.png"  # Replace with your image file path
    delete_file_if_exists(img_file_path)

    # We have already scraped the following fields: [all your fields] + PDF File Path
    tender_data = {
        "Organisation Chain": organisation_chain,
        "Tender Reference Number": tender_reference_number,
        "Tender ID": tender_id,
        "Form Of Contract": form_of_contract,
        "No. of Covers": no_of_covers,
        "Tender Fee": tender_fee,
        "EMD Amount": emd_amount,
        "Title": title,
        "Tender Value": tender_value,
        "Product Category": product_category,
        "Bid Opening Place": bid_opening_place,
        "Published Date": published_date,
        "Bid Opening Date": bid_opening_date,
        "Bid Submission Start Date": bid_submission_start_date,
        "Bid Submission End Date": bid_submission_end_date,
        "Tender Inviting Authority Name": tender_inviting_authority_name,
        "Tender Inviting Authority Address": tender_inviting_authority_address,
        "PDF File Path": pdf_path
        }

    # Append the data to the DataFrame
    existing_data = existing_data.append(tender_data, ignore_index=True)

    # Save the updated DataFrame to a CSV file
    existing_data.to_csv(file_name, index=False)

    # After extracting the data, navigate back to the tenders page
    driver.execute_script("window.history.go(-2)")

    # Time delay to respect the website's resources and robots.txt guidelines
    time.sleep(5)

    # Increment the tender_index to process the next tender
    tender_index += 1
    tenders_processed += 1

