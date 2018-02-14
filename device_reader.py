#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 10:18:46 2018

@author: root
"""

import DatabaseConnect as dc

db = dc.DatabaseConnect()
db.connect()
table_contents = db.readTable("ip")
db.disconnect()

#print(table_contents)


device_details = {} #mac address is key, ip address is value

for i in sorted(table_contents, key=lambda hello: hello[0]):
    device_details[i[1]] = i[2]

#print(device_details)
for j in device_details:
    print(str(j) + " -> " + str(device_details[j]))