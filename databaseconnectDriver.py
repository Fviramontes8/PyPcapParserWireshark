'''
author: Seth Decker

Description: This code is a driver to test databaseReader and databaseVerification



Output:
    #>>> python databaseTestDriver
         Connecting to the PostgreSQL database...
         PostgreSQL database version:
         ('PostgreSQL 9.6.2, compiled by Visual C++ build 1800, 64-bit',)
         Database connection closed.
         
         [('192.168.1.121', '255.255.255.0', 'video', 250.0, 1.5),
         ('192.168.1.122', '255.255.255.1', 'blog', 55.0, 12.5),
         ('192.168.1.123', '255.255.255.2', 'video', 356.0, 15.5),
         ('192.168.1.124', '255.255.255.3', 'music', 157.0, 17.5),
         ('192.168.1.125', '255.255.255.4', 'other', 58.0, 15.5),
         ('192.168.1.126', '255.255.255.5', 'other', 9.0, 12.5)]
         
         Connecting to the PostgreSQL database...
         Connected to host '192.168.1.121'
         Data written
         Database connection closed.
         
         [('192.168.1.121', '255.255.255.0', 'video', 250.0, 1.5),
         ('192.168.1.122', '255.255.255.1', 'blog', 55.0, 12.5),
         ('192.168.1.123', '255.255.255.2', 'video', 356.0, 15.5),
         ('192.168.1.124', '255.255.255.3', 'music', 157.0, 17.5),
         ('192.168.1.125', '255.255.255.4', 'other', 58.0, 15.5),
         ('192.168.1.126', '255.255.255.5', 'other', 9.0, 12.5),
         ('202.163.1.248', '255.255.244.5', 'other', 9.0, 12.5),
         ('155.163.5.155', '255.255.255.5', 'other', 9.0, 12.5)]
'''

import DatabaseConnect as dc

database = dc.DatabaseConnect()
print("hello")
database.connect()

print(database.getTableNames())
data_list = []

#database.writeData(data_list)

#database.writeData("")
#database.writeIP((3, "1.1.1.3"))
print(database.readIPTable())
print(database.getNextMACKey())
#print(database.describe())
print(database.getIPAddress(7))
print(database.getIPAddressKey("1.1.1.1"))
print(database.getIPAddressKey("1.1.1.5"))