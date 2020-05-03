#!/usr/bin/env python

# Python 3.8
# https://github.com/kti/python-netfilterqueue
# apt install python3-pip git libnfnetlink-dev libnetfilter-queue-dev
# pip install -U git+https://github.com/kti/python-netfilterqueue
import subprocess

import netfilterqueue


def process_packet(packet):
    print(packet)
    # packet.accept()
    packet.drop()  # stop connection


try:
    # traps all packets from FORWARD chain to NFQUEUE
    subprocess.call("iptables -I FORWARD -j NFQUEUE --queue-num 0", shell=True)
    queue = netfilterqueue.NetfilterQueue()
    queue.bind(0, process_packet)
    queue.run()
except KeyboardInterrupt:
    print("Exiting...")
finally:
    print("Flushing iptables...")
    subprocess.call("iptables --flush", shell=True)
