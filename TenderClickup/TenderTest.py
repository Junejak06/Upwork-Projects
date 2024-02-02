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


# Organization name to search for; replace this with the desired name
organization_name = "Municipal Corporation of Greater Mumbai"  # Example organization name

# At the top of your script after defining the organization_name
organization_directory = os.path.join(os.getcwd(), organization_name)
if not os.path.exists(organization_directory):
    os.makedirs(organization_directory)




def delete_file_if_exists(file_path):
    """Delete a file if it exists."""
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"Deleted {file_path}.")
        except Exception as e:
            print(f"Error deleting {file_path}. Reason: {e}")

def get_existing_tender_ids(filepath):
    try:
        df = pd.read_csv("/Users/kunaljuneja/Upwork/TenderClickup/scraped_tenders.csv")
        return set(df['tender_id'].tolist())
    except:
        return set()

def sanitize_filename(filename):
    """Return a sanitized version of the filename."""
    return "".join([c for c in filename if c.isalnum() or c in (' ', '_')]).rstrip()

def move_and_rename_latest_download(title):
    downloads_path = os.path.expanduser("~") + "/Downloads/"
    matching_files = glob.glob(downloads_path + "Tendernotice_*.pdf")
    
    if not matching_files:
        print("No tendernotice.pdf found in Downloads directory.")
        return None

    # Sorting to get the most recently downloaded file
    matching_files.sort(key=os.path.getmtime, reverse=True)
    source_file_path = matching_files[0]


    destination_path = os.path.join(organization_directory, title + ".pdf")
    shutil.move(source_file_path, destination_path)
    return destination_path


def save_to_excel(data, filepath):
    # Convert data to DataFrame
    if isinstance(data, dict):
        data = pd.DataFrame([data])
        
    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:  # Check if the file exists and is not empty
        # Load the existing CSV to a DataFrame
        df_existing = pd.read_csv(filepath)
        # Append the new data to it
        df = pd.concat([df_existing, data], ignore_index=True)
    else:
        df = data
        
    # Save the combined DataFrame back to CSV
    df.to_csv(filepath, index=False)

    
def is_address_text(tag):
    return tag.name == "td" and tag.get_text().strip().startswith("Address")


options = uc.ChromeOptions()
options.binary_location = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
driver = uc.Chrome(driver_executable_path=r"/usr/local/bin/chromedriver", options=options)

# Navigate to the provided URL
driver.get('https://mahatenders.gov.in/nicgep/app?page=FrontEndTendersByOrganisation&service=page')

# Set a wait time to ensure the page has loaded properly
wait = WebDriverWait(driver, 10)

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

link_element = driver.find_element(By.XPATH, "//a[@id='DirectLink']")
link_element.click()

try:
    pdf_download_link = driver.find_element(By.XPATH, '//a[contains(text(), "Tendernotice")]')
    try:
        pdf_download_link.click()
    except:
        pass
except:
        pass



# CAPTCHA solving logic
try:
    captcha_img_elem = wait.until(EC.visibility_of_element_located((By.ID, "captchaImage")))
    src_data = captcha_img_elem.get_attribute("src")
    base64_data = src_data.split(",")[1]
    decoded_data = urllib.parse.unquote(base64_data)
    image_data = base64.b64decode(decoded_data)
    with open("downloaded_captcha.png", 'wb') as img_file:
        img_file.write(image_data)
    recognized_text = ocr_from_image("downloaded_captcha.png")

    max_attempts = 3  # Maximum number of attempts to solve CAPTCHA
    attempts = 0

    while attempts < max_attempts:
        if not recognized_text:
                    recognized_text = "A"  # If empty, set it to "A"
        captcha_input = driver.find_element(By.ID, "captchaText")
        captcha_input.clear()
        captcha_input.send_keys(recognized_text)

        submit_btn = driver.find_element(By.ID, "Submit")
        submit_btn.click()

        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//td[@class='td_space']/span[@class='error']")))
            print("CAPTCHA solving failed. Trying again.")
            driver.refresh()

            captcha_img_elem = wait.until(EC.presence_of_element_located((By.ID, "captchaImage")))
            src_data = captcha_img_elem.get_attribute("src")
            base64_data = src_data.split(",")[1]
            decoded_data = urllib.parse.unquote(base64_data)
            image_data = base64.b64decode(decoded_data)
            with open("downloaded_captcha.png", 'wb') as img_file:
                img_file.write(image_data)
            recognized_text = ocr_from_image("downloaded_captcha.png")

        except NoSuchElementException:
            print("CAPTCHA solved successfully!")
            break

        except StaleElementReferenceException:
            print("Element reference became stale. Retrying.")
            attempts += 1

