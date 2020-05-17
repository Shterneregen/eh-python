#!/usr/bin/env python
import argparse

import requests


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", dest="target", help="Target domain")
    parser.add_argument("-sf", "--subdomains-file", dest="subdomains_file", help="File with list of subdomains")
    options = parser.parse_args()
    if not options.target:
        parser.error("[-] Please specify a target, use --help for more info")
    elif not options.subdomains_file:
        parser.error("[-] Please specify a subdomains file, use --help for more info")
    return options


def request(url):
    try:
        return requests.get("http://" + url)
    except Exception:
        pass


def scan_subdomains(target, subdomains_file):
    with open(subdomains_file, "r") as word_list_file:
        for line in word_list_file:
            word = line.strip()
            test_url = word + "." + target
            response = request(test_url)
            if response:
                print("[+] Discovered subdomain --> " + test_url)


options = get_arguments()
scan_subdomains(options.target, options.subdomains_file)
