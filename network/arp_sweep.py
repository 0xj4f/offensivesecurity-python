import scapy.all as scapy


class ArpScanner:
    def __init__(self, target_ip_range):
        self.target_ip_range = target_ip_range

    def scan(self):
        arp_request = scapy.ARP(pdst=self.target_ip_range)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast / arp_request
        answered_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]
        devices = []
        for element in answered_list:
            devices.append({"ip": element[1].psrc, "mac": element[1].hwsrc})
        return devices


if __name__ == "__main__":
    target_range = "192.168.0.1/24"  # change this to your subnet
    scanner = ArpScanner(target_range)
    result = scanner.scan()
    for device in result:
        print(f"{device['ip']}\t{device['mac']}")


"""
╰─$ ifconfig | grep "inet "
        inet 127.0.0.1 netmask 0xff000000
        inet 192.168.254.144 netmask 0xffffff00 broadcast 192.168.254.255
        
╰─$ python3 arp_sweep.py
192.168.254.103 18:ef:3a:85:d1:a5
192.168.254.136 b8:27:eb:74:f2:6c
192.168.254.254 58:56:c2:2d:cc:0a
192.168.254.109 88:e9:fe:76:6d:0a
192.168.254.169 e8:fb:1c:7d:0a:ef
192.168.254.144 80:a9:97:27:41:b7
"""