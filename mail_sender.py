#!/usr/bin/env python
import smtplib
from email.header import Header
from email.mime.text import MIMEText


# https://myaccount.google.com/lesssecureapps


class MailSender:
    def __init__(self, smtp_server, smtp_port, sender, password, recipients, subject, message):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender = sender
        self.password = password
        self.recipients = recipients
        self.subject = subject
        self.message = message

    def get_mime_text(self, sender, recipients, subject, message):
        mime_msg = MIMEText(message, 'plain', 'utf-8')
        mime_msg['Subject'] = Header(subject, 'utf-8')
        mime_msg['From'] = sender
        mime_msg['To'] = recipients
        return mime_msg

    def send_mail(self, smtp_server, smtp_port, psw, mime_msg):
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        try:
            server.starttls()
            server.login(mime_msg['From'], psw)
            server.sendmail(mime_msg['From'], mime_msg['To'], mime_msg.as_string())
        finally:
            server.quit()

    def sendmail(self):
        mime_msg = self.get_mime_text(self.sender, self.recipients, self.subject, self.message)
        self.send_mail(self.smtp_server, self.smtp_port, self.password, mime_msg)
