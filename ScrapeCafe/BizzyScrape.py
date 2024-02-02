import pandas as pd
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException, \
    JavascriptException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
import ssl
import os
import openpyxl


# For SSL issue
ssl._create_default_https_context = ssl._create_unverified_context

options = uc.ChromeOptions()
options.binary_location = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
driver = uc.Chrome(driver_executable_path=r"/usr/local/bin/chromedriver", options=options)

driver.get('https://bizzy.org/en/login?incentive=HEADER&returnPath=%2Fen')

def scroll_to_element(driver, element):
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    time.sleep(1)  # Adjust time as necessary for the page to settle

# Function to click using JavaScript
def js_click(driver, element):
    driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true, view: window}));", element)



# Wait for the cookies acceptance button to appear and then click it
try:
    accept_cookies_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@class='styles_button__ljEg8 styles_accept__dqSGH']"))
    )
    accept_cookies_button.click()
except (NoSuchElementException, TimeoutException):
    print("Could not find the 'Accept all cookies' button or it took too long to load.")

try:
    google_sign_in_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@class='styles_sso__BpVXS styles_signInGoogle__QfQjP']//div[1]"))
    )

    # Use ActionChains to Ctrl+Click (Cmd+Click on macOS) on the element
    actions = ActionChains(driver)

    # For macOS use Keys.COMMAND, for others use Keys.CONTROL
    actions.key_down(Keys.COMMAND if os.name == 'posix' else Keys.CONTROL).click(google_sign_in_button).key_up(
        Keys.COMMAND if os.name == 'posix' else Keys.CONTROL).perform()

    # Wait a bit to ensure the new tab is opened
    time.sleep(2)

    # Switch to the new tab
    driver.switch_to.window(driver.window_handles[-1])

except (NoSuchElementException, TimeoutException):
    print("Could not find the Google sign-in button or it took too long to load.")

try:
    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='email']"))
    )
    email_input.send_keys('testbizzy955@gmail.com')
except (NoSuchElementException, TimeoutException):
    print("Could not find the email input field or it took too long to load.")

# Click 'Next' after email
try:
    next_button_email = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH,
                                    "//button[contains(@class, 'VfPpkd-LgbsSe-OWXEXe-k8QpJ') and contains(@jsname, 'LgbsSe')][span[text()='Next']]"))
    )
    next_button_email.click()
except (NoSuchElementException, TimeoutException):
    print("Could not find the 'Next' button after email or it took too long to load.")

# Continue with the password input

time.sleep(3)

# Input Password
try:
    password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='password']"))
    )
    password_input.send_keys('Bizzy@123')
except (NoSuchElementException, TimeoutException):
    print("Could not find the password input field or it took too long to load.")

time.sleep(3)

# Click 'Next' after password
try:
    next_button_password = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH,
                                    "//button[contains(@class, 'VfPpkd-LgbsSe-OWXEXe-k8QpJ') and contains(@jsname, 'LgbsSe')][span[text()='Next']]"))
    )
    next_button_password.click()
except (NoSuchElementException, TimeoutException):
    print("Could not find the 'Next' button after password or it took too long to load.")

driver.switch_to.window(driver.window_handles[0])

time.sleep(8)

df = pd.read_excel('output 10.xlsx')

if not os.path.exists('combined_output6.xlsx'):
    df_combined = pd.DataFrame(columns=['URL', 'Phone Number', 'Email'])
else:
    df_combined = pd.read_excel('combined_output6.xlsx')

base_url = "https://bizzy.org/en/be/"
# Assuming numbers are in the first column, adjust if they're elsewhere
urls = [base_url + str(num).replace(".", "") + '/' for num in df.iloc[1:, 0]]  # Skips the first row (header)

# Create empty lists to store the scraped data
emails = []
phone_numbers = []

for url in urls:
    driver.get(url)
    time.sleep(3)  # giving the page some time to load

    # Absolute XPath you provided
    abs_xpath = "/html[1]/body[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[3]/div[2]/div[2]/div[1]/div[1]/div[1]/div[3]/div[4]/div[1]/div[1]/div[2]/div[1]/div[1]/div[3]/*[name()='svg'][1]"

    try:
        # Wait for the phone number element to be present
        phone_num_element = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, abs_xpath))
        )
        # Click the phone number element
        phone_num_element.click()
    except Exception as e:
        print("An error occurred:", str(e))

    try:
        # Extract phone number from the new element
        phone_num_element = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, "//a[starts-with(normalize-space(),'+')]"))
        )
        phone_number = phone_num_element.text
    except (NoSuchElementException, TimeoutException):
        phone_number = 'Not Found'

    phone_numbers.append(phone_number)
    print(f"Phone Number: {phone_number}")

    email = 'Not Found'  # Default assignment in case email is not found

    # Xpath for the email button
    email_button_xpath = "//div[@class='styles_contactAndSocialsBlock__xOOo0 styles_noLeftTopPadding__SILnA']//div[@class='styles_contactButton___XkFT styles_contactButtonEnabled__CXAYY']//*[name()='svg']//*[name()='path' and contains(@d,'M22 6c0-1.')]"

    try:
        email_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, email_button_xpath))
        )
        scroll_to_element(driver, email_button)  # Scroll to the element
        try:
            email_button.click()  # Try normal click first
        except ElementClickInterceptedException:
            js_click(driver, email_button)  # Fallback to JS click if normal click fails

        # Now wait for the email to be present after the click
        email_element = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(normalize-space(),'@')]"))
        )
        email = email_element.text
    except (ElementClickInterceptedException, JavascriptException, NoSuchElementException, TimeoutException) as e:
        print(f"Error occurred when extracting email for {url}: {str(e)}")

    emails.append(email)
    print(f"Email: {email}")

    new_row = {'URL': url, 'Phone Number': phone_number, 'Email': email}
    df_combined = pd.concat([df_combined, pd.DataFrame([new_row])], ignore_index=True)

    # Save the DataFrame to Excel after each iteration
    with pd.ExcelWriter('combined_output6.xlsx', mode='w', engine='openpyxl') as writer:
        df_combined.to_excel(writer, index=False)

    # Providing feedback in the console
    print(f"Data for {url} saved to combined_output6.xlsx")

# If you want to print a message after completing all the scraping
print("All data scraped and saved to combined_output6.xlsx")