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
        self.mac_table_query = "(Key , MACAddress) VALUES (%s, %s)"
        self.ip_table_query = "(Key , IPAddress) VALUES (%s, %s)"
        
    def _checkConnection(self):
        if self.conn is None:
            print("No connection established. Use obj.connect() to connect to database.")
            return False
        else:
            return True  
    
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

    def _tableExists(self, cursor, table_name):
        cursor.execute("select exists(select * from information_schema.tables where table_name=%s)", (table_name,))
        return cursor.fetchone()[0]

    ## Public Functions
    def getMACAddress(self, mac_address_key):
        print("returned mac address.")
        
    def getMACAddressKey(self, mac_address):
        
        #query for address
        #if it doesn't exist add mac_address to list
        #add new key set to max
        #return key
        print("returned mac address key.")
        
    def getIPAddress(self, ip_address_key):
        if self._checkConnection():
            cur = self.conn.cursor()
            query = sql.SQL("SELECT * FROM {} WHERE IPAddress = (SELECT IPAddress FROM {} WHERE id = {})").format(sql.Identifier(self.data_table_name), sql.Identifier(self.data_table_name), sql.Identifier(ip_address_key))
            cur.execute(query)
            latest_key = cur.fetchall()
            return latest_key
            print("returned ip address.")
        
    def getIPAddressKey(self, ip_address):
        print("returned ip address key.")

    
    def getNextKey(self, table_name):
        if self._checkConnection():
            cur = self.conn.cursor()
            query = sql.SQL("SELECT MAX(Key) from {}").format(sql.Identifier(table_name))
            cur.execute(query)
            latest_key = cur.fetchall()
            res_list = [x[0] for x in latest_key]
            return res_list[0]

    def getNextMACKey(self):
        return self.getNextKey(self.mac_address_table_name)
        
    def getNextIPKey(self):
        return self.getNextKey(self.ip_address_table_name)
        
    def getNextDataKey(self):
        return self.getNextKey(self.data_table_name)
        
    def readTable(self, table_name):
        if self._checkConnection():
            cur = self.conn.cursor()
            query = sql.SQL("select * from {} as a").format(sql.Identifier(table_name))
            cur.execute(query)
            print("Data retrieved")
        
            output = cur.fetchall()
        
            return output
        return
        
    def readDataTable(self):
        return self.readTable(self.data_table_name)
         
    def readIPTable(self):
        return self.readTable(self.ip_address_table_name)
    
    def readMACTable(self):
        return self.readTable(self.mac_address_table_name)
        
    def writeData(self, new_table_data):
        if self._checkConnection():
            cur = self.conn.cursor()
            
            query = sql.SQL("INSERT INTO {} " + self.data_table_query).format(sql.Identifier(self.data_table_name))   
            
            cur.executemany(query, new_table_data)
        
            self.conn.commit()
            
    def writeIP(self, new_ip_data):
        if self._checkConnection():
            cur = self.conn.cursor()
            
            query = sql.SQL("INSERT INTO {} " + self.ip_table_query).format(sql.Identifier(self.ip_address_table_name))   
            
            cur.execute(query, new_ip_data)
        
            self.conn.commit()
    
    def writeMAC(self, new_mac_data):
        if self._checkConnection():
            cur = self.conn.cursor()
            
            query = sql.SQL("INSERT INTO {} " + self.mac_table_query).format(sql.Identifier(self.mac_address_table_name))   
            
            cur.execute(query, new_mac_data)
        
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
    

    def writeDataTable(self):
        if self._checkConnection():
            args = "(Key INT PRIMARY KEY, Timestamp INT, SourceMAC VARCHAR(20), DestinationMAC VARCHAR(20), TotalBits INT, FlagPassive INT, Flag2GHz INT, FlagOFDM INT, FlagCCK INT, FlagGFSK INT, Flag5GHz INT, FlagGSM INT, FlagCCKOFDM INT, TotalPackets INT, SignalStrength INT, DataRate INT, Duration INT, DurationPreamble INT, PhysType VARCHAR(3))"
            query = sql.SQL("CREATE TABLE {} " + args).format(sql.Identifier(self.data_table_name))
            
            self.conn.cursor().execute(query)

            self.conn.commit()

    def getTableNames(self):
        if self._checkConnection():
            cur = self.conn.cursor()
    
            cur.execute("select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';")
            out = cur.fetchall()
            table_names = [x[0] for x in out]
            return table_names
        
    def convertTimetoEpoch(self, time):
        return 0