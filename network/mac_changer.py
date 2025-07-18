#!/usr/bin/env python

import subprocess
import optparse
import re
from util.randomize_mac import get_mac_address

def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option('-i', '--interface', dest="interface",
                      help=' Interface to change its MAC address ')
    parser.add_option('-m', '--mac', dest="mac_address",
                      help=' New MAC address to use')
    (options, arguments) = parser.parse_args()
    if not options.interface:
        parser.error("[-] Please Specify an interface, use --help")
        print("MAC Address is auto Generated, just add -m if you want to specify")
    if not options.mac_address:
        #parser.error("[-] Please Specify an new MAC address, use --help")
        options.mac_address = get_mac_address()

    # For improvement add auto mac address 00:11:22:33:44:55
    print(options)
    return options
    
def change_mac(interface, mac_address):
    print
    print("-"*60)
    print("[+] Changing MAC address for {} to {}".format(interface, mac_address))

    subprocess.call([ "ifconfig", interface, "down" ])
    subprocess.call([ "ifconfig", interface, "hw", "ether", mac_address ])
    subprocess.call([ "ifconfig", interface, "up" ])
    print("-"*60)

def get_current_mac(interface):
    print
    ifconfig_result=subprocess.check_output(["ifconfig", interface])

    mac_adddress_search_result = re.search(r"\w\w:\w\w:\w\w:\w\w:\w\w:\w\w", ifconfig_result)
    if mac_adddress_search_result:
        return mac_adddress_search_result.group(0)
    else:
        print("[-] No MAC address")

options = get_arguments()
current_mac = get_current_mac(options.interface)
print("Current MAC Adress: {} in {}".format(str(current_mac), options.interface))

change_mac(options.interface, options.mac_address)

new_mac = get_current_mac(options.interface)
if new_mac == options.mac_address:
    print("[+] Interface: {}".format(options.interface))
    print("[+] MAC address Successfully changed to {}".format(new_mac))
else:
    print("[-] MAC address did not get changed.")
