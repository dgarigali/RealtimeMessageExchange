from geopy.distance import distance

class buildingDB:
    
    def __init__(self, obj_DB):
        self.obj_DB = obj_DB
        
    def check_building(self, b_id):
        query = "SELECT id FROM building where id = '%s'" % (b_id)
        resp = self.obj_DB.read_operation(query)
        if (resp["success"]):
            return len(resp["data"]) > 0
        else:
            return False
        
    def add_building(self, b_id, name, x, y, radious):
        if (self.check_building(b_id)):
            query = "UPDATE building set name = '%s', latitude = %s, longitude = %s, radious = %s where id = '%s'" %(name, x, y, radious, b_id)          
        else:
            query = "INSERT into building value('%s','%s', %s, %s, %s)" %(b_id, name, x, y, radious)
        self.obj_DB.write_operation(query) 
            
    def get_building_in_range(self, latitude, longitude):
        resp = self.obj_DB.read_operation("SELECT * from building")
        if (resp["success"]):
            buildings = resp["data"]
        else:
            buildings = []
        nearby_buildings = []
        for i in range(len(buildings)):
            coord_building = (buildings[i]["latitude"], buildings[i]["longitude"])
            coord_user = (latitude, longitude)
            dist = distance(coord_user, coord_building).m
            if (dist <= buildings[i]["radious"]):
                nearby_buildings.append([dist, i])
        nearby_buildings = sorted(nearby_buildings) 
        if (len(nearby_buildings) == 0) :
            return None
        else :
            return buildings[nearby_buildings[0][1]]
    
    def get_building_name(self, b_id):
        query = "SELECT name from building where id = '%s'" %(b_id)
        resp = self.obj_DB.read_operation(query)
        if (resp["success"]):
            return resp["data"][0]["name"] 
        else:
            return ""
    
    def show_all_buildings(self):
        query = "SELECT name, id from building";
        resp = self.obj_DB.read_operation(query)
        if (resp["success"]):
            return resp["data"]
        else:
            return []