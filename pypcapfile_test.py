from glob import glob
from pcapfile import savefile
from pcapfile.protocols.linklayer import ethernet
from pcapfile.protocols.network import ip
import datetime
import binascii
for file_name in glob("*.pcap"):        #Opens .pcap files in folder
    with open(file_name, "rb") as testC:
        print file_name
        pdata = savefile.load_savefile(testC, layers = 1, verbose=True) 
        for n in range(0,len(pdata.packets)):
            pkt = pdata.packets[n]
            
            print len(pkt)
            #eth_frame = ethernet.Ethernet(pdata.packets[n].raw())
            #ip_frame = ip.IP(binascii.unhexlify(eth_frame.payload))
            #print ip_frame.len
            #print eth_frame.src + " " + eth_frame.dst
            #print"Timestamp: ", str(datetime.datetime.utcfromtimestamp(pkt.timestamp))
            