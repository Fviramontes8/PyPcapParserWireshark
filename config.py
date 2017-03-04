'''
author: Seth Decker (Editted from http://www.postgresqltutorial.com/postgresql-python/connect/)

Description: This code parses a configuration file used to connect to a postgreSQL database

I/O:
    filename: name of the configuration file
    section: section in the config file

    db: the database
'''


from configparser import ConfigParser
import os

def config(filename='database.ini', section='postgresql'):
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
            raise Exception('Section {0} not found in the {1} file'.format(section, filename))

        return db
    else:
        print("Configuration file does not exist")
        return None