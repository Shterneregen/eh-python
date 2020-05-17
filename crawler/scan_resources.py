#!/usr/bin/env python
import argparse

import requests

# python scan_resources.py -t site.com -rf file.txt

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", dest="target", help="Target domain")
    parser.add_argument("-rf", "--resources-file", dest="resources_file", help="File with list of resources")
    options = parser.parse_args()
    if not options.target:
        parser.error("[-] Please specify a target, use --help for more info")
    elif not options.resources_file:
        parser.error("[-] Please specify a file with list of resources, use --help for more info")
    return options


def request(url):
    try:
        return requests.get("http://" + url)
    except Exception:
        pass


def scan_resources(target, subdomains_file):
    with open(subdomains_file, "r") as word_list_file:
        for line in word_list_file:
            word = line.strip()
            test_url = target + "/" + word
            response = request(test_url)
            if response:
                print("[+] Discovered URL --> " + test_url)


options = get_arguments()
scan_resources(options.target, options.resources_file)
