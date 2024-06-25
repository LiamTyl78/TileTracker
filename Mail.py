from email.message import EmailMessage
from app2 import EMAIL_PASSWORD,EMAIL_SENDER
import ssl, smtplib, os

emailSender = EMAIL_SENDER
EMAIL_PASSWORD = EMAIL_PASSWORD
emailReciver = ''
emailSubject = ''
emailBody = ''
context = ssl.create_default_context()
    
class email:
    def __init__(self, emailReciver, emailSubject, emailBody):
        self.emailReciver = emailReciver
        self.emailSubject = emailSubject
        self.emailBody = emailBody
    
        self.msg = EmailMessage()
        self.msg['From'] = emailSender
        self.msg['To'] = self.emailReciver
        self.msg['Subject'] = self.emailSubject
        self.msg.set_content(self.emailBody)

        with open('C:/Users/e-tyl/OneDrive - Rowan University/TileTraker/map.png', 'rb') as f:
            image_data = f.read()
            image_type = 'png'

        self.msg.add_attachment(image_data, maintype='image', subtype=image_type, filename='map.png')


    def send(self):
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(emailSender, EMAIL_PASSWORD)
            smtp.sendmail(emailSender, self.emailReciver, self.msg.as_string())
            del self.msg['TO']
            del self.msg['From']
            del self.msg['subject']
            smtp.close()