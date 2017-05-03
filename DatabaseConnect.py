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
        if self._checkConnection():
            cur = self.conn.cursor()
            #query = sql.SQL("SELECT * FROM {} WHERE key = (SELECT key FROM {} WHERE key = {})").format(sql.Identifier(self.data_table_name), sql.Identifier(self.data_table_name), sql.Identifier(str(ip_address_key)))
            
            query = sql.SQL("SELECT macaddress FROM {} WHERE key =  %(name)s").format(sql.Identifier(self.mac_address_table_name), sql.Identifier(str(mac_address_key)))
            
            cur.execute(query, {"name" : str(mac_address_key)})
            address = cur.fetchone()
            if address is not None:
                return address[0]
            else:
                #add to database
                print("doesn't exist")
            
        
    def getMACAddressKey(self, mac_address):
        if self._checkConnection():
            cur = self.conn.cursor()
            #query = sql.SQL("SELECT * FROM {} WHERE key = (SELECT key FROM {} WHERE key = {})").format(sql.Identifier(self.data_table_name), sql.Identifier(self.data_table_name), sql.Identifier(str(ip_address_key)))
            
            query = sql.SQL("SELECT key FROM {} WHERE macaddress =  %(name)s").format(sql.Identifier(self.mac_address_table_name), sql.Identifier(mac_address))
            
            cur.execute(query, {"name" : str(mac_address)})
            key = cur.fetchone()
            if key is not None:
                return key[0]
            
        
    def getIPAddress(self, ip_address_key):
        if self._checkConnection():
            cur = self.conn.cursor()
            #query = sql.SQL("SELECT * FROM {} WHERE key = (SELECT key FROM {} WHERE key = {})").format(sql.Identifier(self.data_table_name), sql.Identifier(self.data_table_name), sql.Identifier(str(ip_address_key)))
            
            query = sql.SQL("SELECT ipaddress FROM {} WHERE key =  %(name)s").format(sql.Identifier(self.ip_address_table_name), sql.Identifier(str(ip_address_key)))
            
            cur.execute(query, {"name" : str(ip_address_key)})
            address = cur.fetchone()
            if address is not None:
                return address[0]
            else:
                #add to database
                print("Entry doesn't exist.")
                
        
    def getIPAddressKey(self, ip_address):
        if self._checkConnection():
            cur = self.conn.cursor()
            #query = sql.SQL("SELECT * FROM {} WHERE key = (SELECT key FROM {} WHERE key = {})").format(sql.Identifier(self.data_table_name), sql.Identifier(self.data_table_name), sql.Identifier(str(ip_address_key)))
            
            query = sql.SQL("SELECT key FROM {} WHERE ipaddress =  %(name)s").format(sql.Identifier(self.ip_address_table_name), sql.Identifier(ip_address))
            
            cur.execute(query, {"name" : str(ip_address)})
            key = cur.fetchone()
            if key is not None:
                return key[0]
            else:
                self.writeIPData((self.getNextIPKey()+1, ip_address))
                cur.execute(query, {"name" : str(ip_address)})
                return cur.fetchone()[0]

    
    def getNextKey(self, table_name):
        if self._checkConnection():
            cur = self.conn.cursor()
            query = sql.SQL("SELECT MAX(Key) from {}").format(sql.Identifier(table_name))
            cur.execute(query)
            latest_key = cur.fetchall()
            res_list = [x[0] for x in latest_key]
            return res_list[0]

    def getNextMACKey(self):
        a = self.getNextKey(self.mac_address_table_name)
        return a + 1
        
    def getNextIPKey(self):
        a = self.getNextKey(self.ip_address_table_name)
        return a + 1 
        
    def getNextDataKey(self):
        a = self.getNextKey(self.data_table_name)
        return a + 1
        
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
    
    def _writeData(self, table_name, query, new_data):
        print(query)
        print(table_name)
        print(new_data)
        
        if self._checkConnection():
            cur = self.conn.cursor()
            
            query = sql.SQL("INSERT INTO {} " + query).format(sql.Identifier(table_name))   
            
            # need to discriminate single and multiple data
            cur.execute(query, new_data)
        
            self.conn.commit()
    
    def writeData(self, new_table_data):
        self._writeData(self.data_table_name, self.data_table_query, new_table_data)
            
    def writeIPData(self, new_ip_data):
        self._writeData(self.ip_address_table_name, self.ip_table_query, new_ip_data)
    
    def writeMACData(self, new_mac_data):
        self._writeData(self.mac_address_table_name, self.data_mac_query, new_mac_data)
        
    def _deleteData(self, key, table_name):
        if self._checkConnection():
            cur = self.conn.cursor()
            query = sql.SQL("delete from {} where Key={}").format(sql.Identifier(table_name), sql.Identifier(key))
            cur.execute(query)
    def deleteIPData(self, key):
        self._deleteData(self.ip_address_table_name, key)
        
    def deleteMACData(self, key):  
        self._deleteData(self.mac_address_table_name, key) 
        
    def deleteData(self, key):  
        self._deleteData(self.data_table_name, key) 
                                        
    
               
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