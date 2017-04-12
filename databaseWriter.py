'''
author: Seth Decker

Description: This code querys all data in a table of a posgreSQL database.

I/O:
    databaseInput: data to write to databse. In the form of a tuple of tuples

Example:
    #>>> data = (('273.163.1.126', '255.255.255.5', 'other', 9.0, 12.5))
    #>>> output = databaseWrite(data)
         Connecting to the PostgreSQL database...
         Connected to host '192.168.1.121'
         Data written
         Database connection closed.

     Tuple "data" is now in the list. If the key value matches with a key value in the database table, an error will occur.
     
    #>>> data = (('192.163.1.248', '255.255.244.5', 'other', 9.0, 12.5),('173.163.5.155', '255.255.255.5', 'other', 9.0, 12.5))
    #>>> output = databaseWriteList(data)
         Connecting to the PostgreSQL database...
         Connected to host '192.168.1.121'
         Data written
         Database connection closed.
'''

import psycopg2
from config import config

def databaseWrite(databaseInput):
    try:
        params = config()

        if params is None:
            return

        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        print("Connected to host '192.168.1.121'")
    except:
        print("Unable to connect to the database!")
        return
    
    cur = conn.cursor()
    
    #query = "INSERT INTO networkInfo (Source, Destination, Type, Download, Upload) VALUES (%s, %s, %s, %s, %s)"
    #query = "INSERT INTO networkInfo (Source, Destination, Type, Download, Upload) VALUES (%s, %s, %s, %d, %d, %s, %d, %d, %d, %d, %d, %d)"
    #query = "INSERT INTO networkTest (Key, SourceIP, DestinationIP, SourcePort, DestinationPort, PhysType, ChannelFlag, ChannelNumber, ChannelFrequency, DataRateIn, SignalStrength, Bandwidth) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"    
    query = "INSERT INTO networkTest11 (Key, Timestamp, SourceMAC, DestinationMAC, Bandwidth, flag1, flag2, flag3, flag4, flag5, flag6, flag7, flag8, flag9, flag10) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"    
   
    cur.execute(query, databaseInput)
            
    conn.commit()
    print("Data written")
    

    #cur.close()
    if conn is not None:
        conn.close()
        print('Database connection closed.')

def databaseWriteList(databaseInput):
    try:
        params = config()

        if params is None:
            return

        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        print("Connected to host '192.168.1.121'")
    except:
        print("Unable to connect to the database!")
        return
    
    cur = conn.cursor()
    
    query = "INSERT INTO networkTest (Key, SourceIP, DestinationIP, SourcePort, DestinationPort, PhysType, ChannelFlag, ChannelNumber, ChannelFrequency, DataRateIn, SignalStrength, Bandwidth) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"    

    cur.executemany(query, databaseInput)
 
    conn.commit()
    print("Data written")

    #cur.close()
    if conn is not None:
        conn.close()
        print('Database connection closed.')
        
def databaseWriteTable():
    try:
        params = config()

        if params is None:
            return

        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        print("Connected to Database")
    except:
        print("Unable to connect to the database!")
        return
    
    cur = conn.cursor()
    
    #cur.execute("CREATE TABLE networkTest (Key VARCHAR(30) PRIMARY KEY, SourceIP VARCHAR(20), DestinationIP VARCHAR(20), SourcePort INT, DestinationPort INT, PhysType VARCHAR(20), ChannelFlag INT, ChannelNumber INT, ChannelFrequency INT, DataRateIn INT, SignalStrength INT, Bandwidth INT)")
    cur.execute("CREATE TABLE networkTest11 (Key VARCHAR(50) PRIMARY KEY, TimeStamp VARCHAR(20), SourceMAC VARCHAR(20), DestinationMAC VARCHAR(20), Bandwidth INT, FLAG1 INT, FLAG2 INT, FLAG3 INT, FLAG4 INT, FLAG5 INT, FLAG6 INT, FLAG7 INT, FLAG8 INT, FLAG9 INT, FLAG10 INT)")
    
    conn.commit()
    conn.close()
