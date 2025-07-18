#!/usr/bin/env python

import scapy.all as scapy
import optparse

def scapy_scan(ip):
    scapy.arping(ip)

scapy_scan("192.168.100.1/24")
