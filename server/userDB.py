from geopy.distance import distance

class userDB:
    
    def __init__(self, obj_DB):
        self.obj_DB = obj_DB
    
    def check_user(self, u_id):
        query = "SELECT id FROM user where id = '%s'" % (u_id)
        resp = self.obj_DB.read_operation(query)
        if (resp["success"]):
            return len(resp["data"]) > 0
        else:
            return False
    
    def update_user(self, u_id):
        if (self.check_user(u_id)):
            radious = self.get_radious(u_id)
        else:
            self.add_user(u_id)
            radious = 50
            self.update_radious(u_id, radious)
        return radious

    def add_user(self, u_id):   
        query = "INSERT into user(id) value('%s')" %(u_id)
        self.obj_DB.write_operation(query)   
            
    def get_radious(self, u_id):
        query = "SELECT radious from user where id = '%s'" %(u_id)
        resp = self.obj_DB.read_operation(query)
        if (resp["success"]):
            return resp["data"][0]["radious"]
        else:
            return 50

    def update_status(self, u_id, status):
        query = "UPDATE user set online = %s where id = '%s'" %(status, u_id)
        self.obj_DB.write_operation(query)
        
    def update_radious(self, u_id, radious):
        query = "UPDATE user set radious = %s where id = '%s'" %(radious, u_id)
        self.obj_DB.write_operation(query)
        
    def update_coordinates(self, u_id, x, y, b_id = None):
        if b_id is None:
            query = "UPDATE user set latitude = %s, longitude = %s, b_id = null where id = '%s'" %(x, y, u_id)
        else:
            query = "UPDATE user set latitude = %s, longitude = %s, b_id = '%s' where id = '%s'" %(x, y, b_id, u_id)
        self.obj_DB.write_operation(query)
        
    def get_building(self, u_id):
        query = "SELECT b_id from user where id = '%s'" %(u_id);
        resp = self.obj_DB.read_operation(query)
        if (resp["success"]):
            return resp["data"][0]["b_id"]
        else:
            return ""
    
    def get_users_in_building(self, u_id):
        building = self.get_building(u_id)
        if building is None:
            return []
        return self.show_users_per_building(building, u_id)
    
    def show_users_per_building(self, b_id, u_id = None):
        if (u_id is None):
            query = "SELECT id from user where b_id = '%s' and online = 1" %(b_id);
        else:
            query = "SELECT id from user where b_id = '%s' and online = 1 and id != '%s'" %(b_id, u_id);
        resp = self.obj_DB.read_operation(query)
        if (resp["success"]):
            return resp["data"]
        else:
            return []

    def get_users_in_range(self, u_id, latitude, longitude, radious):
        users = self.show_users_online()
        users_nearby = []
        for i in range(len(users)):
            coord_building = (users[i]["latitude"], users[i]["longitude"])
            coord_user = (latitude, longitude)
            dist = distance(coord_user, coord_building).m
            if (dist <= radious):
                users_nearby.append(users[i]["id"])
        if u_id in users_nearby:
            users_nearby.remove(u_id)
        return users_nearby
   
    def show_users_online(self): 
        query = "SELECT * from user where online = 1";
        resp = self.obj_DB.read_operation(query)
        if (resp["success"]):
            return resp["data"]
        else:
            return []
        
    def show_all_users(self): 
        query = "SELECT id from user";
        resp = self.obj_DB.read_operation(query)
        if (resp["success"]):
            return resp["data"]
        else:
            return []
        
    def get_counter(self, u_id):
        query = "SELECT counter from user where id = '%s'" %(u_id)
        resp = self.obj_DB.read_operation(query)
        if (resp["success"]):
            return resp["data"][0]["counter"]
        else:
            return 0
        
    def update_counter(self, u_id, flag):
        if flag:
            counter = self.get_counter(u_id) + 1
        else:
            counter = self.get_counter(u_id) - 1
        query = "UPDATE user set counter = %s where id = '%s'" %(counter, u_id)
        self.obj_DB.write_operation(query)
        return counter
    
    def get_status(self, u_id):
        query = "SELECT online from user where id = '%s'" %(u_id)
        resp = self.obj_DB.read_operation(query)
        if (resp["success"]):
            return resp["data"][0]["online"]
        else:
            return 0