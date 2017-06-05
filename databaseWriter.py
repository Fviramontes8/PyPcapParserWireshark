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

     Tuple "data" is now in the list. If the key value matches with a key
     value in the database table, an error will occur.
     
    #>>> data = (('192.163.1.248', '255.255.244.5', 'other', 9.0, 12.5),
    ('173.163.5.155', '255.255.255.5', 'other', 9.0, 12.5))
    #>>> output = databaseWriteList(data)
         Connecting to the PostgreSQL database...
         Connected to host '192.168.1.121'
         Data written
         Database connection closed.
'''

import psycopg2
from psycopg2 import sql
import time
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
    
    query = "INSERT INTO networkTest11 (Key, Timestamp, SourceMAC, DestinationMAC, TotalBits, FlagPassive, Flag2GHz, FlagOFDM, FlagCCK, FlagGFSK, Flag5GHz, FlagGSM, FlagCCKOFDM, TotalPackets, SignalStrength, DataRate, Duration, PhysType) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"    
   
    cur.execute(query, databaseInput)
            
    conn.commit()
    print("Data written")
    

    #cur.close()
    if conn is not None:
        conn.close()
        print('Database connection closed.')

def databaseWriteList(databaseInput, table_time = "None", table_type = "None"):
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
    
    #query = sql.SQL("CREATE TABLE {}" + args).format(sql.Identifier(table_time + table_type))
    
    query = sql.SQL("INSERT INTO {} (Key, Timestamp, SourceMAC, DestinationMAC, TotalBits, FlagPassive, Flag2GHz, FlagOFDM, FlagCCK, FlagGFSK, Flag5GHz, FlagGSM, FlagCCKOFDM, TotalPackets, SignalStrength, DataRate, Duration, DurationPreamble, PhysType) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)").format(sql.Identifier(table_time + table_type))   
    if not tableExists(cur, table_time + table_type):
        print("abana" + table_type)
        databaseWriteTable(table_time, table_type)
    
    cur.executemany(query, databaseInput)
 
    conn.commit()
    print("Data written")

    #cur.close()
    if conn is not None:
        conn.close()
        print('Database connection closed.')
        
def databaseWriteTable(table_time = None, table_type=None):
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
    print(table_type)
    cur = conn.cursor()
    if table_type is None:
        print("To create a table a table type must be defined. Use argument table_type to specify")
        conn.close()
        return

    if table_time is None:
        table_time = time.strftime("%m-%d-%Y")
    table_name = table_time + table_type
    #see if table exists

    if tableExists(cur, table_name) is False:
        if table_type is not None:
                    #(Key, Timestamp, SourceMAC, DestinationMAC, TotalBits, FlagPassive, Flag2GHz, FlagOFDM, FlagCCK, FlagGFSK, Flag5GHz, FlagGSM, FlagCCKOFDM, TotalPackets, SignalStrength, DataRate, Duration, PhysType)
            args = "(Key VARCHAR(30) PRIMARY KEY, Timestamp INT, SourceMAC VARCHAR(20), DestinationMAC VARCHAR(20), TotalBits INT, FlagPassive INT, Flag2GHz INT, FlagOFDM INT, FlagCCK INT, FlagGFSK INT, Flag5GHz INT, FlagGSM INT, FlagCCKOFDM INT, TotalPackets INT, SignalStrength INT, DataRate INT, Duration INT, DurationPreamble INT, PhysType VARCHAR(3))"
        else:
            print("Table type " + table_type + " does not exist")
            conn.close()
            return
        query = sql.SQL("CREATE TABLE {}" + args).format(sql.Identifier(table_time + table_type))
        
        cur.execute(query)
        print("Table created")
        #cur.execute("CREATE TABLE networkTest11 (Key VARCHAR(50) PRIMARY KEY, TimeStamp VARCHAR(20), SourceMAC VARCHAR(20), DestinationMAC VARCHAR(20), Bandwidth INT, FLAG1 INT, FLAG2 INT, FLAG3 INT, FLAG4 INT, FLAG5 INT, FLAG6 INT, FLAG7 INT, FLAG8 INT, FLAG9 INT, FLAG10 INT)")
    else:
        print("Table already exists")
    conn.commit()
    conn.close()

def tableExists(cursor, table_name):
    cursor.execute("select exists(select * from information_schema.tables where table_name=%s)", (table_name,))
    return cursor.fetchone()[0]