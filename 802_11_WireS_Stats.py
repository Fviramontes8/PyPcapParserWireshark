from glob import glob
import pyshark
import socket


for file_name in glob("*.pcap"):
    with open(file_name, "rb") as pcap_data:      #Opens .pcap files in working directory
        pdata = pyshark.FileCapture(pcap_data)#Loads .pcap data into variable "pdata" 
        uniqueEth = []                       #Empty list of Unique MAC addresses
        nOU= 0                               #Number of Users
        cBits = 0                            #Cumulitive Bits
        ipv4 = []                            #List for IPv4 addresses
        ipv6 = []                            #List for IPv6 addresses
        ethDict = {}                         #Dictionary that holds Source MAC 
                                             # address, destination MAC addresses
                                             # and bits from source to destination
                
        k = 0
        for z in pdata:
            k += 1
        print file_name
        for n in range(0, k):
            pkt = pdata[n]
            #Packet number
            print "Packet: " + str(n+1)
            #Timestamp in UTC/Epoch
            print pkt.sniff_timestamp         
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
            #The packet has IPv4 information
            try:
                pkt.ip
                print("\nDNS information for IPv4:")
                name_ip = pkt.ip.src
            
                if name_ip not in ipv4:
                    try:
                        host_srcv4 = socket.getfqdn(name_ip)
                        print ("IP src: " + host_srcv4)
                    except socket.gaierror, err:
                        print "Timed out, IP src: ", name_ip, err
                else:
                    print "IP src: " + name_ip
                    
                if host_srcv4 not in ipv4:
                    ipv4.append(host_srcv4)
        
                name_ip = pkt.ip.dst
                if name_ip not in ipv4:
                    try:
                        host_dstv4 = socket.getfqdn(name_ip)
                        print ("IP dst: " + host_dstv4 + "\n")
                    except socket.timeout, err:
                        print "Timed out, IP dst: ", name_ip, err
                else:
                    print "IP dst: " + name_ip + "\n"
                if host_dstv4 not in ipv4:
                    ipv4.append(host_dstv4)
                    
            except:
                pass
            #The packet has IPv6 information
            try:
                pkt.ipv6
                print("\nDNS information for IPv6:")
                name_ip = pkt.ipv6.src
            
                if name_ip not in ipv6:
                    try:
                        host_srcv6 = socket.getfqdn(name_ip)
                        print ("IP src: " + str(host_srcv6))
                    except socket.gaierror, err:
                        print "Timed out, IP src: ", name_ip, err
                else:
                    print "IP src: " + name_ip
                    
                if host_srcv6 not in ipv6:
                    ipv6.append(host_srcv6)
        
                name_ip = pkt.ipv6.dst
                if name_ip not in ipv6:
                    try:
                        host_dstv6 = socket.getfqdn(name_ip)
                        print ("IP dst: " + host_dstv6)
                    except socket.timeout, err:
                        print "Timed out, IP dst: ", name_ip, err
                else:
                    print "IP dst: " + name_ip + "\n"
                if host_dstv6 not in ipv6:
                    ipv6.append(host_dstv6)
            except:
                pass
            try:
                if pkt.wlan_radio.phy == "4":
                    phy = "802.11b"
                    print "Physical type: " + phy
                channel = pkt.wlan_radio.channel
                print "Channel: " + channel
                freq = pkt.wlan_radio.frequency
                print "Frequency: " + freq + " Mhz"
                dur = pkt.wlan_radio.duration
                print "Duration: " + dur + " us"
                preamble = pkt.wlan_radio.preamble
                print "Preamble duration: " + preamble + " us"
            except:
                pass
                
            
        if nOU > 0: 
            print "Number of Users: "+str(nOU)
            for z in uniqueEth:
                print z
            print "\nBandwidth is "+str(cBits)+" bits/s \n"
            for k in ethDict: 
                for n in ethDict[k]:
                    print "From " + str(k) + " to " + str(n)+" is " +\
                    str(ethDict[k][n]) + " bits \n"
            if ipv4:
                print "IPv4 addresses: "
                for h in ipv4:
                    print h
                print "\n"
            if ipv6:
                print "IPv6 addresses: "
                for u in ipv6:
                    print u
                print "\n"
        else:
            print "There are no users/data for this pcap file: " + str(file_name)