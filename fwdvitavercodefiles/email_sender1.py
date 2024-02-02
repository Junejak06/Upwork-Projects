import imaplib
import email
import os
import pathlib
import re
import time
from datetime import datetime, timedelta
from email.mime.application import MIMEApplication
import mimetypes


from bs4 import BeautifulSoup
import boto3
from email.header import decode_header

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from xhtml2pdf import pisa
from io import BytesIO
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart



class emailSender:
    def __init__(self):
        self.imap = None
        self.imap_server = 'email9.luxsci.com'
        self.username = 'xyfd321@vitaver.com/ai1'
        self.emailid = 'xyfd321@vitaver.com'
        self.password = 'D2vuFEhBeA5+'

    def setup(self):
        try:
            self.imap = imaplib.IMAP4_SSL(self.imap_server)
            self.imap.login(self.username, self.password)
            print('📧Successfully logged in to email.')
        except Exception as e:
            print("Failed to connect to the IMAP server:", str(e))

    def sendMail(self,receiver,subject, body,attachments=None):
        message = MIMEMultipart()
        message["From"] = self.emailid
        message["To"] = receiver
        message["Subject"] = subject
        message.attach(MIMEText(body))
        if attachments:
            for attach in attachments:

                mime_type, _ = mimetypes.guess_type(attach)

                with open(attach, 'rb') as docx_file:
                    docx_attachment = MIMEApplication(docx_file.read(), _subtype=mime_type.split('/')[1])
                    docx_attachment.add_header('Content-Disposition', f'attachment; filename={attach}')

                # with open(attach, 'rb') as pdf_file:
                #     pdf_attachment = MIMEApplication(pdf_file.read(), _subtype='pdf')
                #     pdf_attachment.add_header('Content-Disposition', f'attachment; filename={attach}')
                message.attach(docx_attachment)

        try:
            smtp_server = smtplib.SMTP(self.imap_server)
            smtp_server.starttls()
            smtp_server.login(self.username, self.password)
            # Send the email
            smtp_server.sendmail(self.emailid, receiver, message.as_string())
            smtp_server.quit()
            print("Email sent successfully.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

# if __name__ == "__main__":
#     sender = emailSender()
#     sender.setup()
#     L1s = ['1696334883_IT Programmer Analyst, Principal.docx']
#     sender.sendMail('aanchal.goel2508@gmail.com','Test','Hello, this is a testmail \n\n Regards Robot',L1s)
