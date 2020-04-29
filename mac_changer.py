#!/usr/bin/env python

import optparse
import subprocess


def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-i", "--interface", dest="interface", help="Interface to change its MAC address")
    parser.add_option("-m", "--mac", dest="new_mac", help="New MAC address")
    (options, arguments) = parser.parse_args()
    if not options.interface:
        parser.error("[- Please specify an interface, use --help for more info]")
    elif not options.new_mac:
        parser.error("[- Please specify a new mac, use --help for more info]")
    return options


def change_mac(interface, new_mac):
    print(f'[+] Changing MAC address for {interface} to {new_mac}')
    subprocess.call(["ifconfig", interface, "down"])
    subprocess.call(["ifconfig", interface, "hw", "ether", new_mac])
    subprocess.call(["ifconfig", interface, "up"])


options = get_arguments()
change_mac(options.interface, options.new_mac)

# Second less secure option ()
# subprocess.call(f'ifconfig {interface} down', shell=True)
# subprocess.call(f'ifconfig {interface} hw ether {new_mac}', shell=True)
# subprocess.call(f'ifconfig {interface} up', shell=True)
