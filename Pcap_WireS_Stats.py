from glob import glob
from pcapfile import savefile
from pcapfile.protocols.linklayer import ethernet
from pcapfile.protocols.network import ip
import datetime
import binascii
import socket

#Hello World!


for file_name in glob("*.pcap"):
    with open(file_name, "rb") as pcap_data:      #Opens .pcap files in working directory
        pdata = savefile.load_savefile(pcap_data, verbose=True)#Loads .pcap data into variable "pdata" 
        uniqueEth = []                       #Empty list of Unique MAC addresses
        nOU= 0                               #Number of Users
        cBits = 0                            #Cumulitive Bits
        ethDict = {}                         #Dictionary that holds Source MAC 
                                             # address, destination MAC addresses
                                             # and bits from source to destination
        
        for n in range(0, len(pdata.packets)):
            pkt = pdata.packets[n]
            #Timestamp in UTC
            t_stamp = str(datetime.datetime.utcfromtimestamp(pkt.timestamp))
            print t_stamp
            eth_frame = ethernet.Ethernet(pdata.packets[n].raw())            
            #Source MAC address
            eth_src = eth_frame.src
            #Destination MAC address
            eth_dst = eth_frame.dst
            #Amount of bits from the nth packet
            dBits = pkt.packet_len * 8
            #Simple calculation of cumulitive bits
            cBits += dBits

            #Adds source and destination MAC address and the number of bits
            # from source to destination into a dictionary, modeled like this:
            # {src1 :{dst1 : bits from src1 to dst1}, {dst2 : bits from src1 to dst2}}   
            if eth_src not in ethDict:             #Adds to dictionary with initial bits
                ethDict[eth_src] = {eth_dst : dBits}
            elif eth_dst not in ethDict[eth_src]: #Adds additional destinations
                ethDict[eth_src].update({eth_dst : dBits})
            else:                                   #Updates bits in dictionary
                ethDict[eth_src][eth_dst] += dBits
        
            #This adds all unique MAC addresses to a list
            if eth_src not in uniqueEth:
                uniqueEth.append(eth_src)
                nOU += 1
            if eth_dst not in uniqueEth:
                uniqueEth.append(eth_dst)
                nOU += 1
                
        
            ip_frame = ip.IP(binascii.unhexlify(eth_frame.payload))
            ip_src = ip_frame.src
            ip_dst = ip_frame.dst
            host = socket.getfqdn(ip_src)
            print host
            host = socket.getfqdn(ip_dst)
            print host
            
        print "Number of Users: "+str(nOU)
        for z in uniqueEth:
            print z
        print "\nBandwidth is "+str(cBits)+" bits/s \n"
        for k in ethDict: 
            for n in ethDict[k]:
                print "From " + str(k) + " to " + str(n)+" is " +\
                str(ethDict[k][n]) + " bits"