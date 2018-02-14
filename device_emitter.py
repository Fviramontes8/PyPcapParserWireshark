# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 15:17:49 2018

@author: fviramontes8
"""

import DatabaseConnect as dc

db = dc.DatabaseConnect()
db.connect()
table_contents = db.readTable("ip")
db.disconnect()

#print(table_contents[0][0])
pi_details = {}
for i in table_contents:
    pi_details[i[0]] = [i[1], i[2]]
#print(pi_details)

text_object = open("ip.txt", "r")
#print(text_object.read())
ip_address = text_object.read()
text_object.close()
ip_address = ip_address.strip("\n")
ip_address = ip_address.strip()
#print("This computer's IP address: " + ip_address)

text_object = open("mac.txt", "r")
mac_address = text_object.read()
text_object.close()
mac_address = mac_address.strip("\n")
#print("This computer's MAC address: " + mac_address)

for pi_iterator in range(len(pi_details)):
    database_ip = pi_details[pi_iterator+1][1]
    #print("Database: " + database_ip)
    if(database_ip == ip_address):
        ip_check = 0
        print("There is an IP address, here is the key: " +str(pi_iterator+1))
    else:
        #print("There is no match for IP!")
        ip_check = 1
    #print("ip_check: " + str(ip_check))

mac_check = 0

if(ip_check):
    for pi_iterator in range(len(pi_details)):
        database_mac = pi_details[pi_iterator+1][0]
        #print("Database: " + database_mac)
        if(database_mac == mac_address):
            mac_check = 0
            print("There is a MAC address, here is the key: " +str(pi_iterator+1))
            #db.deleteIPData(pi_iterator+1)
        else:
            mac_check = 1
            #print("There is no match for MAC!")
        #print("mac_check: " + str(mac_check))

if(mac_check):
    print("This device is not on the database!")
    db.connect()
    key = db.getNextKey("ip")
    db.disconnect()
    key += 1
    #print("Next key: " + str(key))
    pi_upload = [key, mac_address, ip_address]
    db.connect()
    db.writeDeviceData("ip", pi_upload)
    db.disconnect()
