import urllib.request

import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from selenium import webdriver
from selenium.webdriver.common.by import By
import json
import feedparser
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
import statistics
import datetime
import pathlib
import re
import os
import boto3
import shutil
from jdFinder4 import *
from fetchClientName3 import extract_client_name


class Job_Scraper:
    def __init__(self):

        # Initialize Firefox WebDriver with options and GeckoDriver path

        cluster = MongoClient(
            "mongodb+srv://marina:gqTFE1S0fwr8goGZ@cluster0.u75kq1t.mongodb.net/?retryWrites=true&w=majority&appName=AtlasApp")

        self.db = cluster['vitaver']['jobs']

        self.Bucket_name = "vitavers3bucket"

        self.s3 = boto3.client('s3', aws_access_key_id='AKIA265QHS6RBURYM5PA',
                               aws_secret_access_key='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')

    def setup_browser(self):
        options = EdgeOptions()

        # Set download folder preferences
        options.add_experimental_option("prefs", {
            "download.default_directory": str(pathlib.Path(__file__).parent.resolve()),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })

        # Set MIME types to automatically save without prompting
        options.add_experimental_option("prefs", {
            "download.extensions_to_open": "",
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "download.default_directory": str(pathlib.Path(__file__).parent.resolve())
        })

        # Create the Edge browser instance with the specified options
        self.driver = webdriver.Edge(options=options, service=EdgeService())

        # Set the desired MIME type to automatically save without prompting (application/pdf)
        self.driver.execute_cdp_cmd("Page.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": str(pathlib.Path(__file__).parent.resolve()),
            "extensionsToOpen": []
        })

    def attachment_scraper(self, jds, data):
        self.dump_data_into_mongo(data)
        for file in jds:
            self.dump_files_into_aws(file)

        for file in jds:
            if os.path.exists(file):
                os.remove(file)

    def body_scraper(self, jds, data):
        self.dump_data_into_mongo(data)
        for file in jds:
            self.dump_files_into_aws(file)

        for file in jds:
            if os.path.exists(file):
                os.remove(file)

    def logout(self):
        self.driver.quit()

        options = EdgeOptions()

        # Set download folder preferences
        options.add_experimental_option("prefs", {
            "download.default_directory": str(pathlib.Path(__file__).parent.resolve()),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })

        # Set MIME types to automatically save without prompting
        options.add_experimental_option("prefs", {
            "download.extensions_to_open": "",
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "download.default_directory": str(pathlib.Path(__file__).parent.resolve())
        })

        # Create the Edge browser instance with the specified options
        self.driver = webdriver.Edge(options=options, service=EdgeService())

        # Set the desired MIME type to automatically save without prompting (application/pdf)
        self.driver.execute_cdp_cmd("Page.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": str(pathlib.Path(__file__).parent.resolve()),
            "extensionsToOpen": []
        })

    def login(self, lnk, credentials):
        if 'fieldglass' in lnk:
            self.driver.get(lnk)
            try:
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="usernameId_new"]'))
                )
            except:
                print("Timeout occurred. Page may not be fully loaded.")

            try:
                self.driver.find_element(By.XPATH, '//*[@id="usernameId_new"]').send_keys(credentials[0])
                time.sleep(1)
                self.driver.find_element(By.XPATH, '//*[@id="passwordId_new"]').send_keys(credentials[1])
                time.sleep(1)
                self.driver.find_element(By.XPATH, '//*[@type="submit"]').click()
                time.sleep(10)
            except:
                pass
        elif 'ariba' in lnk:

            self.driver.get(lnk)
            try:
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="userid"]'))
                )
            except:
                print("Timeout occurred. Page may not be fully loaded.")
            try:
                self.driver.find_element(By.XPATH, '//*[@id="userid"]').send_keys(credentials[0])
                time.sleep(1)
                self.driver.find_element(By.XPATH, '//*[@id="_czgbx"]').click()
                try:
                    WebDriverWait(self.driver, 30).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="Password"]'))
                    )
                except:
                    print("Timeout occurred. Page may not be fully loaded.")
                self.driver.find_element(By.XPATH, '//*[@id="Password"]').send_keys(credentials[1])
                time.sleep(1)
                self.driver.find_element(By.XPATH, '//*[@type="submit"]').click()
                time.sleep(10)
            except:
                pass
        elif 'lotus' in lnk:
            try:
                self.driver.get('https://www.lotusconnect.com/')
                try:
                    WebDriverWait(self.driver, 30).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="email"]'))
                    )
                except:
                    print("Timeout occurred. Page may not be fully loaded.")

                self.driver.find_element(By.XPATH, '//*[@id="email"]').send_keys(credentials[0])
                time.sleep(1)
                self.driver.find_element(By.XPATH, '//*[@type="submit"]').click()
                try:
                    WebDriverWait(self.driver, 30).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="password"]'))
                    )
                except:
                    print("Timeout occurred. Page may not be fully loaded.")
                self.driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(credentials[1])
                time.sleep(1)
                self.driver.find_element(By.XPATH, '//*[@type="submit"]').click()
                time.sleep(10)
            except:
                pass
        else:
            self.driver.get(lnk)
            try:
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="userid"]'))
                )
            except:
                print("Timeout occurred. Page may not be fully loaded.")
            try:

                self.driver.find_element(By.XPATH, '//*[@id="userid"]').send_keys(credentials[0])
                time.sleep(1)
                self.driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(credentials[1])
                time.sleep(1)
                # selector for submit
                self.driver.find_element(By.XPATH, '//*[@id="btnActive"]').click()
                time.sleep(10)
            except:
                pass

    def string_to_pdf(self, input_string, output_file):
        # Create a PDF document
        doc = SimpleDocTemplate(output_file, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Split the input string into paragraphs
        paragraphs = input_string.split('\n\n')

        # Create a Paragraph object for each paragraph
        for paragraph in paragraphs:
            p = Paragraph(paragraph, styles["Normal"])
            story.append(p)

        # Build the PDF document
        doc.build(story)

    def fieldGlass_scraper(self, lnk, cred, message_id, message_type, client_system, body):
        self.login(lnk, cred)
        self.driver.get(lnk)
        self.driver.maximize_window()
        files = []
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="signOut"]'))
            )
        except:
            print("Timeout occurred. Page may not be fully loaded.")
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//*[@data-help-id="LABEL_BUYER_40"]/div[@class="values"]'))
            )
        except:
            print("Timeout occurred. Page may not be fully loaded.")

        client_system = client_system

        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@data-help-id="LABEL_JOBPOSTING_REF_40"]/div[@class="values"]'))
            )
        except:
            print("Timeout occurred. Page may not be fully loaded.")
        try:
            requisition_id = self.driver.find_element(by=By.XPATH,
                                                      value='//*[@data-help-id="LABEL_JOBPOSTING_REF_40"]/div[@class="values"]').text
            time.sleep(1)
        except:
            requisition_id = ''

        try:
            period = self.driver.find_element(by=By.XPATH,
                                              value='//*[@data-help-id="LABEL_PERIOD_40"]/div[@class="values"]').text
            time.sleep(1)
        except:
            period = ''

        try:
            bill_rate_range = self.driver.find_element(by=By.XPATH,
                                                       value='//*[@fgid="Target Bill Rate Range"]//*[@class="cfValue"]/div/div[@class="diff-part-value "]').text
            time.sleep(1)
        except:
            try:
                bill_rate_range = self.driver.find_element(by=By.XPATH,
                                                           value='//*[text()="Bill Rate"]/parent::tr/td[@class=" rightborder bottomborder numericFieldBold norightborder"]').text
            except:
                bill_rate_range = ''
        try:
            shift_type = self.driver.find_element(by=By.XPATH,
                                                  value='//*[@fgid="Shift Type"]//*[@class="cfValue"]/div/div[@class="diff-part-value "]').text
            time.sleep(1)
        except:
            shift_type = ''
        try:
            job_role = self.driver.find_element(by=By.XPATH,
                                                value='//*[@id="jpBadge"]//div[@class="titleHolderGridDiv"]/div/span').text
            time.sleep(1)
        except:
            job_role = ''
        try:
            location = self.driver.find_elements(by=By.XPATH,
                                                 value='//*[text()="Work Location:"]/following::div')[0].text
            time.sleep(1)
        except:
            location = ''

        try:
            job_category = self.driver.find_element(by=By.XPATH, value='//*[text()="Category"]/parent::tr/td').text
            time.sleep(1)
        except:
            job_category = ''
        try:
            positions_requested = self.driver.find_element(by=By.XPATH,
                                                           value='//*[@id="positionsAvailable"]/td').text
            time.sleep(1)
        except:
            positions_requested = ''
        try:
            hours_per_day = self.driver.find_element(by=By.XPATH,
                                                     value='//*[text()="Hours per Day"]/parent::tr/td').text
            time.sleep(1)
        except:
            hours_per_day = ''
        try:
            hours_per_week = self.driver.find_element(by=By.XPATH,
                                                      value='//*[text()="Hours per Week"]/parent::tr/td').text
            time.sleep(1)
        except:
            hours_per_week = ''
        try:
            total_hours = self.driver.find_element(by=By.XPATH,
                                                   value='//*[text()="Total Hours"]/parent::tr/td').text
            time.sleep(1)
        except:
            total_hours = ''

        files_data = []
        isInMongo = self.db.find_one({'requisition_id': requisition_id})
        if not isInMongo:
            try:  # Find attachments
                self.driver.find_element(by=By.XPATH,
                                         value='//*[@id="attachment_list"]//tr[@class="primaryRow"]/td/div/span').click()
                self.wait_for_download()

                filename = max([str(pathlib.Path(__file__).parent.resolve()) + "/" + f for f in
                                os.listdir(pathlib.Path(__file__).parent.resolve())], key=os.path.getctime)
                actual_filename = filename.split('/')[-1]
                timestamp = int(time.time())
                filename = f"{timestamp}_{actual_filename}"
                os.rename(actual_filename, filename)
                isValidJD = is_jd(filename)
                time.sleep(5)
                print("Is File a JD:", isValidJD)
                if isValidJD == "no":
                    ai_relevance = False
                else:
                    ai_relevance = True

                if ai_relevance:
                    # if filename.endswith("docx"):
                    #     if os.path.exists(filename):
                    #         os.remove(filename)  # Since we already have a PDF version generated by jdFinder
                    #     filename = filename.replace("docx", "pdf")
                    #     print(filename)

                    file_data = {"s3_key": 'JD/' + filename, "is_jd": True}
                    files_data.append(file_data)
                    files.append(filename)
                    self.dump_files_into_aws(filename)
            except:  # When No attachments
                try:
                    Jd_descript = self.driver.find_elements(by=By.XPATH, value='//*[@id="description"]//div')[1].text
                    time.sleep(1)
                    try:
                        Jd_descript += self.driver.find_element(by=By.XPATH,
                                                                value='//*[@fgid = "Additional Job Details"]//div[@class="diff-part-value "]').text
                    except:
                        print("No Additional Job Details")
                except:
                    print("No Job description")
                    Jd_descript = ""

                output = f"{str(int(time.time()))}_{job_role}.pdf"
                if Jd_descript != "":
                    self.string_to_pdf(Jd_descript, output)
                file_data = {"s3_key": 'JD/' + output, "is_jd": True}
                files_data.append(file_data)
                files.append(output)
                self.dump_files_into_aws(output)

            time.sleep(5)
            organization = self.get_organization(body, files)

            data = {
                'client_system': client_system,
                'requisition_id': requisition_id,
                'period': period,
                'organization': organization[0],
                'bill_rate_range': bill_rate_range,
                'shift_type': shift_type,
                'job_role': job_role,
                'location': location,
                'job_category': job_category,
                'positions_requested': positions_requested,
                'hours_per_day': hours_per_day,
                'hours_per_week': hours_per_week,
                'total_hours': total_hours,
                'JDs': files_data,
                'job_status': 'new',
                "message_id": message_id,
                'message_type': message_type,
                "job_link": str(lnk),
                "organization_id": organization[1]
            }

            self.dump_data_into_mongo(data)

            self.logout()

            for file in files:
                if os.path.exists(file):
                    os.remove(file)
        else:
            self.logout()

    def wait_for_download(self):
        time.sleep(30)

    def ariba_scraper(self, lnk, cred, message_id, message_type, client_system, body):

        self.login(lnk, cred)
        self.driver.get(lnk)
        self.driver.maximize_window()
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="lout"]'))
            )
        except:
            print("Timeout occurred. Page may not be fully loaded.")

        time.sleep(5)
        client_system = client_system
        try:
            reference_id = self.driver.find_element(by=By.XPATH,
                                                    value='//*[@id="_v$u7zb"]/td[@class="ffp-noedit"]').text
            time.sleep(2)
        except:
            reference_id = ''

        try:
            job_role = self.driver.find_element(by=By.XPATH, value='//*[@id="_0ogjl"]/td[@class="ffp-noedit"]').text
            word = job_role.split(' ')
            job_role = ''
            for each in range(len(word)):
                if each < 3:
                    continue
                job_role = job_role + word[each]
            time.sleep(1)
        except:
            job_role = ''
        try:
            total_hours = self.driver.find_element(by=By.XPATH, value='//*[@id="_rq5ynd"]').text

            time.sleep(1)
        except:
            total_hours = ''
        try:
            hourly_rate = self.driver.find_element(by=By.XPATH, value='//*[@id="_oqa8l"]').text
            time.sleep(1)
        except:
            hourly_rate = ''
        try:
            amount = self.driver.find_element(by=By.XPATH, value='//*[@id="_hhuvqc"]').text

            time.sleep(1)
        except:
            amount = ''
        try:
            self.driver.find_element(by=By.XPATH, value='//*[@id="_9mzdzc"]').click()
            time.sleep(3)
        except:
            print('link does not work')

        files = []
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="_ly2yt"]/tbody'))
            )
        except:
            print("Timeout occurred. Page may not be fully loaded.")

        files_data = []

        for docu in self.driver.find_elements(by=By.XPATH, value='//a[text()="Download"]'):
            try:
                docu.click()
                self.wait_for_download()
                filename = max([str(pathlib.Path(__file__).parent.resolve()) + "/" + f for f in
                                os.listdir(pathlib.Path(__file__).parent.resolve())], key=os.path.getctime)
                actual_filename = filename.split('/')[-1]
                timestamp = int(time.time())
                newfilename = f"{timestamp}_{actual_filename}"
                os.rename(actual_filename, newfilename)
                isValidJD = True if is_jd(newfilename) != "no" else False
                time.sleep(5)
                print("Is File a JD:", "yes" if isValidJD else "no")
                file_data = {"s3_key": 'JD/' + newfilename, "is_jd": isValidJD}
                files_data.append(file_data)
                files.append(newfilename)
                if isValidJD == "no":
                    ai_relevance = False
                else:
                    ai_relevance = True
                if ai_relevance:
                    self.dump_files_into_aws(newfilename)
            except:
                print('There is no Attachment')

        organization = self.get_organization(body, files)

        data = {
            'client_system': client_system,
            'reference_id': reference_id,
            'organization': organization[0],
            'job_role': job_role,
            'total_hours': total_hours,
            'hourly_rate': hourly_rate,
            'amount': amount,
            'JDs': files_data,
            'job_status': 'new',
            "message_id": message_id,
            'message_type': message_type,
            "job_link": str(lnk),
            "organization_id": organization[1]

        }

        self.dump_data_into_mongo(data)

        for file in files:
            if os.path.exists(file):
                os.remove(file)
        self.logout()

    def lotus_scraper(self, lnk, cred, message_id, message_type, client_system, body):

        self.login(lnk, cred)
        self.driver.get(lnk)
        self.driver.maximize_window()
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//*[@data-qa-id="topNavUserDropdown"]'))
            )
        except:
            print("Timeout occurred. Page may not be fully loaded.")
        self.driver.get(str(lnk))
        self.logout()

    def oracle_scraper(self, lnk, cred, message_id, message_type, client_system, body):
        self.login(lnk, cred)
        self.driver.get(lnk)
        self.driver.maximize_window()
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="_FOpt1:_UISlg1"]'))
            )
        except:
            print("Timeout occurred. Page may not be fully loaded.")
        time.sleep(3)

        client_system = client_system

        try:
            job_id = self.driver.find_element(by=By.XPATH,
                                              value='//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:Upl:UPsp1:SPcf1"]/span').text
            time.sleep(1)
        except:
            job_id = ''
        try:
            job_role = self.driver.find_element(by=By.XPATH,
                                                value='//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:Upl:UPsp1:SPph::_afrTtxt"]/h1').text
            time.sleep(1)
        except:
            job_role = ''

        try:
            job_family = self.driver.find_element(by=By.XPATH,
                                                  value='//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:Upl:UPsp1:jInfPse:jbFmInp::content"]').text
            time.sleep(1)
        except:
            job_family = ''
        try:
            location = self.driver.find_element(by=By.XPATH,
                                                value='//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:Upl:UPsp1:jInfPse:flNmInp::content"]').text
            time.sleep(1)
        except:
            location = ''
        try:
            full_or_part_time = self.driver.find_element(by=By.XPATH,
                                                         value='//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:Upl:UPsp1:jInfPse:ftPtInp::content"]').text
            time.sleep(1)
        except:
            full_or_part_time = ''
        try:
            travel_required = self.driver.find_element(by=By.XPATH,
                                                       value='//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:Upl:UPsp1:jInfPse:tlRqInp::content"]').text
            time.sleep(1)
        except:
            travel_required = ''
        try:
            job_description = self.driver.find_element(by=By.XPATH,
                                                       value='//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:Upl:UPsp1:jdPse:PSEroc"]').text
            time.sleep(1)
        except:
            job_description = ''
        try:
            hiring_manager = self.driver.find_elements(by=By.XPATH,
                                                       value='//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:Upl:UPsp1:cntPce:ctLv:0:ctsPgl"]/div')[
                0].text
        except:
            hiring_manager = ''
        try:
            hiring_manager_email = self.driver.find_element(by=By.XPATH,
                                                            value='//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:Upl:UPsp1:cntPce:ctLv:0:emlgl"]').text
        except:
            hiring_manager_email = ''
        try:
            recruiter = self.driver.find_elements(by=By.XPATH,
                                                  value='//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:Upl:UPsp1:cntPce:ctLv:1:ctsPgl"]')[
                0].text
        except:
            recruiter = ''
        try:
            recruiter_email = self.driver.find_element(by=By.XPATH,
                                                       value='//*[@id="_FOpt1:_FOr1:0:_FONSr2:0:MAnt2:2:Upl:UPsp1:cntPce:ctLv:1:emlgl"]').text
        except:
            recruiter_email = ''
        output = f"{str(int(time.time()))}_{client_system}.pdf"
        self.string_to_pdf(job_description, output)
        organization = self.get_organization(body, output)
        data = {'client_system': client_system, 'job_id': job_id, 'job_role': job_role, 'organization': organization[0],
                'job_family': job_family, 'location': location, 'full_or_part_time': full_or_part_time,
                'travel_required': travel_required, 'job_description': job_description,
                'hiring_manager': hiring_manager, 'hiring_manager_email': hiring_manager_email, 'recruiter': recruiter,
                'recruiter_email': recruiter_email, 'job_status': 'new', "organization_id": organization[1],
                "message_id": message_id,
                'message_type': message_type,
                "job_link": str(lnk)
                }
        self.dump_data_into_mongo(data)
        self.logout()

    def get_organization(self, body, attachment):
        if not attachment:
            attachment = ""
        client = extract_client_name(attachment[0], body)
        temp = None
        for key in client:
            temp = (key, client[key])

        return temp

    def dump_data_into_mongo(self, data):
        self.db.insert_one(data)

    def dump_files_into_aws(self, filename=None):
        if filename is None:
            filename = max([str(pathlib.Path(__file__).parent.resolve()) + "/" + f for f in
                            os.listdir(pathlib.Path(__file__).parent.resolve())], key=os.path.getctime)
            filename = filename.split('/')[-1]
        self.s3.upload_file(filename, self.Bucket_name, f"JD/{filename}")

    def run(self, message_id, message_type, lnk=None, jds=None, data=None, site=None, cred=None, client_system=None,
            body=None):
        if message_type == "jd_as_link":
            if 'fieldglass' in site:
                self.fieldGlass_scraper(lnk, cred, message_id, message_type, client_system, body)
            elif 'ariba' in site:
                self.ariba_scraper(lnk, cred, message_id, message_type, client_system, body)
            elif 'lotus' in site:
                self.lotus_scraper(lnk, cred, message_id, message_type, client_system, body)
            else:
                self.oracle_scraper(lnk, cred, message_id, message_type, client_system, body)
        elif message_type == "jd_as_attachment":
            self.attachment_scraper(jds, data)
        else:
            self.body_scraper(jds, data)
