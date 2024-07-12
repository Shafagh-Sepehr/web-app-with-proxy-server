# Import necessary modules from Scapy
from scapy.all import *
from scapy.layers.http import HTTP, HTTPRequest

def http_packet_callback(packet):
    # Check if the packet has an HTTP layer
    if packet.haslayer(HTTPRequest):
        # Extract HTTP request details
        http_layer = packet[HTTPRequest]
        print(f"HTTP Method: {http_layer.Method.decode('utf-8')}")
        print(f"Host: {http_layer.Host.decode('utf-8')}")
        print(f"Path: {http_layer.Path.decode('utf-8')}")
        print(f"User-Agent: {http_layer.User_Agent.decode('utf-8')}")

# Start sniffing packets with a filter for HTTP requests
print("Starting packet sniffing...")
sniff(filter="tcp port 80", prn=http_packet_callback, store=False)
