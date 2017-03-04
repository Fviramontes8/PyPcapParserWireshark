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
    output = dr.databaseReader(username='postgres', password='postgres', excel=True, output=True)

    output now contains the data from a table, and an xlsx file is also stored in the same directory as the program

To do:
    Currently this is dummy data. Once we have the structure of data that we want this will change to support extracting
    that data. A configuration file will be created to access the/any database with user/pass more easily and will be imported.
'''
#import modules
import psycopg2
import pandas as pd
import os

#query a table. Do not call this function
def _databaseQuery(username, password):
    try:
        conn = psycopg2.connect(dbname='networkinfodb',  user=username, password=password, host='192.168.1.121', port=5432)
        print("Connected to host '192.168.1.121'")
    except:
        print("Unable to connect to the database!")
        
    cur = conn.cursor()
    
    try:
        cur.execute("""SELECT * from Cars""")
        print("Data retrieved")
    except:
        print("Error accessing database")
    
    return cur.fetchall()

#query a table interface. Use this function
def databaseReader(username=None, password=None, path=None, excel = False, output = True):
    if username is None:
        print('Username is required')
        return
    elif password is None:
        print('Password is required')
        return
    
    #query all data from database
    data = _databaseQuery(username, password)
    
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
		
