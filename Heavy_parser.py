''' 
Authors: Francisco Viramontes, Seth Decker

Description: This program is a packet parser intended to firstly, take 
 statistical information from all the users in one pcap file in the working 
 folder and organizes it between a set amount of conversations between two 
 users and displays it in a list. 
 
 Secondly, it is also intended to take all unique IP addresses that are in the
 pcap file and put it into a list. 
 
 Lastly, the parser will see if there are any packets that use the Domain Name 
 Service protocol (dns) and check the dns packets for answers. If the dns 
 packets have answers it will try to read them and put them into a dictionary
 so that they can use the list of unique IP addresses and see what websites 
 were visited to determine what services (Video, Audio, VoIP, etc) were used.

Input: Any pcap file that has packets that use 802.11 protocols, this parser 
 DOES NOT WORK with pcap files that captured packets via Ethernet connection.
 This parser has only worked with pcap files from wireshark so far.

Output: This parser has 3 intended outputs

 The statistical converation list (Displays two converations between four users)
 [['14914988132c:56:xx:xx:50:e1ff:ff:ff:ff:ff:ff', 1491498813, 
 '2c:56:xx:xx:50:e1','ff:ff:ff:ff:ff:ff', 9880, 0, 5, 0, 5, 0, 0, 0, 0, 4, -102,
 1, 0, 0, 'b'], ['149149881300:0b:xx:xx:59:c020:68:xx:xx:d4:74', 1491498813, 
 '00:0b:xx:xx:59:c0','20:68:xx:xx:d4:74', 9814768, 0, 873, 59, 0, 0, 0, 0, 814,
 872, -36, 55, 0, 0, 'n']]

 Unique IP address list
 ['91.189.91.26', '10.81.198.43', '72.21.91.29']

 dns answer dictionary
 {'172.217.5.78':'www.youtube.com', '52.26.140.68':'services.addons.mozilla.org',
 '216.58.193.194':'securepubads.g.doubleclick.net', '172.217.5.67':'fonts.gstatic.com', 
 '208.77.78.221': 'www.google.com', '54.191.164.105': 'aus5.mozilla.org', 
 '54.68.139.233': 'services.addons.mozilla.org', '172.217.4.131': 'www.gstatic.com',
 '52.11.31.31': 'incoming.telemetry.mozilla.org', '35.166.101.77': 'aus5.mozilla.org'}
'''

from glob import glob
import pyshark

##################################################################

# Take a look at keeping the program running (maybe a command prompt script??),
# and finalize list to add to the table.

#########################################################

#This function checks specific channel flags of a packet
# also updates ethDict
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
        #Returns the updated dictionary
        return cflags
    except:
        pass

#Looks for any pcap files in working directory
for file_name in sorted(glob("*.pcap")):
    #If there are any, it will open them as pcap_data
    with open(file_name, "rb") as pcap_data:
        #Loads .pcap data into variable "pktdata"
        pktdata = pyshark.FileCapture(pcap_data, keep_packets = False)
        #Empty list of Unique MAC addresses
        uniqueMAC = []                            
        #Interger counter for number of users based on unique MAC address
        numOfUsers= 0                               
        #Cumulitive Bits
        cumulBits = 0                          
        #List for unique IPv4 addresses
        ipv4 = []
        #List of dns answers for the pcap file (if there are any)
        dns_list = []
        #Gets dns answers (if any) and puts in a dictionary.
        # It has this format: {ip_addr : website that it belongs to}
        dns_addr = {}                             
        #Dictionary that reads on organizes statistics from packets
        ethDict = {}  
        #Cumulitive channel flag counter
        cflags = {"cck": 0,"ofdm": 0,"twoghz": 0,"fiveghz": 0,\
        "passive": 0,"cck_ofdm": 0,"gfsk": 0,"gsm": 0} 
        #This list gets everything ready to upload to a database
        listFinal = []
        
        n = 0
        for z in pktdata:
###############################################################################
            #Needs to be documented
            pkt = pktdata.next()
            if n == 0:
                pktfirst = pkt
