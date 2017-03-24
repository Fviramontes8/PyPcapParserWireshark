from glob import glob
import pyshark
import socket

#This function checks specific channel flags of a packet
# also updates a dictionary counting channel flags
def check_flags(pkt, cflags):
    try:
        #Complementary Code Keying
        if pkt.channel_flags_cck != "0":
            cflags["cck"] += 1  
        #Orthogonal Frequency Division Multiplexing
        if pkt.channel_flags_ofdm != "0":
            cflags["ofdm"] += 1
        #Uses 2 GHz spectrum
        if pkt.channel_flags_2ghz != "0":
            cflags["twoghz"] += 1 
        #Uses 5 GHz spectrum
        if pkt.channel_flags_5ghz != "0":
            cflags["fiveghz"] += 1 
        #Passive mode is on
        if pkt.channel_flags_passive != "0":
            cflags["passive"] += 1 
        #Dynamic CCK-OFDM
        if pkt.channel_flags_dynamic != "0":
            cflags["cck_ofdm"] += 1 
        #Gaussian frequency shift keying
        if pkt.channel_flags_gfsk != "0":
            cflags["gfsk"] += 1 
        #GSM at 900 MHz
        if pkt.channel_flags_gsm != "0":
            cflags["gsm"] += 1 
        #Uses a half rate channel (10 MHz channel width)
        if pkt.channel_flags_half != "0":
            cflags["half"] += 1
        #Uses a quarter rate channel (5MHz channel width)
        if pkt.channel_flags_quarter != "0":
            cflags["quarter"] += 1
        #Returns the updated dictionary
        return cflags
    except:
        print "Cannot determine channel flags"

