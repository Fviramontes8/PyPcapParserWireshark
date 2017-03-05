'''
author: Seth Decker

Description: This code querys all data in a table of a posgreSQL database.

I/O:
    username: username to access database
    password: password to access database
    excel: True if you want an output xlsx file for external use
    path: define path to save excel file
    output: returns the data

Example:
    #>>> output = databaseReader(excel=True, output=True)
         Connecting to the PostgreSQL database...
         Connected to host '192.168.1.121'
         Data retrieved
         Database connection closed.

     output now contains the data from a table, and an xlsx file is also stored in the same directory as the program

To do:
    Currently this is dummy data. Once we have the structure of data that we want this will change to support extracting
    that data. This will involve changing Table names to access specific data.
'''

#import modules
import psycopg2
import pandas as pd
import os
from config import config

#query a table. Do not call this function
def _databaseRead():
    try:
        params = config()

        if params is None:
            return

        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        #conn = psycopg2.connect(dbname='networkinfodb',  user=username, password=password, host='192.168.1.121', port=5432)
        print("Connected to host '192.168.1.121'")
    except:
        print("Unable to connect to the database!")
        return
    
    cur = conn.cursor()
    
    cur.execute("""SELECT * from networkInfo""")
    print("Data retrieved")

    output = cur.fetchall()

    if conn is not None:
        conn.close()
        print('Database connection closed.')

    return output

#query a table interface. Use this function
def read(path=None, excel = False, output = True):

    #query all data from database
    data = _databaseRead()
    
    if excel == True:
        df = pd.DataFrame(data)
        if path is None:
            path = 'databaseOutput.xlsx'
            i = 0
            while(os.path.exists(path)):
                i = i + 1
                path = 'databaseOutput (' + str(i) + ').xlsx'
            writer = pd.ExcelWriter(path, engine='xlsxwriter')
        else:
            print("Not working yet")
            writer = pd.ExcelWriter(path, engine='xlsxwriter')
        # Convert the dataframe to an XlsxWriter Excel object.
        df.to_excel(writer, sheet_name='Sheet1')

        # Close the Pandas Excel writer and output the Excel file.
        writer.save()
    if output:
        return data
    

def databaseWrite(databaseInput, output = False):
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
        
    if len(databaseInput) > 1:
        print("many")
        print(databaseInput)
        cur.executemany(query, databaseInput)
    else:
        print("one")
        cur.execute(query, (databaseInput))
            
    conn.commit()
    print("Data written")
    

    #cur.close()
    if conn is not None:
        conn.close()
        print('Database connection closed.')
		
