#!/usr/bin/env python

import scapy.all as scapy
import optparse

def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option('-t', '--target', dest="target",
                      help=' Target Range of IP address ex: 10.0.2.1/24 ')
    (options, arguments) = parser.parse_args()
    if not options.target:
        parser.error("[-] Please Specify an IP range, use --help")
    # For improvement add auto input of IP address range
    return options


def scapy_scan(ip):
    scapy.arping(ip)

def scan(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff") # 34. Combining Frames Review
    arp_request_broadcast = broadcast/arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0] # this returns two list; answered and unanswered

    client_list = []
    for e in answered_list:
        client_dict = {
            "ip" : e[1].psrc,
            'mac' : e[1].hwsrc
        }
        client_list.append(client_dict)
    return client_list

def print_result(result_list):
    print("IP\t\t\tMAC Address")
    print("-"*50)
    for client in result_list:
        print(client["ip"] + "\t\t" + client["mac"])

options = get_arguments()
scan_result = scan(options.target)
print_result(scan_result)
