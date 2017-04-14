from glob import glob
import pyshark

##################################################################

# Take a look at what causes memory leakage, keeping the program running
# (maybe a command prompt script??), and finalize adding to the table.

#########################################################

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
        '''#Uses a half rate channel (10 MHz channel width)
        if pkt.channel_flags_half != "0":
            cflags["half"] += 1
        #Uses a quarter rate channel (5MHz channel width)
        if pkt.channel_flags_quarter != "0":
            cflags["quarter"] += 1'''
        #Returns the updated dictionary
        return cflags
    except:
        pass

dns_addr = {}
for file_name in glob("*.pcap"):
    #Opens .pcap files in working directory
    with open(file_name, "rb") as pcap_data:
        #Loads .pcap data into variable "pktdata"
        pktdata = pyshark.FileCapture(pcap_data) 
        #Empty list of Unique MAC addresses
        uniqueMAC = []                            
        #Interger counter for number of users
        numOfUsers= 0                               
        #Cumulitive Bits
        cumulBits = 0                          
        #List for IPv4 addresses
        ipv4 = []
        #List of dns answers for the pcap file (if there are any)
        dns_list = []                             
        #Dictionary that holds Source MAC address, destination MAC addresses
        # and bits from source to destination
        ethDict = {}  
        #Cumulitive channel Flag counter
        cflags = {"cck": 0,"ofdm": 0,"twoghz": 0,"fiveghz": 0,\
        "passive": 0,"cck_ofdm": 0,"gfsk": 0,"gsm": 0} #,"half": 0,\
        #"quarter": 0}
        #This dictionary gets everything ready to upload to a database
        ethFinal = {}
                
        n = 0
        for z in pktdata:
            pkt = pktdata[n]
            #Packet number
            print "Packet: " + str(n+1)
            #Timestamp in UTC/Epoch time
            #print pkt.sniff_timestamp
            
            #Channel Flag counter between two users
            cflags_c = {"cck": 0,"ofdm": 0,"twoghz": 0,"fiveghz": 0,\
            "passive": 0,"cck_ofdm": 0,"gfsk": 0,"gsm": 0} #,"half": 0,\
            #"quarter": 0}
            
            #Computing bits in packet n and adding to cumulitive bits
            try:
                #Amount of bits from the nth packet
                pktBits = int(pkt.length) * 8
                #Simple calculation of cumulitive bits
                cumulBits += pktBits
            except:
                pass
            #Taking a look at IPv4 information
            try:
                #Source IP address of the packet
                ip_src = pkt.ip.src
                print "IPv4 src: " + ip_src
                
                #Destination IP address of the packet
                ip_dst = pkt.ip.dst
                print "IPv4 dst: " + ip_dst
                
                #If we encounter DNS packets we want to see which domains a user
                # is looking for so we can see what services they may use.               
                try:
                    #Full Qualified Domain Name
                    fqdn = pkt.dns.qry_name
                    #Adding the fqdn to a list so we can  go through the unique
                    # IP addresses we find and replace it with the fqdn
                    if fqdn not in dns_list:
                        dns_list.append(fqdn)
                except:
                    pass
                
                try:
                    #DNS response packets can have multiple answers to a DNS
                    # query, they can range from 1 - 9 answers so here we are
                    # trying to pick up as much as we can.
                    dns_addr[pkt.dns.a] = fqdn
                    dns_addr[pkt.dns.a_0] = fqdn
                    dns_addr[pkt.dns.a_1] = fqdn
                    dns_addr[pkt.dns.a_2] = fqdn
                    dns_addr[pkt.dns.a_3] = fqdn
                    dns_addr[pkt.dns.a_4] = fqdn
                    dns_addr[pkt.dns.a_5] = fqdn
                    dns_addr[pkt.dns.a_6] = fqdn
                    dns_addr[pkt.dns.a_7] = fqdn
                    dns_addr[pkt.dns.a_8] = fqdn
                except:
                   pass
                
                #Unique source/destination IP addresses are taken and added 
                # to a list   
                if ip_src not in ipv4:
                    ipv4.append(ip_src)
                    
                if ip_dst not in ipv4:
                    ipv4.append(ip_dst)
                
                #Checks protocol version of an IPv4 packet  
                if pkt.ip.proto == "6":
                    proto = "TCP"
                if pkt.ip.proto == "17":
                    proto = "UDP"
                print "Uses " + proto + " protocol"
            except:
                pass
             
            #Computing statistics from user A to user B
            try:         
                #Source MAC address
                eth_src = pkt.wlan.sa
                #Destination MAC address
                eth_dst = pkt.wlan.da
                #Integer version of time stamp
                ts = int(float(pktdata[0].sniff_timestamp))
                
                #Dictionary that takes and updates data sent between two users
                # the zeros count how many times the channel flags occur.
                # For example, if 3 2GHz cck signals were are between users 
                # the output of the flag counter would look like this:'
                # [..., ..., ..., ..., 0, 3, 0, 3, 0, 0, 0, 0]
                #Format: {key : [timestamp, MAC src, MAC dst, 
                # bits from src to dst, passive, 2GHz, ofdm, cck, gfsk, 5GHz,
                # gsm, cck_ofdm, # of packets in conversation, cumulitive 
                # signal strength,cumulitive data rate, duration (us)]}
                if eth_src not in ethDict:
                    ethDict[eth_src] = {eth_dst : [ts, eth_src, eth_dst, \
                    pktBits, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]} 
                #For multiple sources that have different destinations
                elif eth_dst not in ethDict[eth_src]: 
                    ethDict[eth_src].update({eth_dst :[ts, eth_src, eth_dst, \
                    pktBits, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]})
                #Updates already existing converations in dictionary
                else:
                    #Bits between user A and user B
                    ethDict[eth_src][eth_dst][3] += pktBits
                    #Number of packets between user A and user B
                    ethDict[eth_src][eth_dst][12] += 1
                    
                #Function calls for checking/updating channel flags   
                check_flags(pkt.radiotap,cflags)
                check_flags(pkt.radiotap,cflags_c)
                
                #This little block updates channel flags betweens users
                iterator = 4
                for f in cflags:
                    if iterator < 12:
                        ethDict[eth_src][eth_dst][iterator] += cflags_c[f]
                        iterator += 1
                
                #Looking at signal properties of the packet
                try:
                    #Determines the physical type, 802.11b/g/n
                    if pkt.wlan_radio.phy == "4":
                        phy = "b"
                    if pkt.wlan_radio.phy == "6":
                        phy = "g"
                    if pkt.wlan_radio.phy == "7":
                        phy = "n"
                    #Adding physical type to the dictionary
                    try:
                        #Updates the most recent physical type (802.11b/g/n)
                        if ethDict[eth_src][eth_dst][16]:
                            ethDict[eth_src][eth_dst][16] = phy
                    except:
                        #If it is in the dictionary it will be added
                        ethDict[eth_src][eth_dst].append(phy)
                    
                    #Signal strength in decibels
                    signal_strength = int(pkt.wlan_radio.signal_dbm)
                    #Adds to the signal strength part of the dictionary
                    ethDict[eth_src][eth_dst][13] += signal_strength
                    
                    #Data rate from source to destination in Mb/s
                    d_rate = int(pkt.wlan_radio.data_rate)
                    #Adds to the data rate part of the dictionary
                    ethDict[eth_src][eth_dst][14] += d_rate
                    
                    #Gives what channel is being used
                    channel = int(pkt.wlan_radio.channel)
                    #Channel frequency of the packet in MHz
                    freq = pkt.wlan_radio.frequency
                    
                    #Duration in microseconds
                    dur = int(pkt.wlan_radio.duration)
                    #Adds duration of the packet to get cumulitive value (us)
                    ethDict[eth_src][eth_dst][15] += dur
                    
                    #Preamble duration in microseconds
                    preamble = pkt.wlan_radio.preamble
                    print "Channel: " + str(channel)
                    print "Frequency: " + freq + " Mhz"
                    print "Preamble duration: " + preamble + " us\n"
                except:
                    pass
                
                #This adds all unique MAC addresses to a list and counts number 
                # of users based on number of unique MAC addresses
                if eth_src not in uniqueMAC:
                    uniqueMAC.append(eth_src)
                    numOfUsers += 1
                if eth_dst not in uniqueMAC:
                    uniqueMAC.append(eth_dst)
                    numOfUsers += 1 
            except:
                try:
                    #Work in progress to deal with a specific type of
                    # 802.11 packet
                    pkt.wlan.ra
                    
                except:
                    pass
            
            n += 1  
        
        #Gets time between final and first packet, this is computed to find bandwidth      
        total_duration = float(pktdata[n-1].sniff_timestamp) - float(pktdata[0].sniff_timestamp)
        #In the case that there is only one packet in the pcap file
        if total_duration <= 0:
            total_duration = 1
            
        #Average for signal strength and data rate:
        try:
            for k in ethDict:
                for j in ethDict[k]:
                    ethDict[k][j][13] = ethDict[k][j][13]/ethDict[k][j][12]
                    ethDict[k][j][14] = ethDict[k][j][14]/ethDict[k][j][12]
        except:
            pass
        
        #Puts ethDict into a more readable dictionary, ready to give to a database 
        #Format:
        # {key:[key, timestamp, MAC src, MAC dst, bits from src to dst, passive,
        # 2GHz, ofdm, cck, gfsk, 5GHz, gsm, cck_ofdm, # of pkt in convo, 
        # avg signal strength, avg data rate, cumulitive duration, physical type]}
        print cflags_c
        for k in ethDict: 
                for j in ethDict[k]:
                    l = str(int(float(pktdata[0].sniff_timestamp))) + str(k) + str(j)
                    if l not in ethFinal:
                        ethFinal[l] = ethDict[k][j] #[l] + #
        
        #Finally, we print everything
        if numOfUsers > 0: 
            print "Number of Users: "+str(numOfUsers)
            for z in uniqueMAC:
                print z
            print "Number of packets for this file: " + str(len(pktdata))
            print "Bandwidth is "+str(int(cumulBits/total_duration))+" bits/s\n"
            
            #Prints flags if they occured at least once
            for k in cflags:
                if cflags[k] > 0:
                    print k + ": " + str(cflags[k])
            
            #This goes through the ipv4 list and replaces matching IP addresses
            # with the full qualified domain name so that we can determine 
            # services
            for n in range(0, len(ipv4)):
                for h in dns_addr:
                    if ipv4[n] == h:
                        ipv4[n] = dns_addr[h]
            print ethFinal
            print"\n"
            print ipv4
            print"\n"
            print dns_addr
        else:
            print "There are no users/data for this pcap file: " + str(file_name)