for file_name in glob("*.pcap"):
    #Opens .pcap files in working directory
    with open(file_name, "rb") as pcap_data:
        #Loads .pcap data into variable "pdata"
        pktdata = pyshark.FileCapture(pcap_data) 
        #Empty list of Unique MAC addresses
        uniqueEth = []                            
        #Interger counter for number of users
        numOfUsers= 0                               
        #Cumulitive Bits
        cumulBits = 0                            
        #List for IPv4 addresses
        ipv4 = []                            
        #Dictionary that holds Source MAC address, destination MAC addresses
        # and bits from source to destination
        ethDict = {}  
        #Cumulitive channel Flag counter
        cflags = {"cck": 0,"ofdm": 0,"twoghz": 0,"fiveghz": 0,\
        "passive": 0,"cck_ofdm": 0,"gfsk": 0,"gsm": 0,"half": 0,\
        "quarter": 0}
        #This dictionary gets everything ready to upload to a database
        ethFinal = {}
                
        n = 0
        for z in pktdata:
            pkt = pktdata[n]
            #Packet number
            print "Packet: " + str(n+1)
            #Timestamp in UTC/Epoch time
            print pkt.sniff_timestamp
            
            #Channel Flag counter between two users
            cflags_c = {"cck": 0,"ofdm": 0,"twoghz": 0,"fiveghz": 0,\
            "passive": 0,"cck_ofdm": 0,"gfsk": 0,"gsm": 0,"half": 0,\
            "quarter": 0}
            
            #Computing bits in packet n and adding to cumulitive bits
            try:
                #Amount of bits from the nth packet
                pktBits = int(pkt.length) * 8
                #Simple calculation of cumulitive bits
                cumulBits += pktBits
            except:
                pass
                
            #Computing statistics from user A to user B
            try:         
                #Source MAC address
                eth_src = pkt.wlan.sa
                #Destination MAC address
                eth_dst = pkt.wlan.da
                
                #Dictionary that takes and updates data sent between two users
                # the zeros count how many times the channel flags occur.
                # For example, if 3 2GHz cck signals were are between users 
                # the output of the flag counter would look like this:'
                # [..., ..., ..., ..., 0, 3, 0, 0, 3, 0, 0, 0, 0, 0]
                #Format: {key : [timestamp, src, dst, 
                # bits from src to dst, passive, 2GHz, quarter, ofdm, cck, 
                # gfsk, 5GHz, half, gsm, cck_ofdm]}
                if eth_src not in ethDict:
                    ethDict[eth_src] = {eth_dst : \
                    [int(float(pktdata[0].sniff_timestamp)), eth_src, eth_dst, pktBits,\
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0]} 
                #For multiple sources that have different destinations
                elif eth_dst not in ethDict[eth_src]: 
                    ethDict[eth_src].update({eth_dst :\
                    [int(float(pktdata[0].sniff_timestamp)), eth_src, eth_dst, pktBits,\
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0]})
                #Updates bits in dictionary
                else:
                    ethDict[eth_src][eth_dst][3] += pktBits
                    
                #Function calls for checking/updating channel flags   
                check_flags(pkt.radiotap,cflags)
                check_flags(pkt.radiotap,cflags_c)
                
                #This little block updates channel flags betweens users
                iterator = 4
                for f in cflags:
                    ethDict[eth_src][eth_dst][iterator] += cflags_c[f]
                    iterator += 1
                
                #This adds all unique MAC addresses to a list and counts number 
                # of users based on number of unique MAC addresses
                if eth_src not in uniqueEth:
                    uniqueEth.append(eth_src)
                    numOfUsers += 1
                if eth_dst not in uniqueEth:
                    uniqueEth.append(eth_dst)
                    numOfUsers += 1 
            except:
                pass
                
            #Taking a look at IPv4 information
            try:
                #Takes a 'bare' ip address (129.168.24.131) and tries to find
                # the fully qualified domain name, but if it was already encountered
                # in a previous packet, we do not want to do a lookup again and will
                # move on.
                name_ip = pkt.ip.src
                if name_ip not in ipv4:
                    try:
                        fqdn_srcv4 = socket.getfqdn(name_ip)
                        print ("IPv4 src: " + fqdn_srcv4)
                    except:
                        pass
                else:
                    print "IPv4 src: " + name_ip
                
                #This adds either a 'bare' ip address (129.168.24.131) or 
                # a domain name (video.google.com) so if the parser comes across
                # another packet with the same IP address it does not waste time
                # doing a fully qualified domain name lookup    
                if fqdn_srcv4 not in ipv4:
                    ipv4.append(fqdn_srcv4)
                
                #This does the exact thing as above, but with the destination 
                # IP address rather than the source IP address
                name_ip = pkt.ip.dst
                if name_ip not in ipv4:
                    try:
                        fqdn_dstv4 = socket.getfqdn(name_ip)
                        print ("IPv4 dst: " + fqdn_dstv4 + "\n")
                    except:
                        pass
                else:
                    print "IPv4 dst: " + name_ip + "\n"
                    
                if fqdn_dstv4 not in ipv4:
                    ipv4.append(fqdn_dstv4)
                
                #Checks protocol version of an IPv4 packet and prints socket info  
                if pkt.ip.proto == "6":
                    proto = "TCP"
                    print "Source port: " + pkt.tcp.srcport
                    print "Destination port: " + pkt.tcp.dstport
                if pkt.ip.proto == "17":
                    proto = "UDP" 
                    print "Source port: " + pkt.udp.srcport
                    print "Destination port: " + pkt.udp.dstport 
                print "\n" 
            except:
                pass
                
            #Looking at signal properties of the packet
            try:
                #Determines the physical type, 802.11b/g/n
                if pkt.wlan_radio.phy == "4":
                    phy = "b"
                if pkt.wlan_radio.phy == "6":
                    phy = "g"
                if pkt.wlan_radio.phy == "7":
                    phy = "n"
                    #802.11n can give us the bandwidth used
                    try:
                        pkt.wlan_radio.get_field("11n_bandwidth")
                        band = pkt.wlan_radio.get_field("11n_bandwidth")
                        if band is not None and band == "0":
                            band = "20 Mhz"
                            print "802.11n bandwidth is: " + band
                    except:
                        pass
                #Gives what channel is being used
                channel = pkt.wlan_radio.channel
                #Channel frequency of the packet in MHz
                freq = pkt.wlan_radio.frequency
                #Data rate from source to destination in Mb/s
                d_rate = pkt.wlan_radio.data_rate
                #Signal strength in decibels
                signal_strength = pkt.wlan_radio.signal_dbm
                #Duration and preamble duration in mircoseconds
                dur = pkt.wlan_radio.duration
                preamble = pkt.wlan_radio.preamble
                print "Physical type: " + phy
                print "Channel: " + channel
                print "Frequency: " + freq + " Mhz"
                print "Data rate is: " + d_rate + " Mb/s"
                print "Signal strength: " + signal_strength + " dBm"
                print "Duration: " + dur + " us"
                print "Preamble duration: " + preamble + " us\n"
            except:
                pass
            n += 1  
        
        #Gets time between final and first packet, this is computed to find bandwidth      
        total_duration = float(pktdata[n-1].sniff_timestamp) - float(pktdata[0].sniff_timestamp)
        #In the case that there is only one packet in the pcap file
        if total_duration <= 0:
            total_duration = 1
        
        #Puts ethDict into a more readable dictionary, ready to give to a database 
        #Format:
        # {key:[key, timestamp, src, dst, bits from src to dst, passive,
        # 2GHz, quarter, ofdm, cck, gfsk, 5GHz, half, gsm, cck_ofdm]}
        for k in ethDict: 
                for j in ethDict[k]:
                    l = str(int(float(pktdata[0].sniff_timestamp))) + str(k) + str(j)
                    if l not in ethFinal:
                        ethFinal[l] = [l] + ethDict[k][j]
        
        #Finally, we print everything
        if numOfUsers > 0: 
            print "Number of Users: "+str(numOfUsers)
            for z in uniqueEth:
                print z
            print"\n"
            print "Bandwidth is "+str(int(cumulBits/total_duration))+" bits/s \n"
            for k in cflags:
                if cflags[k] > 0:
                    print k + ": " + str(cflags[k])
            print ethFinal
            print"\n"
        else:
            print "There are no users/data for this pcap file: " + str(file_name)