#!/usr/bin/env python
import argparse
import re
import urllib.parse

import requests


# python link_scanner.py -t https://some-site.com/

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", dest="target", help="Target url")
    options = parser.parse_args()
    if not options.target:
        parser.error("[-] Please specify a target, use --help for more info")
    return options


def extract_links_from(url):
    try:
        response = requests.get(url)
        if response and response.content:
            return re.findall('(?:href=")(.*?)"', response.content.decode())
    except Exception:
        pass


def craw(url):
    href_links = extract_links_from(url)
    if href_links:
        for link in href_links:
            link = urllib.parse.urljoin(url, link)
            if "#" in link:
                link = link.split("#")[0]
            if target_url in link and link not in target_links:
                target_links.append(link)
                print(link)
                craw(link)


target_links = []
options = get_arguments()
target_url = options.target
craw(target_url)
