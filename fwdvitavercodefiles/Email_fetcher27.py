import imaplib
import email
import os
import pathlib
import re
import time
from datetime import datetime, timedelta
from email.mime.application import MIMEApplication

from bs4 import BeautifulSoup
from pymongo import MongoClient
import boto3
from email.header import decode_header
from Job_scraper34 import Job_Scraper
from jdFinder4 import *
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from xhtml2pdf import pisa
from io import BytesIO
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fetchClientName3 import extract_client_name

class EmailWorker:
    def __init__(self):
        self.imap = None
        self.imap_server = 'email9.luxsci.com'
        self.username = 'xyfd321@vitaver.com/ai1'
        self.emailid = 'xyfd321@vitaver.com'
        self.password = 'D2vuFEhBeA5+'
        
        cluster = MongoClient(
            "mongodb+srv://marina:gqTFE1S0fwr8goGZ@cluster0.u75kq1t.mongodb.net/?retryWrites=true&w=majority&appName=AtlasApp")

        self.db = cluster['vitaver']['emails']
        self.jobs_db = cluster['vitaver']['jobs']
        self.db_admin = cluster['admin_db']['client_data']
        self.Bucket_name = "vitavers3bucket"
        self.db_email = cluster['admin_db']['email_filter']

        self.dir = str(pathlib.Path(__file__).parent.resolve()) + "/"

        self.s3 = boto3.client('s3', aws_access_key_id='AKIA265QHS6RBURYM5PA',
                               aws_secret_access_key='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')

        self.jd_email = "jdfilter@vitaver.com"
        # self.jd_email = "pinaaki.aggarwal@gmail.com"
        self.smtp_server = self.imap_server

    def cleanDB(self):
        self.db.delete_many({})
        self.jobs_db.delete_many({})
        print("🧹Cleaned up MongoDB")
        objects = self.s3.list_objects_v2(Bucket=self.Bucket_name)

        # Iterate through the objects and delete them
        for obj in objects.get('Contents', []):
            self.s3.delete_object(Bucket=self.Bucket_name, Key=obj['Key'])
        print("🧹Cleaned up AWS S3")

    def setup(self):
        try:
            print("Now logging in to email.")
            self.imap = imaplib.IMAP4_SSL(self.imap_server)
            self.imap.login(self.username, self.password)
            print('📧Successfully logged in to email.')
        except Exception as e:
            print("Failed to connect to the IMAP server:", str(e))

    def forwardMail(self, subject, body, charset, subtype, jd=True, attachments=None):
        message = MIMEMultipart()
        message["From"] = self.emailid
        message["To"] = self.jd_email
        message["Subject"] = subject if jd else subject + " - Not a JD"
        subtyper = subtype.split("/")[1] if len(subtype.split("/")) > 1 else subtype
        # message.attach(MIMEText(body, _subtype=subtyper, _charset=charset))
        message.attach(MIMEText(body.encode('utf-8'), _subtype=subtyper, _charset='utf-8'))


        if attachments:
            for attach in attachments:
                with open(attach, 'rb') as pdf_file:
                    pdf_attachment = MIMEApplication(pdf_file.read(), _subtype='pdf')
                    pdf_attachment.add_header('Content-Disposition', f'attachment; filename={attach}')
                message.attach(pdf_attachment)

        try:
            smtp_server = smtplib.SMTP(self.smtp_server)
            smtp_server.starttls()
            smtp_server.login(self.username, self.password)
            # Send the email
            smtp_server.sendmail(self.emailid, self.jd_email, message.as_string())
            smtp_server.quit()
            print("Email forwarded successfully.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def dump_into_mongodb(self, data):
        self.db.insert_one(data)

    def get_organization(self, body, attachment):
        client = extract_client_name(jd=attachment, email=body)
        client_name = client['Client Name']
        client_id = client['Client ID']
        # temp = None
        # for key in client:
        #     temp = (key, client[key])

        # return temp
        return client_name,client_id

    def save_attachment(self, filename, attachment_content):
        # Function to save attachment content to a file
        with open(filename, "wb") as file:
            file.write(attachment_content)

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

    def read_emails(self, mailbox="INBOX"):
        # Calculate the date 24 hours ago from the current time
        twenty_four_hours_ago = datetime.now() - timedelta(hours=6)

        # Select the mailbox you want to read emails from
        try:
            self.imap.select(mailbox)
        except:
            return "Unable to select mailbox: {mailbox}"

        date_format = twenty_four_hours_ago.strftime("%d-%b-%Y")

        search_criteria = f'(SINCE "{date_format}")'
        # Search for all emails in the selected mailbox
        result, data = self.imap.search(None, search_criteria)

        if result != "OK":
            return "Error searching for emails."

        email_list = []

        # Fetch email IDs
        for num in data[0].split():
            result, message_data = self.imap.fetch(num, "(RFC822)")
            if result != "OK":
                continue

            # Parse the email content
            raw_email = message_data[0][1]
            msg = email.message_from_bytes(raw_email)

            # Extract email details
            subject, _ = decode_header(msg["Subject"])[0]
            from_, _ = decode_header(msg.get("From", ""))[0]
            date, _ = decode_header(msg["Date"])[0]
            message_id = msg["Message-ID"]

            email_data = {
                "Subject": subject,
                "From": from_,
                "Date": date,
                "Message-ID": message_id,
                "Body": "",
                "Body-Type": "",
                "charset": "",
                "Attachments": []  # Initialize as an empty list
            }

            # Extract the email body and attachments
            # if msg.is_multipart():
            #     for part in msg.walk():
            #         content_type = part.get_content_type()
            #         content_disposition = str(part.get("Content-Disposition"))

            #         if "attachment" in content_disposition:
            #             # This part is an attachment
            #             attachment = {
            #                 "filename": part.get_filename(),
            #                 "content": part.get_payload(decode=True)
            #             }
            #             email_data["Attachments"].append(attachment)
            #         else:
            #             # This part is not an attachment
            #             charset = part.get_content_charset()
            #             payload = part.get_payload(decode=True)
            #             if payload is not None:
            #                 if content_type == "text/html" and (
            #                         email_data["Body-Type"] == '' or email_data["Body-Type"] == "text/html"):
            #                     # Convert HTML content to plain text using html2text
            #                     email_data["Body"] += str(payload, charset)
            #                     email_data["Body-Type"] = "text/html"
            #                     email_data["charset"] = charset
            #                 if content_type == "text/plain" and (
            #                         email_data["Body-Type"] == '' or email_data["Body-Type"] == "text/plain"):
            #                     email_data["Body"] += str(payload, charset) if charset else str(payload)
            #                     email_data["Body-Type"] = "text/plain"
            #                     email_data["charset"] = charset
            # else:
            #     charset = msg.get_content_charset()
            #     email_data["Body"] = str(msg.get_payload(decode=True), charset)
            #     email_data["charset"] = charset

            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))

                    if "attachment" in content_disposition:
                        # This part is an attachment
                        attachment = {
                            "filename": part.get_filename(),
                            "content": part.get_payload(decode=True)
                        }
                        email_data["Attachments"].append(attachment)
                    else:
                        # This part is not an attachment
                        charset = part.get_content_charset()
                        payload = part.get_payload(decode=True)
                        if payload is not None:
                            if content_type == "text/html" and (
                                    email_data["Body-Type"] == '' or email_data["Body-Type"] == "text/html"):
                                # Convert HTML content to plain text using html2text
                                email_data["Body"] += str(payload, charset) if charset else payload.decode(errors='replace')
                                email_data["Body-Type"] = "text/html"
                                email_data["charset"] = charset
                            if content_type == "text/plain" and (
                                    email_data["Body-Type"] == '' or email_data["Body-Type"] == "text/plain"):
                                email_data["Body"] += str(payload, charset) if charset else payload.decode(errors='replace')
                                email_data["Body-Type"] = "text/plain"
                                email_data["charset"] = charset
            else:
                charset = msg.get_content_charset()
                payload = msg.get_payload(decode=True)
                email_data["Body"] = str(payload, charset) if charset else payload.decode(errors='replace')
                email_data["charset"] = charset

            email_list.append(email_data)

        return email_list

    def html_to_pdf(self, input_html, output_file):
        # Preprocess the HTML content
        preprocessed_html = self.preprocess_html(input_html)

        pdf_data = BytesIO()

        # Convert preprocessed HTML to PDF
        pisa_status = pisa.CreatePDF(preprocessed_html, pdf_data)
        if pisa_status.err:
            # Handle the PDF generation error gracefully
            print(f"Error converting HTML to PDF: {pisa_status.err}")
        else:
            # Save the PDF data to the output file
            pdf_data.seek(0)
            with open(output_file, 'wb') as pdf_file:
                pdf_file.write(pdf_data.read())

    def preprocess_html(self, html_content):
        # Replace "initial" with a default color value (e.g., black)
        modified_html = html_content.replace('color:initial', 'color: #000000;')
        return modified_html

    def get_content_from_a_tag(self, html_content):
        try:
            # Parse the HTML using Beautiful Soup
            soup = BeautifulSoup(html_content, 'html.parser')

            # Find the <a> tag containing the link
            a_tag = soup.find_all('a')

            # Extract the link (href) if the <a> tag is found
            for basic_a in a_tag:
                if basic_a:
                    link_href = basic_a.get('href')

                    if "fieldglass.net/job_posting_detail" in link_href or "ariba.com/Supplier.aw/ad/collabReqDetail" in link_href:
                        return link_href
                    # match_ttps = re.search(r'https://\S*/\S*', basic_a.get('href'))
                    # match_ttp = re.search(r'http://\S*/\S*', basic_a.get('href'))
                    # if match_ttps or match_ttp:
                    #     link_href = basic_a.get('href')
                    #     if "linkedin" in link_href.lower():
                    #         continue
                    #     return link_href
                else:
                    print("No <a> tag found in the HTML content.")
                    return None

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def run_loop(self):
        test = 0
        while True:
            print("Reading Emails....")
            email_list = self.read_emails()
            print("Emails Read.")
            for mail in email_list:
                print("Processing mail...")
                print(f"Type of mail: {type(mail)}")
                if isinstance(mail, str):
                    continue
                msg_id = mail["Message-ID"]
                Subject = mail["Subject"]

                if isinstance(Subject, bytes):
                    # Decode bytes to string using utf-8
                    Subject = Subject.decode('utf-8')
                elif isinstance(Subject, str):
                    # Subject is already a string
                    Subject = Subject


                invalid_char = ['\\', '/', '*', '<', '>', '|', '?', ':', "'", '"', '\n', '\r']
                for x in invalid_char:
                    Subject = Subject.replace(x, '')
                Subject = Subject.strip()
                Sender = mail["From"]
                received_at_timestamp = mail["Date"]
                Content = mail["Body"]
                ContentType = mail["Body-Type"]
                attachments = mail["Attachments"]
                charset = mail["charset"]
                relevant = True
                files = []
                email_filter = []

                msg_exists = self.db.find_one({"message_id": msg_id})
                if Sender == 'support@support.luxsci.com':
                    continue
                if not msg_exists:
                    email_cur = self.db_email.find()
                    for doc in email_cur:
                        email_filter.extend(list(doc.values())[1])
                    if any(x.lower() in Subject.lower() for x in email_filter):
                        relevant = False
                    print("-----------------------------------------------------------")
                    print("            ")
                    print("Subject:", Subject)
                    print("Is mail relevant:", relevant)
                    print("Received at:", received_at_timestamp)

                    if not any("pdf" in attachment["filename"].lower() or "docx" in attachment["filename"].lower() for attachment in attachments):
                        attachments=None


     

                    if attachments:
                        if relevant:
                            attachments = [attachment for attachment in attachments if any(ext in attachment["filename"].lower() for ext in ["pdf", "docx"])]
                            ai_relevance = False
                            files_data = []
                            print("🟢 The Email has files as attachment.")
                            for attach in attachments:
                                if attach["filename"] is not None:
                                    print("Processing:",attach["filename"])
                                    attachment_filename = os.path.join(self.dir, attach["filename"])
                                    
                                    self.save_attachment(attachment_filename, attach["content"])
                                    isJDValid = is_jd(attachment_filename)
                                    print("❓ Is the document a valid JD:", isJDValid)
                                    if isJDValid == "no":
                                        ai_relevance_new = False
                                    else:
                                        ai_relevance_new = True

                                    ai_relevance = ai_relevance or ai_relevance_new

                                    if ai_relevance_new:
                                        filename = max([str(pathlib.Path(__file__).parent.resolve()) + "/" + f for f in
                                                        os.listdir(pathlib.Path(__file__).parent.resolve())],
                                                       key=os.path.getctime)
                                        newfilename = f"{int(time.time())}_{filename.split('/')[-1]}"
                                        os.rename(filename.split('/')[-1], newfilename)
                                        files.append(newfilename)
                                        file_data = {"s3_key": "JD/" + newfilename, "is_jd": True}
                                        files_data.append(file_data)

                            relevant = ai_relevance
                            if relevant:
                                fwdSubject = Subject + " - Working on it"
                                self.forwardMail(fwdSubject, Content, charset, ContentType, True, files)
                                organization, organization_id = self.get_organization(attachment=files[0], body=Content)
                                job_worker = Job_Scraper()
                                job_worker.run(message_id=msg_id, message_type="jd_as_attachment", jds=files,
                                               data={"message_id": msg_id, "message_type": "jd_as_attachment",
                                                     "job_status": "new",
                                                     "JDs": files_data, "organization":organization, "client_id":int(organization_id)})
                            else:
                                # Location 1: forward email after appending " - Not a JD" to the subject line
                                self.forwardMail(Subject, Content, charset, ContentType, False, files)


                        else:
                            # Location 2: forward email after appending " - Not a JD" to the subject line
                            self.forwardMail(Subject, Content, charset, ContentType, False, files)

                        data = {
                            "message_id": msg_id,
                            "from": Sender,
                            "received_at_timestamp": received_at_timestamp,
                            "subject": Subject,
                            "type": "jd_as_attachment" if relevant else "non_jd",
                            "is_mail_relevant": relevant

                        }

                        self.dump_into_mongodb(data)



                    elif any(x in Subject for x in ["ariba","lotus", "fieldglass", "oracle"]) or any( #Add "ariba"
                            x in Content for x in ["ariba","lotus", "fieldglass", "oracle"]):

                        value = ""

                        data = {
                            "message_id": msg_id,
                            "from": Sender,
                            "received_at_timestamp": received_at_timestamp,
                            "subject": Subject,
                            "type": "jd_as_link" if relevant else "non_jd",
                            "is_mail_relevant": relevant,
                        }

                        self.dump_into_mongodb(data)
                        if relevant:
                            print("🟢 The Email may have JD as Link.")
                            
                            for x in ["ariba", "lotus", "fieldglass", "oracle"]:
                                if x in Content:
                                    value = x
                            if ContentType == "text/html":
                                lnk = self.get_content_from_a_tag(Content)
                                print("1:",lnk)
                            else:
                                lnk = self.extract_url(Content)
                                print("2:",lnk)

                            if lnk==None:
                                self.forwardMail(Subject, Content, charset, ContentType, False)
                                continue

                            fwdSubject = Subject + " - Working on it"
                            self.forwardMail(fwdSubject, Content, charset, ContentType, True)

                            cursor = self.db_admin.find()
                            cred = ()
                            client_system = ''
                            for doc in cursor:
                                if value == 'fieldglass':
                                    if 'NEE' in lnk:
                                        if value in doc.get('email_domain'):
                                            cred = (doc.get('system_username'), doc.get('system_password'))
                                            client_system = doc.get('email_domain')
                                    else:
                                        if value in doc.get('email_domain'):
                                            cred = (doc.get('system_username'), doc.get('system_password'))
                                            client_system = doc.get('email_domain')
                                            break

                                else:
                                    if value in doc.get('email_domain'):
                                        cred = (doc.get('system_username'), doc.get('system_password'))
                                        client_system = doc.get('email_domain')

                            job_worker = Job_Scraper()
                            job_worker.setup_browser()
                            try:
                                job_worker.run(message_id=msg_id, message_type="jd_as_link", lnk=str(lnk), cred=cred,
                                           site=value, client_system=client_system, body=Content)
                            except:
                                print("Some issue with Job scraping. Continuing...")

                        else:  # Location 3: forward email after appending " - Not a JD" to the subject line
                            self.forwardMail(Subject, Content, charset, ContentType, False)

                    else:

                        print("🟢 The Email may have JD in the body.")
                        if relevant:
                            files = []
                            file = f"{int(time.time())}_{Subject}.pdf"
                            files.append(file)
                            self.html_to_pdf(Content, file)

                            isJDValid = is_jd(file)
                            # isJDValid = "yes" #Only for Demo
                            print("❓ Is the body a valid JD:", isJDValid)
                            if isJDValid == "no":
                                relevant = False
                                message_type = "non_jd"
                            else:
                                message_type = "jd_in_body"

                            if relevant:
                                organization, organization_id = self.get_organization(attachment=files[0], body=Content)
                                fwdSubject = Subject + " - Working on it"
                                self.forwardMail(fwdSubject, Content, charset, ContentType)
                                job_worker = Job_Scraper()
                                job_worker.run(message_id=msg_id, message_type="jd_as_body", jds=files,
                                               data={"message_id": msg_id, "message_type": message_type,
                                                     "job_status": "new",
                                                     "JDs": [{"s3_key": "JD/" + files[0], "is_jd": relevant}], "organization":organization, "client_id":int(organization_id)})
                            else:
                                self.forwardMail(Subject, Content, charset, ContentType, False)
                                # Location 4: forward email after appending " - Not a JD" to the subject line
                        else:
                            self.forwardMail(Subject, Content, charset, ContentType, jd=False)
                            # Location 5: forward email after appending " - Not a JD" to the subject line

                        data = {
                            "message_id": msg_id,
                            "from": Sender,
                            "received_at_timestamp": received_at_timestamp,
                            "subject": Subject,
                            "type": "jd_in_body" if relevant else "non_jd",
                            "is_mail_relevant": relevant,

                        }
                        self.dump_into_mongodb(data)
                else:
                    continue
            print('🟢🟢🟢 DONE. Now waiting for 1 minute for new mails.')
            time.sleep(10)

    def run_once(self):
        self.setup()
        self.run_loop()

    def simpelDetetction(self, Content):
        match_ttps = re.search(r'https://\S*/\S*', Content)
        match_ttp = re.search(r'http://\S*/\S*', Content)
        
        if match_ttps and "fieldglass.net/job_posting_detail" in match_ttps.group(0):
            # print(match_ttps.group(0))
            return match_ttps.group(0)
        elif match_ttp and "ariba.com/Supplier.aw/ad/collabReqDetail" in match_ttp.group(0):
            # print(match_ttps.group(0))
            return match_ttp.group(0)
        else:
            return None

    def extract_url(self,Content):
        try:
            # Use regular expressions to find URLs in the content
            urls = re.findall(r'https?://\S*', Content)

            # Filter URLs based on specified conditions and return the first match
            for url in urls:
                if "fieldglass.net/job_posting_detail" in url or "ariba.com/Supplier.aw/ad/collabReqDetail" in url:
                    return url

            # Return None if no matching URL is found
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None


if __name__ == "__main__":
    worker = EmailWorker()
    # worker.cleanDB()
    worker.run_once()