except TimeoutException:
    print("No CAPTCHA present or CAPTCHA solving logic failed.")
    pass

# Finally, click the back link
try:
    back_link = driver.find_element(By.XPATH, "//a[@id='DirectLink_11' and @title='Back']")
    back_link.click()
    time.sleep(5)  # Wait for the page to go back 
except NoSuchElementException:
    print("Back link not found.")

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


# In[46]:


html_source = driver.page_source

# Parse the extracted HTML using BeautifulSoup
soup = BeautifulSoup(html_source, 'html.parser')


# In[47]:


selected_links = soup.select('a[id^="DirectLink"]')
tender_links = []


existing_tender_ids = get_existing_tender_ids("/Users/kunaljuneja/Upwork/TenderClickup/scraped_tenders.csv")
print(existing_tender_ids)
final_result = []

# Iterate over the selected links and do something with them
for link in selected_links:
    full_link = "https://mahatenders.gov.in" + link["href"]
    tender_links.append(full_link)
    


# In[48]:


for link in tender_links:
    driver.get(link)
    time.sleep(5)
    html_source = driver.page_source
    # Parse the extracted HTML using BeautifulSoup
    soup = BeautifulSoup(html_source, 'html.parser')
    organisation_chain = soup.select_one("td.td_caption:contains('Organisation Chain') + td.td_field b").text
    tender_reference_number = soup.select_one("td.td_caption:contains('Tender Reference Number') + td.td_field b").text
    tender_id = soup.select_one("td.td_caption:contains('Tender ID') + td.td_field b").text
    if tender_id in existing_tender_ids:
        print(f"Skipping Tender ID: {tender_id} as it already exists in the file.")
        continue
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
    tender_inviting_authority_address = soup.find(is_address_text).find_next("td", class_="td_field").text

    if tender_id not in existing_tender_ids:
        # Click on the link to start the PDF download process
        try:
            pdf_download_link = driver.find_element(By.XPATH, '//a[contains(text(), "Tendernotice")]')
            pdf_download_link.click()
            time.sleep(10)  # Give some time for the download to start
            move_and_rename_latest_download(title)
            data["pdf_path"] = destination_path
        except:
            pass

    
   
    data = ({
        "organisation_chain" :organisation_chain,
        "tender_reference_number" :tender_reference_number,
        "tender_id" : tender_id,
        "form_of_contract"  :form_of_contract,
        "no_of_covers" :no_of_covers,
        "tender_fee" :tender_fee,
        "emd_amount" :emd_amount,
        "title" :title,
        "tender_value" :tender_value,
        "product_category" :product_category,
        "bid_opening_place" :bid_opening_place,
        "published_date" :published_date,
        "bid_opening_date" :bid_opening_date,
        "bid_submission_start_date" :bid_submission_start_date,
        "bid_submission_end_date" :bid_submission_end_date,
        "tender_inviting_authority_name":tender_inviting_authority_name,
        "tender_inviting_authority_address" :tender_inviting_authority_address,
        "tender_link" : link,
        "pdf_path": None
        
    })

    existing_tender_ids.add(tender_id)
    
    excel_filepath = os.path.join("/Users/kunaljuneja/Upwork/TenderClickup", f"{sanitize_filename(organization_name)}.csv")
    save_to_excel(data, excel_filepath)

    

