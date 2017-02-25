from glob import glob
import pyshark
import datetime
import socket


for file_name in glob("*.pcap"):
    with open(file_name, "rb") as pcap_data:      #Opens .pcap files in working directory
        pdata = pyshark.FileCapture(pcap_data)#Loads .pcap data into variable "pdata" 
        uniqueEth = []                       #Empty list of Unique MAC addresses
        nOU= 0                               #Number of Users
        cBits = 0                            #Cumulitive Bits
        ipA = []                             #Array for ip addresses
        ethDict = {}                         #Dictionary that holds Source MAC 
                                             # address, destination MAC addresses
                                             # and bits from source to destination
        k = 0
        for z in pdata:
            k+=1
        for n in range(0, k):
            pkt = pdata[n]
            #Timestamp in UTC
            t_stamp = str(datetime.datetime.utcfromtimestamp(float(pkt.sniff_timestamp)))
            print "Packet: " + str(n)
            print t_stamp          
            #Source MAC address
            eth_src = pkt.wlan.sa
            #Destination MAC address
            eth_dst = pkt.wlan.da
            #Amount of bits from the nth packet
            dBits = int(pkt.length) * 8
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
             
        
            print("\nDNS information:")
            name_ip = pkt.ip.src
            try:
                host = socket.getfqdn(name_ip)
                print ("IP src: " + host)
            except socket.gaierror, err:
                print "cannot resolve hostname: ", name_ip, err
    
            name_ip = pkt.ip.dst
            try:
                host = socket.getfqdn(name_ip)
                print ("IP dst: " + host + "\n")
            except socket.gaierror, err:
                print "cannot resolve hostname: ", name_ip, err
            
        print "Number of Users: "+str(nOU)
        for z in uniqueEth:
            print z
        print "\nBandwidth is "+str(cBits)+" bits/s \n"
        for k in ethDict: 
            for n in ethDict[k]:
                print "From " + str(k) + " to " + str(n)+" is " +\
                str(ethDict[k][n]) + " bits \n"