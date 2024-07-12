# Import necessary modules
from scapy.all import *

# Define source and destination ports
src_port = 12345
dst_port = 80

# Create a TCP packet with specific source and destination ports
tcp_packet = IP(dst="8.8.8.8")/UDP(dport=53)/DNS(rd=1,qd=DNSQR(qname="www.google.com"))

# Display the packet summary
print("TCP Packet Summary:")
print(tcp_packet.summary())

# Send the packet
r=sr1(tcp_packet)
r.show() 