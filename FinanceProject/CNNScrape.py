import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

BASE_URL = "https://markets.money.cnn.com/research/quote/forecasts.asp?symb="

def extract_analyst_count(soup):
    for div in soup.find_all('div', class_='wsod_twoCol clearfix'):
        for paragraph in div.find_all('p'):
            if "The current consensus" in paragraph.text:
                match = re.search(r"\d{1,2}", paragraph.text)
                if match:
                    return int(match.group(0))
    return None

def get_cnn_forecast(symbol, stock_name):
    symbol = str(symbol)
    url = BASE_URL + symbol
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to retrieve forecast for {symbol} from CNN Money.")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    paragraph = soup.select_one(".wsod_twoCol.clearfix p")

    if not paragraph:
        print(f"Could not find forecast information for {symbol}.")
        return None

    try:
        # Extracting the required details from the paragraph
        median_target_match = re.search(r"median target of ([\d,]+)", paragraph.text)
        high_estimate_match = re.search(r"high estimate of ([\d,]+)", paragraph.text)
        low_estimate_match = re.search(r"low estimate of ([\d,]+)", paragraph.text)
        median_estimate_match = re.search(r"represents a ([+\-]?[\d.]+%)", paragraph.text)
        last_price_match = re.search(r"from the last price of ([\d.]+)", paragraph.text)
        analyst_count_match = re.search(r"The (\d+) analysts offering", paragraph.text)

        if not (median_target_match and high_estimate_match and low_estimate_match and median_estimate_match and analyst_count_match):
            print(f"Failed to extract forecast details for {symbol}. The content structure might be different.")
            return None

        median_target = median_target_match.group(1).replace(',', '')
        high_estimate = high_estimate_match.group(1).replace(',', '')
        low_estimate = low_estimate_match.group(1).replace(',', '')
        median_estimate = median_estimate_match.group(1)
        last_price = last_price_match.group(1) if last_price_match else "N/A"
        analyst_count = analyst_count_match.group(1)

        # Printing the fetched data
        print(f"Symbol: {symbol}")
        print(f"Stock Name: {stock_name}")
        print(f"Median Target: {median_target}")
        print(f"High Estimate: {high_estimate}")
        print(f"Low Estimate: {low_estimate}")
        print(f"Median Estimate: {median_estimate}")
        print(f"Last Price: {last_price}")
        print(f"Analyst Count: {analyst_count}\n")  # Printing the Analyst Count

        return {
            "Symbol": symbol,
            "Stock Name": stock_name,
            "Median Target": median_target,
            "High Estimate": high_estimate,
            "Low Estimate": low_estimate,
            "Median Estimate": median_estimate,
            "Last Price": last_price,
            "Analyst Count": analyst_count
        }
    except Exception as e:
        print(f"Failed to extract forecast details for {symbol}. Error: {e}")
        return None

# Load symbols and names from the CSV
df_nasdaq = pd.read_csv("/Users/kunaljuneja/Upwork/FinanceProject/nasdaq_tickers_with_names ALL.csv")
symbols_names = df_nasdaq[['Symbol', 'name']].to_dict(orient='records')

# Extract forecast data
forecast_data = [get_cnn_forecast(record['Symbol'], record['name']) for record in symbols_names]
forecast_data = [f for f in forecast_data if f]  # Remove any None values

# Convert to DataFrame and save to CSV
df_forecast = pd.DataFrame(forecast_data)
df_forecast.to_csv("nasdaq_forecasts1.csv", index=False)

print("Saved forecasts to nasdaq_forecasts.csv")
