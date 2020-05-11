#!/usr/bin/env python
import requests
import argparse


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", dest="url", help="URL of downloading file")

    options = parser.parse_args()
    if not options.url:
        parser.error("[-] Please specify the URL of downloading file, use --help for more info")
    return options


def download(url):
    response = requests.get(url)
    file_name = url.split("/")[-1]
    with open(file_name, "wb") as out_file:
        out_file.write(response.content)


options = get_arguments()

download(options.url)
