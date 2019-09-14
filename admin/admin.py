from adminUI import adminUI
import requests
import json
import getpass

filename = "params.json"

def login(u, p):
    username = input('Username: ')
    password = getpass.getpass('Password: ')
    return (username == u and password == p)

class proxyRest:
    
    def __init__(self, host):
        self.host = host
        
    def make_request(self, path, data = None):
        try:
            if (data is None):
                r = requests.get(self.host + path)
            else:
                r = requests.post(self.host + path, data = data)
            if (r.status_code == 200):
                return {"success": True, "resp" : r.json()}
            else:
                return {"success": False, "error" : "Error HTTP " + str(r.status_code)}
        except Exception as e:
            return {"success": False, "error" : e}
            
    def add_building(self, b_id, name, x, y, radious):
        json_data = json.dumps({"id": b_id, "name": name, "latitude": x, "longitude" : y, "radious": radious}, ensure_ascii=False)
        return self.make_request("/API/admin/buildings/add", json_data.encode('utf-8'))
        
    def show_all_buildings(self):
        return self.make_request("/API/admin/buildings/show")
    
    def show_all_users(self):
        return self.make_request("/API/admin/users/show")
    
    def show_users_online(self):
        return self.make_request("/API/admin/users/show/online")
        
    def show_users_per_building(self, building_id):
        return self.make_request("/API/admin/users/show/building/" + str(building_id))
        
    def show_logs_per_user(self, user_id):
        return self.make_request("/API/admin/logs/show/user/" + str(user_id))
        
    def show_logs_per_building(self, building_id):
        return self.make_request("/API/admin/logs/show/building/" + str(building_id))
        
    def update_bot_state(self, boot_id, state):
        json_data = json.dumps({"id": boot_id, "state": state}, ensure_ascii=False)
        return self.make_request("/API/admin/bots/update/auth", json_data.encode('utf-8'))
    
    def show_all_bots(self, auth):
        return self.make_request("/API/admin/bots/show/auth/" + str(auth))
        
def main(params):
    if(login(params["user"], params["password"])):
        obj = proxyRest(params["host"])
        ui = adminUI(obj)
        ui.menu()
    else:
        if (input("Wrong username or password. Type 'y' to try again: ") == "y"):
            main(params)

if __name__=="__main__":
    params = json.load(open(filename, encoding='utf-8'))
    main(params)