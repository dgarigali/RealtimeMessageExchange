class logDB:
    
    def __init__(self, obj_DB):
        self.obj_DB = obj_DB
        
    def add_user_log(self, message, u_id, timestamp):
        query = "INSERT into log(message, u_id, timestamp) value('%s','%s', '%s')" %(message, u_id, timestamp)
        self.obj_DB.write_operation(query)   
        
    def add_bot_log(self, message, bot_id, b_id, timestamp):
        query = "INSERT into log(message, bot_id, b_id, timestamp) value('%s','%s', '%s', '%s')" %(message, bot_id, b_id, timestamp)
        self.obj_DB.write_operation(query)  
        
    def show_logs_per_user(self, u_id):
        query = "SELECT timestamp, message from log where u_id = '%s' order by timestamp desc limit 10" %(u_id);
        resp = self.obj_DB.read_operation(query)
        if (resp["success"]):
            return resp["data"]
        else:
            return []
    
    def show_logs_per_building(self, b_id):
        query = "SELECT bot_id, timestamp, message from log where b_id = '%s' order by timestamp desc limit 10" %(b_id);
        resp = self.obj_DB.read_operation(query)
        if (resp["success"]):
            return resp["data"]
        else:
            return []