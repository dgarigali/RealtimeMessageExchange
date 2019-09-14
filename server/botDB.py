class botDB:
    
    def __init__(self, obj_DB):
        self.obj_DB = obj_DB
        
    def add_bot(self, bot_id, b_id, passw):
        query = "INSERT into bot(id, b_id, authorized, online, pass) value('%s','%s', 0, 0, '%s')" %(bot_id, b_id, passw)
        self.obj_DB.write_operation(query)
        
    def change_authorization(self, bot_id, auth):
        query = "UPDATE bot set authorized = %s where id = '%s'" %(auth, bot_id)
        self.obj_DB.write_operation(query)
        
    def show_all_bots(self, auth):
        query = "SELECT id from bot where authorized = %s" %(auth)
        resp = self.obj_DB.read_operation(query)
        if (resp["success"]):
            return resp["data"]
        else:
            return []
        
    def check_bot_availability(self, boot_id):
        query = "SELECT online, authorized from bot where id = '%s'" %(boot_id) 
        resp = self.obj_DB.read_operation(query)
        if (resp["success"]):
            if (len(resp["data"]) == 0):
                return {"available" : 0, "state" : "Bot does not exist.", "new" : 1}
            elif (resp["data"][0]["authorized"] == 0):
                return {"available" : 0, "state" : "Bot has not been authorized yet.", "auth": 0}
            elif (resp["data"][0]["online"] == 1):
                return {"available" : 0, "state" : "Bot currently running."}
            else:
                return {"available" : 1, "state" : "Bot available."}
        else:
            return {"available" : 0, "state" : "Problem reading database"}
        
    def change_status(self, bot_id, status):
        query = "UPDATE bot set online = %s where id = '%s'" %(status, bot_id)
        self.obj_DB.write_operation(query)
        
    def get_building(self, bot_id):
        query = "SELECT b_id from bot where id = '%s'" %(bot_id)
        resp = self.obj_DB.read_operation(query)
        if (resp["success"]):
            return resp["data"][0]["b_id"]
        else:
            return ""
        
    def get_pass(self, bot_id):
        query = "SELECT pass from bot where id = '%s'" %(bot_id)
        resp = self.obj_DB.read_operation(query)
        if (resp["success"]):
            return resp["data"][0]["pass"] 
        else:
            return ""