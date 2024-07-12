# Import necessary modules
from scapy.layers.http import HTTP
from scapy.layers.inet import ICMP, IP, UDP, TCP
from scapy.layers.dns import DNS
from scapy.layers.l2 import Ether
from scapy.sendrecv import sniff, send, sr1


# Define a packet handler function to filter TCP packets based on ports
def packet_handler(packet):
    if packet.haslayer(TCP):
        tcp_layer = packet.getlayer(TCP)
        ip_layer = packet.getlayer(IP)
        print(f"TCP Packet: {ip_layer.src}:{tcp_layer.sport} -> {ip_layer.dst}:{tcp_layer.dport}")

# Start sniffing packets with a filter for TCP packets only
print("Starting to sniff TCP packets...")
sniff(filter="tcp", prn=packet_handler, count=5)
