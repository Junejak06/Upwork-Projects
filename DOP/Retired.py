import pandas as pd
from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import ssl
import os
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows


# For SSL issue
ssl._create_default_https_context = ssl._create_unverified_context

def get_cell_text(cell):
    return cell.get_text(strip=True) if cell else ''

def extract_service_history(soup):
    service_history = []
    service_table = soup.find('table', {'id': 'gv_Shistory'})
    if service_table:
        for row in service_table.find_all('tr')[2:]:
            cells = row.find_all('td')
            if len(cells) >= 4:
                history = {
                    'SNO': get_cell_text(cells[0]),
                    'Post Held by Officer': get_cell_text(cells[1]),
                    'Order Joining': get_cell_text(cells[2]),
                    'Date To': get_cell_text(cells[3])
                }
                service_history.append(history)
    return service_history

def extract_additional_charges(soup):
    additional_charges = []
    charges_table = soup.find('table', {'id': 'grid_Addi'})
    if charges_table:
        for row in charges_table.find_all('tr')[2:]:
            cells = row.find_all('td')
            if len(cells) >= 4:
                charge = {
                    'SNO': get_cell_text(cells[0]),
                    'Additional Post Held by Officer': get_cell_text(cells[1]),
                    'Additional Officer Order Joining': get_cell_text(cells[2]),
                    'Relieving': get_cell_text(cells[3])
                }
                additional_charges.append(charge)
    return additional_charges

def extract_training_details(soup):
    training_details = []
    # Locate the table inside the div with id 'div_lbl1'
    training_div = soup.find('div', {'id': 'div_lbl1'})
    if training_div:
        training_table = training_div.find('table')
        if training_table:
            rows = training_table.find_all('tr')[2:]  # Skipping the header rows
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 6:  # Checking if the row has sufficient cells
                    detail = {
                        'SNO': get_cell_text(cells[0]),
                        'Year': get_cell_text(cells[1]),
                        'Training Name': get_cell_text(cells[2]),
                        'Institute': get_cell_text(cells[3]),
                        'Place': get_cell_text(cells[4]),
                        'Duration (Days)': get_cell_text(cells[5])
                    }
                    training_details.append(detail)
    return training_details


def get_max_length(*dataframes):
    return max(len(df) for df in dataframes if df is not None)


