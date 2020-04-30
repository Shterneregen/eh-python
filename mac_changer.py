#!/usr/bin/env python

import optparse
import subprocess
import re


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


def get_current_mac(interface):
    ifconfig_result = subprocess.check_output(["ifconfig", interface])
    mac_address_search_result = re.search(r"\w\w:\w\w:\w\w:\w\w:\w\w:\w\w", str(ifconfig_result))
    if mac_address_search_result:
        return str(mac_address_search_result.group(0))
    else:
        print("[-] Could not read MAC address")


options = get_arguments()

print(f'Current MAC = {str(get_current_mac(options.interface))}')

change_mac(options.interface, options.new_mac)

current_mac = get_current_mac(options.interface)
if current_mac == options.new_mac:
    print(f'[+] MAC address was successfully changed to {str(current_mac)}')
else:
    print(f'[-] MAC address did not get changed')

# Second less secure option ()
# subprocess.call(f'ifconfig {interface} down', shell=True)
# subprocess.call(f'ifconfig {interface} hw ether {new_mac}', shell=True)
# subprocess.call(f'ifconfig {interface} up', shell=True)
