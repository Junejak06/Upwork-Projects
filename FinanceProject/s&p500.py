import yfinance as yf
import pandas as pd
import ssl

# For SSL issue
ssl._create_default_https_context = ssl._create_unverified_context

def get_nasdaq100_symbols():
    # Get the NASDAQ-100 ticker list
    table = pd.read_html('https://en.wikipedia.org/wiki/NASDAQ-100')
    # Adjust table index as needed to find the right table
    df = table[3]
    return df['Ticker'].tolist()

symbols = get_nasdaq100_symbols()

# Save to CSV
df_symbols = pd.DataFrame(symbols, columns=['Symbol'])
df_symbols.to_csv("nasdaq100_stocks.csv", index=False)

print(f"Saved NASDAQ-100 symbols to nasdaq100_stocks.csv")
