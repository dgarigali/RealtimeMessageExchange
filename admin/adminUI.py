import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import json

class adminUI:
    
    def __init__(self, db):
        self.db = db
        os.system('cls')

    def show_menu(self):
        print("\n---------- Menu--------------")
        print("1) Add buildings from file")
        print("2) Show users online")
        print("3) Show users per building")
        print("4) Show logs per user");
        print("5) Show logs per building");
        print("6) Authorize bot");
        print("7) Disallow bot");
        print("8) Exit")
        print("----------------------------")

    def menu(self):
        while(True):
            self.show_menu()
            try:
                option = int(input("Select an option: "))
            except Exception:
                option = 9
            os.system('cls')
            if option == 1:
                print(self.routine_add_buildings())
            elif option == 2:
                self.routine_list_users_online()
            elif option == 3:
                self.routine_list_users_per_building()
            elif option == 4:
                self.routine_list_logs_per_user()
            elif option == 5:
                self.routine_list_logs_per_building()
            elif option == 6:
                self.routine_bot_auth(0, "Bot authorized!")
            elif option == 7:
                self.routine_bot_auth(1, "Bot disallowed!")
            elif option == 8:
                break
            else:
                print("Wrong option. Try again")	

    def routine_add_buildings(self):
        Tk().withdraw() #hide GUI
        filename = askopenfilename(initialdir = "./", filetypes = [("json files","*.json")])
        if (os.path.isfile(filename)):
            buildings_json = json.load(open(filename, encoding='utf-8'))
            if "containedSpaces" in buildings_json:
                for row in buildings_json["containedSpaces"]:
                    if ("id" in row and "name" in row and "latitude" in row and "longitude" in row):
                        resp = self.db.add_building(row["id"], row["name"], row["latitude"], row["longitude"], row["range"])
                        if (not resp["success"]):
                            return resp["error"]
                return "Buildings added!"
            else:
                return "Wrong file configuration"
        else:
            return "Invalid file!"
        
    def print_users(self, users, msg):
        if (users["success"]):
            if (len(users["resp"]) == 0):
                print(msg)
            else:
                for i in range(len(users["resp"])):
                    print(users["resp"][i]["id"])
        else:
            print(users["error"])        
                        
    def routine_list_users_online(self):
        users = self.db.show_users_online()
        self.print_users(users, "No users online!")
        
    def routine_list_users_per_building(self):
        buildings = self.db.show_all_buildings()
        if (buildings["success"]): 
            res = self.sub_menu(buildings["resp"], "name", "id")
            if res is not None:
                users = self.db.show_users_per_building(res)
                self.print_users(users, "No users in selected building!")
        else:
            print(buildings["error"])
            
    def print_logs(self, logs, msg, flag):
        if (logs["success"]):
            if (len(logs["resp"]) == 0):
                print(msg)
            else:
                for i in range(len(logs["resp"])):
                    if (flag):
                        print(str(logs["resp"][i]["timestamp"]) + " -> " + logs["resp"][i]["message"])
                    else:
                        print(str(logs["resp"][i]["timestamp"]) + " -> [" + logs["resp"][i]["bot_id"] + "]: " + logs["resp"][i]["message"])
        else:
            print(logs["error"])

    def routine_list_logs_per_user(self):
        users = self.db.show_all_users()
        if (users["success"]): 
            res = self.sub_menu(users["resp"], "id", "id")
            if res is not None:
                logs = self.db.show_logs_per_user(res)
                self.print_logs(logs, "No logs for selected user!", 1)
        else:
            print(users["error"])

    def routine_list_logs_per_building(self):
        buildings = self.db.show_all_buildings()
        if (buildings["success"]):
            res = self.sub_menu(buildings["resp"], "name", "id")
            if res is not None:
                logs = self.db.show_logs_per_building(res)
                self.print_logs(logs, "No logs for selected building!", 0)
        else:
            print(buildings["error"])
            
    def sub_menu(self, data, field_name, field_id):
        print("\n---------- Sub-Menu--------------")
        for i in range(len(data)):
            print(str(i+1) + ") " + data[i][field_name])
        print(str(len(data)+1) + ") Return")
        print("-----------------------------------")
        try:
            option = int(input("Select an option: "))
        except Exception:
            option = len(data) + 2
        os.system('cls')
        if (option in range(1, len(data)+1)):
            return data[option-1][field_id]
        elif (option == len(data)+1):
            return None
        else:
            os.system('cls')
            print("Wrong option. Try again")
            return self.sub_menu(data, field_name, field_id)
            
    def routine_bot_auth(self, flag, msg):
        bots = self.db.show_all_bots(flag)
        if (bots["success"]): 
            bot_id = self.sub_menu(bots["resp"], "id", "id")
            if bot_id is not None:
                res = self.db.update_bot_state(bot_id, not flag)
                if(res["success"]):
                    print(msg)
                else:
                    print(res["error"])
        else:
            print(bots["error"])  