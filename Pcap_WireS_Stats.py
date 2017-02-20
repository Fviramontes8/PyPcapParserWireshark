from glob import glob
import math
from pcapfile import savefile
from pcapfile.protocols.linklayer import ethernet
import datetime


for file_name in glob("*.pcap"):
    with open(file_name, "rb") as pcap_data:      #Opens .json files in working directory
        pdata = savefile.load_savefile(pcap_data, verbose=True)#Loads .json data into variable "data" 
        uniqueEth = []                       #Empty list of Unique MAC addresses
        nOU= 0                               #Number of Users
        cBits = 0                            #Cumulitive Bits
        ethDict = {}                         #Dictionary that holds Source MAC 
                                             # address, destination MAC addresses
                                             # and bits from source to destination
        
        for n in range(0, len(pdata)):
            #Amount of bits from the nth packet
            dBits = int(data[n]["_source"]["layers"]["frame"]\
            ["frame.len"]) * 8
            #Simple calculation of cumulitive bits
            cBits += dBits
            #Source MAC address
            data_src = str(data[n]["_source"]["layers"]["eth"]["eth.src"])
            #Destination MAC address
            data_dst = str(data[n]["_source"]["layers"]["eth"]["eth.dst"])
            #Computes bandwidth
            cBand = math.trunc(cBits / float(data[len(data) - 1]["_source"]["layers"]\
            ["frame"]["frame.time_relative"]))

            #Adds source and destination MAC address and the number of bits
            # from source to destination into a dictionary, modeled like this:
            # {src1 :{dst1 : bits from src1 to dst1}, {dst2 : bits from src1 to dst2}}   
            if data_src not in ethDict:             #Adds to dictionary with initial bits
                ethDict[data_src] = {data_dst : dBits}
            elif data_dst not in ethDict[data_src]: #Adds additional destinations
                ethDict[data_src].update({data_dst : dBits})
            else:                                   #Updates bits in dictionary
                ethDict[data_src][data_dst] += dBits
        
            #This adds all unique MAC addresses to a list
            if data_src not in uniqueEth:
                uniqueEth.append(data_src)
                nOU += 1
            if data_dst not in uniqueEth:
                uniqueEth.append(data_dst)
                nOU += 1

        print "Number of Users: "+str(nOU)
        for z in uniqueEth:
            print z
        print "\nBandwidth is "+str(cBand)+" bits/s \n"
        for k in ethDict: 
            for n in ethDict[k]:
                print "From " + str(k) + " to " + str(n)+" is " +\
                str(ethDict[k][n]) + " bits"