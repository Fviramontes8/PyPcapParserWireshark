from configparser import ConfigParser
import os
import psycopg2
from psycopg2 import sql
import pandas as pd

class DatabaseConnect(object):
    
    def __init__(self):
        self.conn = None

        self.mac_address_table_name = "MACAddressTable"
        self.ip_address_table_name = "IPAddressTable"
        self.data_table_name = "DataTable"
        
        self.data_table_query = "(Key, Timestamp, SourceMAC, DestinationMAC, TotalBits, FlagPassive, Flag2GHz, FlagOFDM, FlagCCK, FlagGFSK, Flag5GHz, FlagGSM, FlagCCKOFDM, TotalPackets, SignalStrength, DataRate, Duration, DurationPreamble, PhysType) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        self.mac_table_query = "(Key INT PRIMARY KEY, MACAddress VARCHAR(20)) VALUES (%s, %s)"
        self.ip_table_query = "(Key INT PRIMARY KEY, IPAddress VARCHAR(20)) VALUES (%s, %s)"
        
        
    def _config(self, filename='database.ini', section='postgresql'):
        # create a parser
        parser = ConfigParser()
        # read config file
        if os.path.exists(filename):
            parser.read(filename)
    
            # get section, default to postgresql
            db = {}
            if parser.has_section(section):
                params = parser.items(section)
                for param in params:
                    db[param[0]] = param[1]
            else:
                print("expection called")
                raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    
            return db
        else:
            print("Configuration file does not exist")
            return None

    def _tableExists(cursor, table_name):
        cursor.execute("select exists(select * from information_schema.tables where table_name=%s)", (table_name,))
        return cursor.fetchone()[0]

    ## Public Functions
    def getMACAddress(self, mac_address_key):
        print("returned mac address.")
        
    def getMACAddressKey(self, mac_address):
        print("returned mac address key.")
        
    def getIPAddress(self, ip_address_key):
        print("returned ip address.")
        
    def getIPAddressKey(self, ip_address):
        print("returned ip address key.")
        
    def readData(self):
        if _checkConnection():
            cur = conn.cursor()
            print(table_name)
            query = sql.SQL("select * from {} as a").format(sql.Identifier(data_table_name))

            cur.execute(query)
            print("Data retrieved")
        
            output = cur.fetchall()
        
            return output
        return
        
    def writeData(new_table_data):
        if _checkConnection():
            cur = self.conn.cursor()
            
            query = sql.SQL("INSERT INTO {} " + self.data_table_query).format(sql.Identifier(self.data_table_name))   
            
            cur.executemany(query, new_table_data)
        
            self.conn.commit()
        
    def connect(self):
        try:
            params = self._config()
    
            if params is None:
                print("Unable to connect to the database! No Params.")
                return
    
            self.conn = psycopg2.connect(**params)
            print("Connected.")
        except:
            print("Unable to connect to the database!")

    def disconnect(self):
        print("disconnecting.")
        if self.conn is not None:
            self.conn.close()
    
    #ignore this function                
    def writeTable(table_time = None, table_type=None):
        return
        cur = self.conn.cursor()
        
        #see if table exists
    
        if _tableExists(cur, table_name) is False:
            if table_type is not None:
            else:
                print("Table type " + table_type + " does not exist")
                return
            query = sql.SQL("CREATE TABLE {}" + args).format(sql.Identifier(self.data_table_name))
            
            cur.execute(query)
            print("Table created")
        else:
            print("Table already exists")

    def _checkConnection(self):
        if self.conn is None:
            print("No connection established. Use obj.connect() to connect to database.")
            return False
        else:
            return True    
    def getTableNames(self):
        if _checkConnection():
            cur = self.conn.cursor()
    
            cur.execute("select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';")
            out = cur.fetchall()
            table_names = [x[0] for x in out]
            return table_names