def append_to_excel(filename, service_type,  personal_details, service_history, additional_charges, training_details):
    # Column headers based on the provided structure
    column_headers = [
        'UniqueID', 'Service Type', 'Name of Officer', 'Date of Birth', 'Home Town',
        'Qualification', 'Present Posting', 'SNO', 'Post Held by Officer', 'Order Joining',
        'Date To', 'Additional Post Held by Officer', 'Additional Officer Order Joining', 'Relieving', 'Year', 'Training Name',
        'Institute', 'Place', 'Duration (Days)'
    ]

    # Create an empty DataFrame with the column headers
    df = pd.DataFrame(columns=column_headers)

    # Build each row and append it to the DataFrame
    rows_list = []
    max_length = max(len(service_history), len(additional_charges), len(training_details))

    # Add personal details only to the first row
    for i in range(max_length):
        row = {header: '' for header in column_headers}  # Initialize all cells as empty

        if i == 0:  # Only add personal details to the first row
            row.update(personal_details)

        if i < len(service_history):
            row.update(service_history[i])

        if i < len(additional_charges):
            row.update(additional_charges[i])

        if i < len(training_details):
            row.update(training_details[i])

        rows_list.append(row)

    # Concatenate the list of rows into the DataFrame
    df = pd.concat([df, pd.DataFrame(rows_list)], ignore_index=True)

    # Write to Excel
    if not os.path.exists(filename):
        df.to_excel(filename, index=False)
    else:
        # Append to existing file
        with pd.ExcelWriter(filename, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
            df.to_excel(writer, sheet_name='Sheet1', startrow=writer.sheets['Sheet1'].max_row, index=False,
                        header=False)

def ensure_radio_button_state():
    try:
        radio_button = driver.find_element(By.ID, radio_button_id)
        if not radio_button.is_selected():
            radio_button.click()
            # Wait for the state change to reflect on the page
            wait.until(EC.presence_of_element_located((By.ID, 'ddl_officername')))
    except NoSuchElementException:
        print("Radio button not found!")


options = uc.ChromeOptions()
driver = uc.Chrome(driver_executable_path=r"/usr/local/bin/chromedriver", options=options)

# Navigate to the website
url = 'https://dop.rajasthan.gov.in/forms/CivilType_history.aspx'
driver.get(url)

wait = WebDriverWait(driver, 3)
radio_button_id = 'RadioButtonList1_1'

# Ensure the radio button is in the correct state
ensure_radio_button_state()

all_data = []

# Get service types text once and store it in a list
service_select = Select(driver.find_element(By.ID, 'ddl_ciniltype'))
service_texts = [option.text for option in service_select.options if option.get_attribute('value') != '0']

service_counter = {}

# Iterate over each service type
for service_index, service_text in enumerate(service_texts, start=1):  # Start at 1 to skip 'Select' option
    try:
        # Ensure radio button state
        ensure_radio_button_state()

        # Select service type
        service_select = Select(driver.find_element(By.ID, 'ddl_ciniltype'))
        service_select.select_by_index(service_index)
        service_type = service_text.strip()
        service_counter[service_type] = service_counter.get(service_type, 0)
        wait.until(EC.presence_of_element_located((By.ID, 'ddl_officername')))

        # Iterate over officers
        officer_select = Select(driver.find_element(By.ID, 'ddl_officername'))
        officers = officer_select.options

        for officer_index in range(1, len(officers)):  # Skipping the 'Select' option
            try:
                # Ensure radio button state
                ensure_radio_button_state()
                # Select officer
                officer_select = Select(driver.find_element(By.ID, 'ddl_officername'))
                officer_select.select_by_index(officer_index)
                try:
                    wait.until(EC.presence_of_element_located((By.ID, 'gv_Shistory')))
                    # Proceed with actions if the element is found
                except TimeoutException:
                    print("Element with ID 'gv_Shistory' not found. Skipping to next officer.")
                    continue  # Skip to the next iteration

                # Scrape data for the officer
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                personal_table = soup.find('table', {'class': 'mTable'})
                personal_details = {}
                service_counter[service_type] += 1
                personal_details['UniqueID'] = f"{service_type}{service_counter[service_type]}"
                personal_details['Service Type'] = service_type
                if personal_table:
                    rows = personal_table.find_all('tr')
                    if len(rows) > 1:
                        personal_details['Name of Officer'] = rows[1].find('span', {'id': 'lbl_name'}).get_text(strip=True) if rows[1].find('span', {'id': 'lbl_name'}) else ''
                        personal_details['Date of Birth'] = rows[2].find('span', {'id': 'lbl_DOB'}).get_text(strip=True) if rows[2].find('span', {'id': 'lbl_DOB'}) else ''
                        personal_details['Home Town'] = rows[3].find('span', {'id': 'lbl_Htown'}).get_text(strip=True) if rows[3].find('span', {'id': 'lbl_Htown'}) else ''
                        personal_details['Qualification'] = rows[4].find('span', {'id': 'lbl_Quli'}).get_text(strip=True) if rows[4].find('span', {'id': 'lbl_Quli'}) else ''
                        personal_details['Present Posting'] = rows[5].find('span', {'id': 'lbl_Posting'}).get_text(strip=True) if rows[5].find('span', {'id': 'lbl_Posting'}) else ''

                service_history = extract_service_history(soup)
                additional_charges = extract_additional_charges(soup)
                training_details = extract_training_details(soup)

                append_to_excel('Retired_Officer_Details2.xlsx', service_type, personal_details, service_history,
                                additional_charges, training_details)

                # Navigate back to select next officer
                driver.back()
                ensure_radio_button_state()
                service_select = Select(driver.find_element(By.ID, 'ddl_ciniltype'))
                service_select.select_by_index(service_index)
                wait.until(EC.presence_of_element_located((By.ID, 'ddl_officername')))

            except NoSuchElementException:
                print(f"Officer not found at index {officer_index}, skipping to next.")
                continue

    except NoSuchElementException:
        print(f"Service type not found at index {service_index}, continuing to next.")
        continue

print(f"Data extraction complete. Excel file saved")


driver.quit()