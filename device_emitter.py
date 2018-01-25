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
print(pi_details)