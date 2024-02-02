from operator import truediv
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
from datetime import datetime
import json
import os
import csv


def get_start_timestamp():
    # Generate a timestamp string in the format of M-D-hAPM-S
    timestamp = datetime.now().strftime('%m-%d-%I%p-%M-%S')

    return timestamp


class MySpider(scrapy.Spider):
    name = 'myspider'
    allowed_domains = ['spokeo.com']
    #SCRAPER SETTING!
    custom_settings = {
        'CONCURRENT_REQUESTS':1,
        'LOG_ENABLED': False, #DISABLE ALL LOGS
        
    }
    start_urls = []
    def __init__(self):
        
        # chrome_driver_path = r"/usr/local/bin/chromedriver"
        # options = uc.ChromeOptions()
        # options.headless = False
        # options.add_argument('--no-sandbox')
        # options.add_argument('--disable-dev-shm-usage')
        # self.browser = uc.Chrome(executable_path=chrome_driver_path, options=options)
        options = uc.ChromeOptions()
        options.headless = False
        options.binary_location = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        self.browser = uc.Chrome(driver_executable_path=r"/usr/local/bin/chromedriver", options=options)
        #options.user_data_dir = '/home/haris/.config/google-chrome/Defaultspeokeoo' #change your chrome profile path as per your machine. to find the path go to chrome://version 
        #options = uc.ChromeOptions()


        #options.user_data_dir = '/home/haris/.config/google-chrome/Defaultspeokeoo' #change your chrome profile path as per your machine. to find the path go to chrome://version 
        # self.browser = uc.Chrome(options=options,version_main=119)
        self.wait = WebDriverWait(self.browser, 10)
        # self.df = self.load_existing_data_from_s3('obit-bucket', 'savannah.csv')
        self.df = None


    def perform_search(self, name: str):
        # Wait for the input field to be interactable
        search_input = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".css-7eibf0.e5yecwe0")))
        # Clear the field before inputting text
        search_input.clear()
        # Enter the name
        search_input.send_keys(name)
        self.browser.find_element(By.ID, 'search').click()



    def login_spokeo(self,username: str, password: str):
        time.sleep(1)
        self.browser.find_element(By.XPATH, '//input[@id="email_address"]').send_keys(username)
        time.sleep(1)
        self.browser.find_element(By.XPATH, '//input[@id="email_address"]').send_keys(Keys.COMMAND + "a")
        self.browser.find_element(By.XPATH, '//input[@id="email_address"]').send_keys(Keys.BACK_SPACE)
        time.sleep(1)
        self.browser.find_element(By.XPATH, '//input[@id="email_address"]').send_keys(username)
        time.sleep(2)
        self.browser.find_element(By.ID, 'password').send_keys(password)
        time.sleep(2)
        self.browser.find_element(By.XPATH, '//button[@role="button"]').click()
        time.sleep(3)
        # print("Please solve the CAPTCHA... Resuming in 30 seconds")

    def search_by_name(self, name):
        # Wait until the search input is present and visible
        search_input_selector = '(//input[@aria-label="Search"])[position() = last()]'
        # search_input_selector = "input.header-search-input.css-buevma.e1po0p0y0"  # Update this selector if needed
        time.sleep(1)
        search_input = WebDriverWait(self.browser, 20).until(
            EC.visibility_of_element_located((By.XPATH, search_input_selector))
        )

        # Clear the field before inputting text
        search_input.send_keys(Keys.CONTROL + "a")
        search_input.send_keys(Keys.BACK_SPACE)

        # Enter the name into the search field and submit
        time.sleep(2)
        search_input.send_keys(name)
        time.sleep(2)
        search_input.send_keys(Keys.ENTER)
        time.sleep(35)
    def full_search(self, name):
            self.browser.get('https://www.spokeo.com/')
            time.sleep(1)
            # Perform search by name
            self.search_by_name(name)
            # time.sleep(1)

        
    def extract_property_details(self,response):
        All_property = []
        for property in response.xpath('//div[@class="tertiary-list-text css-1d3w5wq e1aoft386"]'):
            if re.match(r'^\d+', str(property.xpath('./div[@class="tertiary-list-title css-f6td22 e174g7f10"]/a/text()').get())):
                property_info = {'address': property.xpath('./div[@class="tertiary-list-title css-f6td22 e174g7f10"]/a/text()').get(),
                                 'location': ''.join(property.xpath('.//span[@class="primary css-10uw75o exrzi8t1"]/text()').get()),

                                 'duration' : ''.join(d for d in str(property.xpath('.//span[@class="secondary css-axcm68 exrzi8t0"]/text()').get()) if str(property.xpath('.//span[@class="secondary css-axcm68 exrzi8t0"]/text()').get())!=None),
                                'property_details'   :(''.join(x for x in property.xpath('.//div[@class="tertiary-list-description css-muifqk e1aoft385"]//text()').extract()))
                                 
                                 }
               
                All_property.append(property_info)


        return All_property
    
    def process_relatives(self,response):
        All_Relatives = []
        for rel in response.xpath('//div[@id="family-vertical-list"]//a[@class="button secondary vertical-list-item-button css-129j5g3 e63we282"]/@href'):
            relative = 'https://www.spokeo.com' + rel.get()

            self.browser.get(relative)
            self.browser.find_element(By.XPATH,'//a[contains(.,"View Detail")]').click()

            rel_response = Selector(text= self.browser.page_source)
            relative_info = {'name': rel_response.xpath('//h1[@id="summary-name"]/text()').get(),
                             'phone_numbers': rel_response.xpath('//h4[@class="contact-info-item-title css-l1p9op ei6wv05"]/@title[contains(.,"(")]').extract(),
                             'email_addresses': rel_response.xpath('//h4[@class="contact-info-item-title css-l1p9op ei6wv05"]/@title[contains(.,"@")]').extract(),
                             
                             }

            All_Relatives.append(relative_info)


        return All_Relatives
    def extract_addresses_with_dollar_sign(self, response):
        Addresses = []
        for address in response.xpath('//div[contains(@class, "tertiary-list-secondary-description") and contains(text(), "$")]/text()'):
            Addresses.append(address.get().strip())

        return Addresses

    
    

    @staticmethod
    def load_existing_data_from_s3(bucket_name, file_name):
        s3 = boto3.client('s3')
        try:
            obj = s3.get_object(Bucket=bucket_name, Key=file_name)
            df = pd.read_csv(obj['Body'])
            if 'Scraped' not in df.columns:
                df['Scraped'] = False
            return df
        except s3.exceptions.NoSuchKey:
            return pd.DataFrame(columns=['Name', 'Location', 'Age', 'Scraped'])
        
    

    def start_requests(self, result):

        #ADD the path of input file
       
        # self.perform_search('Robert A Fleming Jr, Age 85'
            #Fetching all the results profiles
        self.browser.get(result) #go the profile page
        time.sleep(1)
        self.browser.find_element(By.XPATH,'//a[contains(.,"View Detail")]').click()
        time.sleep(2)
        return scrapy.Request(url = 'https://www.spokeo.com/',callback=self.parse,meta={'html': self.browser.page_source,'url':self.browser.current_url,'handle_httpstatus_all': 'True'},dont_filter=True)
    
    def parse(self, response):
        resp = Selector(text=response.meta.get('html'))

        full_result = {
                'Result URL': response.meta.get('url'),
                'name': resp.xpath('//div[@id="summary-title"]/text()').get(),
                'phone_numbers': resp.xpath('//h4[@class="contact-info-item-title css-l1p9op ei6wv05"]/@title[contains(.,"(")]').extract(),
                'locations': resp.xpath('//li[@class="card-subtitle"]/span/text()').extract(),
                'email_addresses': resp.xpath('//h4[@class="contact-info-item-title css-l1p9op ei6wv05"]/@title[contains(.,"@")]').extract(),  # Ensure this method is updated
                'lived_at': self.extract_property_details(resp),
                'owned': self.extract_addresses_with_dollar_sign(resp),
                'relatives': self.process_relatives(resp),  # Ensure this method is updated

            }
        print(full_result)
        return full_result
        
    def run_bot(self, input_df):
        self.df = input_df
        full_results = []
        start_timestamp = get_start_timestamp()
        full_path = f"Spokeo Search Result -{start_timestamp}.csv"
        #full_path = f"Spokeo Search Results/{file_name}"
        with open(full_path, 'a') as csvfile:  
            csvwriter = csv.writer(csvfile)  
            fields = ['Result URL', 'name', 'phone_numbers', 'locations', 'email_addresses', 'lived_at', 'owned', 'relatives']
            csvwriter.writerow(fields)
        names = self.df.apply(lambda x: f'{x["Name"]}, {x["Location"]}, {x["Age"]}', axis=1)
        self.browser.get('https://www.spokeo.com/login')
        time.sleep(2)
        try:
                
            if self.browser.find_element(By.XPATH, '//input[@id="email_address"]'):
                self.login_spokeo('bwthompson12@gmail.com', 'BT12345678')
        except:
            pass
        for name in names:
            self.full_search(name)
            All_Result = []
            browser_current_url = None
            similars = 0
            self.browser.execute_script("window.scrollTo(0, window.scrollY + 200)")
            for data in self.browser.find_elements(By.XPATH,'//a[@class="button css-wxsd42 e1ndw42t0"]'):
                if browser_current_url == None:
                    browser_current_url = self.browser.current_url
                    All_Result.append(data.get_attribute('href'))
                else:
                    similars += 1
                    self.browser.get(browser_current_url)
                    time.sleep(0.5)
                    self.browser.execute_script("window.scrollTo(0, window.scrollY + 200)")
                    time.sleep(3)
                    try:
                        All_Result.append(data.get_attribute('href'))
                    except:
                        datas = self.browser.find_elements(By.XPATH,'//a[@class="button css-wxsd42 e1ndw42t0"]')
                        data = datas[similars]
                        All_Result.append(data.get_attribute('href'))
                #All_Result.append(data.get_attribute('href'))
           
           
            
            for result in All_Result:
                response = self.start_requests(result)
                temp = self.parse(response)
                full_results.append(temp)
                with open(full_path, 'a') as csvfile:  
                    csvwriter = csv.writer(csvfile)  
                    row = [temp['Result URL'], temp['name'], temp['phone_numbers'], temp['locations'], temp['email_addresses'], temp['lived_at'], temp['owned'], temp['relatives']]
                    csvwriter.writerow(row)  
                        # df = pd.DataFrame([temp])
                        # df.to_csv(full_path, sep = '\t', index = False)
        return full_results      