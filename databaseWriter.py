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

To do:
    Currently this is dummy data. Once we have the structure of data that we want this will change to support extracting
    that data. This will involve changing Table names to access specific data. 
    
    Function to update data may be needed. When classifying types we may change classification and thus need to update the types in the         database. "databaseUpdate(databaseInput)"
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
    
    query = "INSERT INTO networkInfo (Source, Destination, Type, Download, Upload) VALUES (%s, %s, %s, %s, %s)"
        
    cur.execute(query, (databaseInput))
            
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
    
    
    query = "INSERT INTO networkInfo (Source, Destination, Type, Download, Upload) VALUES (%s, %s, %s, %s, %s)"
        

    cur.executemany(query, databaseInput)
 
    conn.commit()
    print("Data written")
    

    #cur.close()
    if conn is not None:
        conn.close()
        print('Database connection closed.')