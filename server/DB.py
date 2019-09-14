import sqlalchemy
from collections import OrderedDict
import logging
import json

filename = "credentials.json"

class DB:
    
    #Inits connection to mysql server
    def __init__(self):
        
        #Database credentials
        db = json.load(open(filename, encoding='utf-8'))["mysql"]
        db_user = db["user"]
        db_password = db["password"]
        db_name = db["name"]
        host = db["host"]
        
        #Prepare engine
        engine_url = 'mysql+pymysql://{}:{}@{}/{}'.format(db_user, db_password, host, db_name)
        self.engine = sqlalchemy.create_engine(engine_url, connect_args={'connect_timeout': 30})
        
    #Returns all rows from a cursor as a list of dicts
    def dictFetchAll(self, cursor):
        desc = cursor._cursor_description()
        return [OrderedDict(zip([col[0] for col in desc], row)) 
                for row in cursor.fetchall()]
        
    #Database read operation
    def read_operation(self, query): 
        try:
            cnx = self.engine.connect()
            cursor = cnx.execute(query)
            data = {"success": True, "data": self.dictFetchAll(cursor)}
        except Exception as error:
            data = {"success": False}
            logging.error(error)
        finally:
            if 'cnx' in locals():
                cnx.close()
            return data
        
    #Database write operation
    def write_operation(self, query): 
        try:
            cnx = self.engine.connect()
            cursor = cnx.execute(query)
            data = {"success": True}
        except Exception as error:
            data = {"success": False}
            logging.error(error)
        finally:
            if 'cnx' in locals():
                cnx.close()
            return data