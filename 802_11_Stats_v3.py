from glob import glob
import pyshark
import socket

#This function checks specific channel flags of a packet and updates a dictionary
def check_flags(pkt, cflags):
    try:
        if pkt.channel_flags_cck != "0":
            cflags["cck"] += 1 #Complementary Code Keying 
        if pkt.channel_flags_ofdm != "0":
            cflags["ofdm"] += 1
        if pkt.channel_flags_2ghz != "0":
            cflags["twoghz"] += 1 #Uses 2 GHz spectrum
        if pkt.channel_flags_5ghz != "0":
            cflags["fiveghz"] += 1 #Uses 5 GHz spectrum
        if pkt.channel_flags_passive != "0":
            cflags["passive"] += 1 #Passive mode is on
        if pkt.channel_flags_dynamic != "0":
            cflags["cck_ofdm"] += 1 #Dynamic CCK-OFDM
        if pkt.channel_flags_gfsk != "0":
            cflags["gfsk"] += 1 #Gaussian frequency shift keying
        if pkt.channel_flags_gsm != "0":
            cflags["gsm"] += 1 #GSM at 900 MHz
        if pkt.channel_flags_half != "0":
            #Uses a half rate channel (10 MHz channel width)
            cflags["half"] += 1
        if pkt.channel_flags_quarter != "0":
            #Uses a quarter rate channel (5MHz channel width)
            cflags["quarter"] += 1
        return cflags
    except:
        print "Cannot determine channel flags"

