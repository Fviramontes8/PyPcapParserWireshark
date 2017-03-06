from glob import glob 
import pyshark
'''import socket
import datetime'''

###Use .field_names to see what can be called from object
 
# Open saved trace file
for file_name in glob("*.pcap"):
    with open(file_name, "rb") as p_cap:
        cap = pyshark.FileCapture(p_cap)
        phy_list = []
        n = 0
        for z in cap:
            try:
                pkt = cap[n]
            except:
                print "Cannot open packet"
            #print pkt.ip.version
            print pkt.wlan_radio.field_names
            try:
                pkt.wlan_radio.phy
                phy = pkt.wlan_radio.phy
                if phy not in phy_list:
                    phy_list.append(phy)
            except:
                pass     
            n += 1         
        print "Physical list: " + str(phy_list)
                    
'''                print pkt.wlan.da
                print(pkt.length)
                print pkt.sniff_timestamp #UTC timestamp
                t_stamp = datetime.datetime.utcfromtimestamp(float(pkt.sniff_timestamp))
                print t_stamp
#source destination, mac, size/length, ip, dns lookup, time stamp


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
                    print "cannot resolve hostname: ", name_ip, err'''