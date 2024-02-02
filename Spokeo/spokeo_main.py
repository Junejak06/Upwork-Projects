import scrapy
from scrapy.crawler import CrawlerProcess
import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
from scrapy.selector import Selector
import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pandas as pd
import boto3
from io import StringIO
from spokeo_bot import MySpider

def run():
    input_df = pd.read_csv('Spokeo/savannahshort.csv')
    spider = MySpider()
    results = spider.run_bot(input_df)  # Get the results

    # Convert results to DataFrame
    results_df = pd.DataFrame(results)

    # Save to CSV
    results_df.to_csv('scraped_data.csv', index=False)

    return results_df

if __name__ == '__main__':
    df = run()
    print(df)  # Display the DataFrame