for file_name in glob("*.pcap"):
    with open(file_name, "rb") as pcap_data:      #Opens .pcap files in working directory
        pdata = pyshark.FileCapture(pcap_data)#Loads .pcap data into variable "pdata" 
        uEth = []                            #Empty list of Unique MAC addresses
        nOU= 0                               #Number of Users
        cBits = 0                            #Cumulitive Bits
        ipv4 = []                            #List for IPv4 addresses
        ethDict = {}                         #Dictionary that holds Source MAC 
                                             # address, destination MAC addresses
                                             # and bits from source to destination
        #Channel Flags
        cflags = {"cck": 0,"ofdm": 0,"twoghz": 0,"fiveghz": 0,\
        "passive": 0,"cck_ofdm": 0,"gfsk": 0,"gsm": 0,"half": 0,\
        "quarter": 0}
        ethFin = {}
                
        n = 0
        for z in pdata:
            pkt = pdata[n]
            #Packet number
            print "Packet: " + str(n+1)
            #Timestamp in UTC/Epoch
            print pkt.sniff_timestamp #float
            
            #Channel Flags counter
            cflags_c = {"cck": 0,"ofdm": 0,"twoghz": 0,"fiveghz": 0,\
            "passive": 0,"cck_ofdm": 0,"gfsk": 0,"gsm": 0,"half": 0,\
            "quarter": 0}
            
            #Computing bits in packet n and adding to cumulitive bits
            try:
                #Amount of bits from the nth packet
                dBits = int(pkt.length) * 8
                #Simple calculation of cumulitive bits
                cBits += dBits
            except:
                pass
                
            #Computing statistics from user A to user B
            try:         
                #Source MAC address
                eth_src = pkt.wlan.sa
                #Destination MAC address
                eth_dst = pkt.wlan.da
                
                #Dictionary structure: {key : [timestamp, src, dst, 
                # bits from src to dst, passive, 2GHz, quarter, ofdm, cck, 
                # gfsk, 5GHz, half, gsm, cck_ofdm]}
                if eth_src not in ethDict:
                    ethDict[eth_src] = {eth_dst : \
                    [int(float(pdata[0].sniff_timestamp)), eth_src, eth_dst, dBits,\
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0]} #The zeros are for channel flags
                #For multiple sources that have different destinations
                elif eth_dst not in ethDict[eth_src]: 
                    ethDict[eth_src].update({eth_dst :\
                    [int(float(pdata[0].sniff_timestamp)), eth_src, eth_dst, dBits,\
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0]})#The zeros are for channel flags
                #Updates bits in dictionary
                else:
                    ethDict[eth_src][eth_dst][3] += dBits
                    
                #Function calls for checking/updating channel flags   
                check_flags(pkt.radiotap,cflags)
                check_flags(pkt.radiotap,cflags_c)
                
                #This little piece right here updates channel flags betweens users
                iterator = 4
                for f in cflags:
                    ethDict[eth_src][eth_dst][iterator] += cflags_c[f]
                    iterator += 1
                
                #This adds all unique MAC addresses to a list
                if eth_src not in uEth:
                    uEth.append(eth_src)
                    nOU += 1
                if eth_dst not in uEth:
                    uEth.append(eth_dst)
                    nOU += 1 
            except:
                pass
                
            #Taking a look at IPv4 information
            try:
                name_ip = pkt.ip.src
            
                if name_ip not in ipv4:
                    try:
                        host_srcv4 = socket.getfqdn(name_ip)
                        print ("IPv4 src: " + host_srcv4)
                    except:
                        pass
                else:
                    print "IPv4 src: " + name_ip
                    
                if host_srcv4 not in ipv4:
                    ipv4.append(host_srcv4)
        
                name_ip = pkt.ip.dst
                if name_ip not in ipv4:
                    try:
                        host_dstv4 = socket.getfqdn(name_ip)
                        print ("IPv4 dst: " + host_dstv4 + "\n")
                    except:
                        pass
                else:
                    print "IPv4 dst: " + name_ip + "\n"
                    
                if host_dstv4 not in ipv4:
                    ipv4.append(host_dstv4)
                    
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
                #Trying to see what is the physical type
                #Consider using a dictionary for this
                if pkt.wlan_radio.phy == "4":
                    phy = "b"
                if pkt.wlan_radio.phy == "6":
                    phy = "g"
                if pkt.wlan_radio.phy == "7":
                    phy = "n"
                    #802.11n can give us bandwidth
                    try:
                        pkt.wlan_radio.get_field("11n_bandwidth")
                        band = pkt.wlan_radio.get_field("11n_bandwidth")
                        if band is not None and band == "0":
                            band = "20 Mhz"
                            print "802.11n bandwidth is: " + band
                    except:
                        pass
                #Finds out what channel is being used
                channel = pkt.wlan_radio.channel #int
                #The frequency is the same as channel frequency
                freq = pkt.wlan_radio.frequency #int
                d_rate = pkt.wlan_radio.data_rate #int
                signal_stren = pkt.wlan_radio.signal_dbm #int
                dur = pkt.wlan_radio.duration #int
                preamble = pkt.wlan_radio.preamble #int
                print "Physical type: " + phy
                print "Channel: " + channel
                print "Frequency: " + freq + " Mhz"
                print "Data rate is: " + d_rate + " Mb/s"
                print "Signal strength: " + signal_stren + " dBm"
                print "Duration: " + dur + " us"
                print "Preamble duration: " + preamble + " us\n"
            except:
                pass
            n += 1    
        total_dur = float(pdata[n-1].sniff_timestamp) - float(pdata[0].sniff_timestamp)
        if total_dur <= 0:
            total_dur = 1
        for k in ethDict: 
                for j in ethDict[k]:
                    l = str(int(float(pdata[0].sniff_timestamp))) + "_" + str(k) + "_" + str(j)
                    if l not in ethFin:
                        ethFin[l] = ethDict[k][j]
        if nOU > 0: 
            print "Number of Users: "+str(nOU)
            for z in uEth:
                print z
            print"\n"
            print "Bandwidth is "+str(int(cBits/total_dur))+" bits/s \n"
            for k in cflags:
                if cflags[k] > 0:
                    print k + ": " + str(cflags[k])
            print ethFin
            print"\n"
        else:
            print "There are no users/data for this pcap file: " + str(file_name)