'''
author: Seth Decker (Editted from http://www.postgresqltutorial.com/postgresql-python/connect/)

Description: This code checks to see that you are able to connect to the postgreSQL database.

I/O:
    None

Example:
    #>>> verify()
         Connecting to the PostgreSQL database...
         PostgreSQL database version:
         ('PostgreSQL 9.6.2, compiled by Visual C++ build 1800, 64-bit',)
         Database connection closed.

'''


#import modules
import psycopg2
from config import config
# from config import config

def verify():
    # verify connection to postgrSQL database
    conn = None
    try:
        # read connection parameters
        params = config()

        if params is None:
            return

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)

        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')