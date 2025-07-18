#!/usr/bin/env python
import netfilterqueue
import subprocess

def proccess_packet(packet):
    print(packet)
    packet.accept()

subprocess.call("iptables -I FORWARD -j NFQUEUE --queue-num 0", shell=True)

try:
    while True:
        queue = netfilterqueue.NetfilterQueue()
        queue.bind(0, proccess_packet)
        queue.run()
except KeyboardInterrupt:
    subprocess.call("iptables --flush", shell=True)
    print("\nStopped.. IP Tables Flushed")