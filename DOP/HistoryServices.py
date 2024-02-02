import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import ssl
import time
import re
import os
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows


# For SSL issue
ssl._create_default_https_context = ssl._create_unverified_context
options = uc.ChromeOptions()
options.add_argument('--headless')  # Run in headless mode
options.add_argument('--disable-gpu')  # Disable GPU hardware acceleration
options.add_argument('--window-size=1920x1080')  # Specify window size
driver = uc.Chrome(driver_executable_path=r"/usr/local/bin/chromedriver", options=options)


# Navigate to the webpage
driver.get('https://dop.rajasthan.gov.in/forms/newhistoryform.aspx')

# Wait for the page to load
time.sleep(3)

# Create DataFrame to store scraped data
all_data = pd.DataFrame()

# Find the department dropdown
department_select = Select(driver.find_element(By.ID, 'ddl_DEPT'))

# Iterate through each department in the dropdown
for department_index in range(1, len(department_select.options)):  # Skip the 'Select' option
    department_select = Select(driver.find_element(By.ID, 'ddl_DEPT'))
    department_select.select_by_index(department_index)
    time.sleep(2)  # Wait for the page to load after selection
    department_select = Select(driver.find_element(By.ID, 'ddl_DEPT'))  # Re-locate the dropdown
    selected_department = department_select.first_selected_option.text

    designation_select = Select(driver.find_element(By.ID, 'ddldesignation'))

    for designation_index in range(1, len(designation_select.options)):
        designation_select = Select(driver.find_element(By.ID, 'ddldesignation'))
        designation_select.select_by_index(designation_index)
        time.sleep(2)  # Wait for the page to load after selection
        designation_select = Select(driver.find_element(By.ID, 'ddldesignation'))  # Re-locate the dropdown
        selected_designation = designation_select.first_selected_option.text

        driver.find_element(By.ID, 'Button1').click()  # Click the 'Find' button
        time.sleep(2)  # Wait for the table to load

        # Get the page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find all tables with IDs starting with 'gv_'
        tables = soup.find_all('table', id=re.compile(r'^gv_'))

        for table in tables:
            service_type_suffix = table['id'][3:]
            service_type = "IAS" if service_type_suffix.lower() == "result" else service_type_suffix
            rows = table.find_all('tr')
            table_data = []


            for i, row in enumerate(rows[1:]):  # Skip the header row
                cols = row.find_all('td')
                cols = [ele.text.strip() for ele in cols]
                if i == 0:
                    cols.extend([selected_department, selected_designation, service_type])
                else:
                    cols.extend(['', '', ''])
                table_data.append(cols)

            temp_df = pd.DataFrame(table_data,
                                   columns=['SNO', 'POST DESCRIPTION', 'OFFICER NAME', 'ORDER DATE', 'JOIN DATE',
                                            'RELIEVING DATE', 'REMARKS', 'Department', 'Designation', 'Service Type'])
            all_data = pd.concat([all_data, temp_df], ignore_index=True)
            all_data.to_csv('PostHistroy_Services1.csv', index=False)



# Close the Selenium WebDriver
driver.quit()

print("Scraping complete. Data saved to 'scraped_data.csv'.")