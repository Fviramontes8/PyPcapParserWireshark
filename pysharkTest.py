import pyshark
 
# Open saved trace file
cap = pyshark.FileCapture('partIV.pcap')

#print(cap[0])
print(cap[0].length)
print(cap[0].ip)
print(cap[0].layers)
print(cap[0].ip.dst)
print(cap[0].ip.src)
print(cap[0].eth.src)
print(cap[0].eth.dst)
print(cap[0].sniff_time)
#source destination, mac, size/length, ip, dns lookup, time stamp


print("\nDNS information\n")
import socket
for pkt in cap:
    name_ip = pkt.ip.src
    try:
        host = socket.getfqdn(name_ip)
        print ("src: " + host)
    except socket.gaierror, err:
        print "cannot resolve hostname: ", name_ip, err
    
    name_ip = pkt.ip.dst
    try:
        host = socket.getfqdn(name_ip)
        print ("dst: " + host + "\n")
    except socket.gaierror, err:
        print "cannot resolve hostname: ", name_ip, err
        
cap.close()