from scapy.all import *

a = rdpcap('partIV.pcap')
print(a)
print(a[0][IP].src)
print(a[0][IP].dst)

print(a[0][Ether].src)
print(a[0][Ether].dst)

print(a[0].time)