################################################################################
            #Packet number
            print "Packet: " + str(n+1)
            #Timestamp in UTC/Epoch time
            ##print pkt.sniff_timestamp
            
            #Channel Flag counter between two users
            cflags_c = {"cck": 0,"ofdm": 0,"twoghz": 0,"fiveghz": 0,\
            "passive": 0,"cck_ofdm": 0,"gfsk": 0,"gsm": 0} 
            
            #Computing bits in packet n and adding to cumulitive bits
            try:
                #Amount of bits from the nth packet
                pktBits = int(pkt.length) * 8
                #Calculation of cumulitive bits
                cumulBits += pktBits
            except:
                pass
                
            #Taking a look at IPv4 information
            try:
                #Source IP address of the packet
                ip_src = pkt.ip.src
                #Destination IP address of the packet
                ip_dst = pkt.ip.dst
                
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
            except:
                pass
             
            #Computing statistics from user A to user B
            try:         
                #Source MAC address
                eth_src = pkt.wlan.sa
                #Destination MAC address
                eth_dst = pkt.wlan.da
                #Integer version of time stamp
                ts = int(float(pktfirst.sniff_timestamp))
                
                #Dictionary that takes and updates statistics sent between two 
                # users. This is the Format: 
                # {key : [timestamp, MAC src, MAC dst, bits from src to dst, 
                # passive, 2GHz, ofdm, cck, gfsk, 5GHz, gsm, cck_ofdm,
                # number of packets in conversation, cumulitive signal strength,
                # cumulitive data rate, duration (us), preamble duration (us),
                # physical type]}
                if eth_src not in ethDict:
                    ethDict[eth_src] = {eth_dst : [ts, eth_src, eth_dst,\
                    pktBits, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "0"]} 
                #For multiple sources that have different destinations
                elif eth_dst not in ethDict[eth_src]: 
                    ethDict[eth_src].update({eth_dst :[ts, eth_src, eth_dst,\
                    pktBits, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, "0"]})
                #Updates already existing converations in dictionary
                else:
                    #Bits between user A and user B
                    ethDict[eth_src][eth_dst][3] += pktBits
                    #Number of packets between user A and user B
                    ethDict[eth_src][eth_dst][12] += 1
                    
                #Function calls for checking/updating channel flags   
                check_flags(pkt.radiotap,cflags)
                check_flags(pkt.radiotap,cflags_c)
                
                #This block updates channel flags betweens users in ethDict
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
                        if ethDict[eth_src][eth_dst][17]:
                            ethDict[eth_src][eth_dst][17] = phy
                    except:
                        pass
                    
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
                    preamble = int(pkt.wlan_radio.preamble)
                    #Adds preamble duration of packet to get cumulitive 
                    # value (us)
                    ethDict[eth_src][eth_dst][16] += preamble
                    
                    print "Channel: " + str(channel)
                    print "Frequency: " + freq + " Mhz"
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
###############################################################################
#Needs documentation
        if n != 0:
            pktlast = pkt
###############################################################################
                
            #Average for signal strength and data rate:
            try:
                for k in ethDict:
                    for j in ethDict[k]:
                        #Number of packets in converation/total signal strength
                        ethDict[k][j][13] = ethDict[k][j][13]/ethDict[k][j][12]
                        #Number of packets in converation/total data rate
                        ethDict[k][j][14] = ethDict[k][j][14]/ethDict[k][j][12]
            except:
                pass
            
            #Puts ethDict into a more readable list, ready to push to a database 
            #Format:
            # [key, timestamp, MAC src, MAC dst, bits from src to dst, passive,
            # 2GHz, ofdm, cck, gfsk, 5GHz, gsm, cck_ofdm, # of pkt in convo, 
            # avg signal strength, avg data rate, cumulitive duration,
            # cumulitive preamble duration, physical type]
            for k in ethDict: 
                    for j in ethDict[k]:
                        #The key is made by concatenating the timestamp with
                        # source and destination MAC addresses
                        l = str(int(float(pktfirst.sniff_timestamp))) + str(k) + str(j)
                        listFinal.append([l] + ethDict[k][j])
            
            #Finally, we print everything
            if numOfUsers > 0: 
                print "Number of Users: "+str(numOfUsers)
#                for z in uniqueMAC: #prints unique MAC addresses
#                    print z
#                print "Number of packets for this file: " + str(len(pktdata))
#                print "Bandwidth is "+str(int(cumulBits/total_duration))+" bits/s\n"
                
                #Prints flags if they occured at least once
#                for k in cflags:
#                    if cflags[k] > 0:
#                        print k + ": " + str(cflags[k])
                
                #This goes through the ipv4 list and replaces matching IP addresses
                # with the full qualified domain name so that we can determine 
                # services
                for n in range(0, len(ipv4)):
                    for h in dns_addr:
                        if ipv4[n] == h:
                            ipv4[n] = dns_addr[h]
                
                #The three intended outputs
                print listFinal
                print"\n"
                print ipv4
                print"\n"
                print dns_addr
            else:
                print "There are no users/data for this pcap file: " + str(file_name)