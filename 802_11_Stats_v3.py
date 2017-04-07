from glob import glob
import pyshark

#field_names
for file_name in glob("*.pcap"):
    #Opens .pcap files in working directory
    with open(file_name, "rb") as pcap_data:
        #Loads .pcap data into variable "pdata"
        pktdata = pyshark.FileCapture(pcap_data) 
        
        n = 0
        for z in pktdata: #((
            pkt = pktdata[n]
            #Packet number
            print "Packet: " + str(n+1)
            #Timestamp in UTC/Epoch time
            print pkt.sniff_timestamp
            
            print pkt.wlan_radio.field_names
            print pkt.wlan.ra
            print pkt.wlan_radio.phy
            print pkt.wlan_radio.data_rate
            print pkt.wlan_radio.channel
            print pkt.wlan_radio.frequency
            print pkt.wlan_radio.signal_dbm
            print pkt.wlan_radio.duration
            print pkt.wlan_radio.preamble
            

            n += 1 
            #))