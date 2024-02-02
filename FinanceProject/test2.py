
from bs4 import BeautifulSoup
import pandas as pd
import requests

# Read the CSV file
df = pd.read_csv('sp500_forecasts.csv')

# Function to scrape Yahoo Finance data using requests and BeautifulSoup
def scrape_yahoo_finance(symbol):
    try:
        url = f"https://finance.yahoo.com/quote/{symbol}?p={symbol}&.tsrc=fin-srch"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Scrape P/E Ratio
        pe_element = soup.find('td', text='PE Ratio (TTM)').find_next_sibling('td')
        pe_ratio = pe_element.text.strip().replace(',', '')

        # Scrape EPS
        eps_element = soup.find('td', text='EPS (TTM)').find_next_sibling('td')
        eps = eps_element.text.strip().replace(',', '')

        return pe_ratio, eps
    except Exception as e:
        print(f"Error scraping data for {symbol}: {e}")
        return None, None

# Function to convert percentage to decimal and handle negative values
def convert_to_decimal(percentage_string):
    if percentage_string in ['N/A', '']:
        return 0
    return float(percentage_string.strip('+%')) / 100

# Function to calculate intrinsic value using EPS, P/E, and growth rate
def calculate_intrinsic_value(eps, pe_ratio, median_estimate):
    try:
        if eps in ['N/A', ''] or pe_ratio in ['N/A', '']:
            return 'N/A'
        growth_rate = convert_to_decimal(median_estimate)
        return float(eps) * (1 + growth_rate) * float(pe_ratio)
    except Exception as e:
        print

# Add new columns to DataFrame
df['P/E'] = ''
df['EPS'] = ''
df['Intrinsic Value'] = ''

# Iterate over stock symbols and scrape data
for index, row in df.iterrows():
    symbol = row['Symbol']
    median_estimate = row['Median Estimate']
    pe, eps = scrape_yahoo_finance(symbol)
    if pe and eps:
        df.at[index, 'P/E'] = pe
        df.at[index, 'EPS'] = eps
        intrinsic_value = calculate_intrinsic_value(eps, pe, median_estimate)
        df.at[index, 'Intrinsic Value'] = intrinsic_value
        print(f"Symbol: {symbol}, P/E Ratio: {pe}, EPS: {eps}, Intrinsic Value: {intrinsic_value}")

# Save the updated DataFrame to a new CSV file
df.to_csv('updated_sp500_forecasts.csv', index=False)
