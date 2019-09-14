#Import libraries
import argparse
from socketIO_client import SocketIO
from threading import Thread
import json
import time
import requests
import warnings
import os
import getpass

#Ignore warnings
warnings.filterwarnings("ignore")

#Upload server info
filename = "url.json"
json_data = json.load(open(filename, encoding='utf-8')) 
host = json_data["schema"] + json_data["host"]
flag = True

def make_request(path, data = None):
    try:
        if (data is None):
            r = requests.get(host + path)
        else:
            r = requests.post(host + path, data = data)
        if (r.status_code == 200):
            return {"success": True, "resp" : r.json()}
        else:
            return {"success": False, "error" : "Error HTTP " + str(r.status_code)}
    except Exception as e:
        return {"success": False, "error" : e}

def user_input():
    input("Enter to stop bot")
    global flag
    flag = False

def receive_events():
    socketio.wait()
    
def send_message():
    json_data = json.dumps({"id": options.bot, "message": options.message}, ensure_ascii=False)
    resp = make_request("/API/bot/message", json_data)
    if (resp["success"] and "auth" in resp["resp"]):
        print("\nBot has been disallowed")
        global flag
        flag = False
    else:
        print("Message sent")
        if (options.interval):
            time.sleep(int(options.interval))
            send_message()
        
def buildings_menu(data):
    print("\n---------- Choose building --------------")
    for i in range(len(data)):
        print(str(i+1) + ") " + data[i]["name"])
    print(str(len(data)+1) + ") Return")
    print("-----------------------------------")
    try:
        option = int(input("Select an option: "))
    except Exception:
        option = len(data) + 2
    os.system('cls')
    if (option in range(1, len(data)+1)):
        return data[option-1]["id"]
    elif (option == len(data)+1):
        return None
    else:
        os.system('cls')
        print("Wrong option. Try again")
        return buildings_menu(data)

#Setup command line options
parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group(required=True)
parser.add_argument("-b", "--bot", dest="bot", help="Bot ID", required=True)
group.add_argument("-s", "--status", dest = "status", help="Bot status", action='store_true')
group.add_argument("-m", "--message", dest = "message", help="Bot message", nargs='+')
group.add_argument("-r", "--register", dest = "register", help="Register bot", action='store_true')
parser.add_argument("-i", "--interval", type = int, dest = "interval", help="Bot interval (in seconds)")
options = parser.parse_args()

#Check if user wants to check bot status
if options.status:
    resp = make_request("/API/bot/check/" + options.bot)
    if(resp["success"]):
        print(resp["resp"]["state"])
    else:
        print(resp["error"])
        
#Check if user wants to register bot
elif options.register:
    status = make_request("/API/bot/check/" + options.bot)
    if(status["success"]):
        if ("new" in status["resp"]):
            buildings = make_request("/API/bot/show/buildings")
            if (buildings["success"]):
                b_id = buildings_menu(buildings["resp"])
                if b_id is not None:
                    json_data = json.dumps({"id": options.bot, "b_id": b_id}, ensure_ascii=False)
                    resp = make_request("/API/bot/register", json_data)
                    if (resp["success"]):
                        print("Bot successfully registered. Wait for admin authorization...")
                        print("Password assigned is: " + resp["resp"]["pass"])
                    else:
                        print(resp["error"])
            else:
                print(buildings["error"])
        else:
            print("Bot already exists")
    else:
        print(status["error"])

#Check if user wants to run bot
elif options.message:
    options.message = ' '.join(options.message)
    state = make_request("/API/bot/check/" + options.bot)
    if (state["success"] and state["resp"]["available"]):
        password = getpass.getpass('Password: ')
        resp = make_request("/API/bot/auth", json.dumps({"id": options.bot, "pass": password}, ensure_ascii=False))
        if (resp["success"] and resp["resp"]["auth"]):
            if (options.interval):
                socketio = SocketIO(json_data["schema"] + json_data["host"])#, verify=False)#, json_data["port"])
                socketio.emit('new_bot', {"id": options.bot})
                
                socketio_thread = Thread(target=receive_events)
                socketio_thread.daemon = True
                socketio_thread.start()
                
                message_thread = Thread(target=send_message)
                message_thread.daemon = True
                message_thread.start()
                
                input_thread = Thread(target=user_input)
                input_thread.daemon = True
                input_thread.start()
                
                while(flag):
                    continue
                
            else:
                send_message()
        else:
            print("Wrong password!")
    else:
        print(state["resp"]["state"])