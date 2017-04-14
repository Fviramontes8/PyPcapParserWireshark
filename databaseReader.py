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
from psycopg2 import sql
import pandas as pd
import os
from config import config



def getTableNames():
    try:
        print("hello world")
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
    
    cur.execute("select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';")
    out = cur.fetchall()
    table_names = [x[0] for x in out]
    return table_names
    

def _databaseConnect():
    try:
        print("hello world")
        params = config()

        if params is None:
            return

        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        
        print("Connected to host '192.168.1.121'")
        return conn
    except:
        print("Unable to connect to the database!")
        return
    

#query a table. Do not call this function
def _databaseRead(table_name="None"):
    if table_name not in getTableNames():
        print("table " + str(table_name) + " does not exist")
        return
    conn = _databaseConnect()
    
    if conn is not None:
        cur = conn.cursor()
        print(table_name)
        query = sql.SQL("select * from {} as a").format(sql.Identifier(table_name))
        cur.execute(query)
        #cur.execute("""SELECT * from networkTest11""")
        print("Data retrieved")
    
        output = cur.fetchall()
    
        if conn is not None:
            conn.close()
            print('Database connection closed.')
    
        return output
        
    else:
        print("Could not connect to database")
    return

#query a table interface. Use this function
def read(table_name="None", path=None, excel = False, output = True):

    #query all data from database
    data = _databaseRead(table_name)
    
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
    