from glob import glob 
import pyshark

##########################################################

#Figure out connecting dns canon names, query names to ip addrs

###########################################################
 
###Use .field_names to see what can be called from object
dns_addr = {}
for file_name in glob("*.pcap"):
    with open(file_name, "rb") as p_cap:
        cap = pyshark.FileCapture(p_cap)
        ip_list = []
        dns_list = []
        n = 0
        for z in cap:
            print n
            try:
                pkt = cap[n]
            except:
                print "Cannot open packet"
            #print pkt.ip.version
            try:
                #print pkt.dns.qry_name
                #print pkt.dns.cname
                 pkt.dns.a
            except:
                pass
            try:
                fqdns = pkt.dns.qry_name
                print fqdns
                if fqdns not in dns_list:
                    dns_list.append(fqdns)
            except:
                pass     
            n += 1
                    
#                print pkt.wlan.da
#                print(pkt.length)
#                print pkt.sniff_timestamp #UTC timestamp
#                t_stamp = datetime.datetime.utcfromtimestamp(float(pkt.sniff_timestamp))
#                print t_stamp
#source destination, mac, size/length, ip, dns lookup, time stamp


            try:
                #print("\nIP information:")
                name_ip_src = pkt.ip.src
                #print "Src IP: " + name_ip_src
                
                try:
                    dns_canonName = pkt.dns.cname
                    dns_addr[pkt.dns.a] = fqdns
                    dns_addr[pkt.dns.a_0] = fqdns
                    dns_addr[pkt.dns.a_1] = fqdns
                    dns_addr[pkt.dns.a_2] = fqdns
                    dns_addr[pkt.dns.a_3] = fqdns
                    dns_addr[pkt.dns.a_4] = fqdns
                    dns_addr[pkt.dns.a_5] = fqdns
                    dns_addr[pkt.dns.a_6] = fqdns
                    dns_addr[pkt.dns.a_7] = fqdns
                    dns_addr[pkt.dns.a_8] = fqdns
                    dns_addr[pkt.dns.a_9] = fqdns
                except:
                   pass
                if name_ip_src not in ip_list:
                    ip_list.append(name_ip_src)
    
                name_ip_dst = pkt.ip.dst
                #print "Dst IP: " + name_ip_dst
                if name_ip_dst not in ip_list:
                    ip_list.append(name_ip_dst)
            except:
                pass
        for n in range(0, len(ip_list)):
            for h in dns_addr:
                if ip_list[n] == h:
                    ip_list[n] = dns_addr[h]
        print dns_list
        print ip_list
print dns_addr