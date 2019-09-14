#Import libraries
from flask import Flask, render_template, request, jsonify, redirect
from flask_socketio import SocketIO
import json
from datetime import datetime
import random
import string
import fenixedu

#Import classes
from message_queue import message_queue
from DB import DB
from userDB import userDB
from buildingDB import buildingDB
from logDB import logDB
from botDB import botDB

#Flask object
app = Flask(__name__)
socketio = SocketIO(app)

#Initialize global objects
obj_DB = DB()
obj_userDB = userDB(obj_DB)
obj_buildingDB = buildingDB(obj_DB)
obj_logDB = logDB(obj_DB)
obj_botDB = botDB(obj_DB)

#Init RabbitMQ object
obj_mq = message_queue()

#Session lists
session_dict = {}
session_dict_bot = {}
session_tokens = {}

def check_token(u_id, token):
    global session_dict, session_tokens
    for item in session_dict.items():
        if item[1] == u_id:
            if token == session_tokens[item[0]]:
                return True
    return False

def MQ_IDs(u_id):
    global session_dict
    IDs = []
    for item in session_dict.items():
        if item[1] == u_id:
            IDs.append(item[0])
    return IDs

# ----------------------- SocketIO ----------------------------
@socketio.on('new_client')
def connect(data):
    obj_mq.declare_queue(request.sid)
    session_dict[request.sid] = data["id"] 
    session_tokens[request.sid] = data["token"] 
    counter = obj_userDB.update_counter(data["id"], 1)
    if (counter == 1):
        obj_userDB.update_status(data["id"], 1)
    socketio.emit("new_movement")
    b_id = obj_userDB.get_building(data["id"])
    if b_id is None:
        msg = "Logged in. Currently out of IST registered facilities"
    else:
        msg = "Logged in. Currently in " + obj_buildingDB.get_building_name(b_id)    
    obj_logDB.add_user_log(msg, data["id"], datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
  
@socketio.on('new_bot')
def connect_bot(data):    
    session_dict_bot[request.sid] = data["id"]
    obj_botDB.change_status(data["id"], 1)

@socketio.on('disconnect')
def disconnect():
    if (request.sid in session_dict):
        counter = obj_userDB.update_counter(session_dict[request.sid], 0)
        if (counter == 0):
            obj_userDB.update_status(session_dict[request.sid], 0)
        socketio.emit("new_movement")
        obj_logDB.add_user_log("Logged out.", session_dict[request.sid], datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        del session_dict[request.sid]
        del session_tokens[request.sid]
        obj_mq.delete_queue(request.sid)
    elif (request.sid in session_dict_bot):
        obj_botDB.change_status(session_dict_bot[request.sid], 0)
        del session_dict_bot[request.sid]

# ----------------------- user web app ----------------------------

@app.route('/')
def login():
    config = fenixedu.FenixEduConfiguration.fromConfigFile('setup.ini')
    client = fenixedu.FenixEduClient(config)
    url = client.get_authentication_url()
    return redirect(url)

@app.route('/login', methods=['GET', 'POST'])
def index():
    config = fenixedu.FenixEduConfiguration.fromConfigFile('setup.ini')
    client = fenixedu.FenixEduClient(config)
    code = request.args["code"]
    user = client.get_user_by_code(code)
    person = client.get_person(user)
    username = person['username']
    token = user.access_token
    radious = obj_userDB.update_user(username)
    return render_template("mainPage.html", user_id = username, token = token, radious = radious)

@app.route('/API/user/update/coordinates', methods=['POST'])
def update_coordinates():
    json_data = json.loads(request.data.decode('utf-8'))
    if (check_token(json_data["id"], json_data["token"])):
        building = obj_buildingDB.get_building_in_range(json_data["latitude"],json_data["longitude"])
        if building is None:
            current_building_name = "Out of IST registered facilities"
            current_building_id = None
        else:
            current_building_name = building["name"]
            current_building_id = building["id"]
        
        #Check if changed location
        if (obj_userDB.get_status(json_data["id"])):
            b_id = obj_userDB.get_building(json_data["id"])
            if (b_id != current_building_id):
                socketio.emit("new_movement")
                if (b_id is None):
                    msg = "Moved from: Out of IST registered facilities to: " + current_building_name
                else:
                    msg = "Moved from: " + obj_buildingDB.get_building_name(b_id) + " to: " + current_building_name
                obj_logDB.add_user_log(msg, json_data["id"], datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        #Update coordinates
        if building is None:
            obj_userDB.update_coordinates(json_data["id"], json_data["latitude"], json_data["longitude"])
        else:
            obj_userDB.update_coordinates(json_data["id"], json_data["latitude"], json_data["longitude"], building["id"])
        
        return current_building_name
    else:
        return ""
        
@app.route('/API/user/update/range', methods=['POST'])
def update_range():
    json_data = json.loads(request.data.decode('utf-8'))
    if (check_token(json_data["id"], json_data["token"])):
        obj_userDB.update_radious(json_data["id"], json_data["radious"])
    return ""

@app.route('/API/user/show/building', methods=['POST'])
def show_users_same_building():
    json_data = json.loads(request.data.decode('utf-8'))
    if (check_token(json_data["id"], json_data["token"])):
        return jsonify(obj_userDB.get_users_in_building(json_data["id"])) 
    else:
        return jsonify([])

@app.route('/API/user/show/range', methods=['POST'])
def show_users_in_range(): 
    json_data = json.loads(request.data.decode('utf-8'))
    if (check_token(json_data["id"], json_data["token"])):
        return jsonify(obj_userDB.get_users_in_range(json_data["id"], json_data["latitude"], json_data["longitude"], json_data["radious"]))
    else:
        return jsonify([])

@app.route('/API/user/message/send', methods=['POST'])
def user_send_message(): 
    json_data = json.loads(request.data.decode('utf-8'))
    if (check_token(json_data["id"], json_data["token"])):
        json_queue = {}
        json_queue["timestamp"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        json_queue["id"] = json_data["id"]
        json_queue["message"] = json_data["message"]
        users = json_data["users"].split("\n")
        del users[-1]
    for i in range(len(users)):
        MQ_array = MQ_IDs(users[i])
        for j in range(len(MQ_array)):
            obj_mq.send_message(MQ_array[j], json.dumps(json_queue))
    obj_logDB.add_user_log(json_data["message"], json_data["id"], json_queue["timestamp"])
    socketio.emit("new_message", users)
    return ""

@app.route('/API/user/message/receive', methods=['POST'])
def user_receive_message(): 
    json_data = json.loads(request.data.decode('utf-8'))
    if (check_token(json_data["id"], json_data["token"])):
        message_array = []
        for i in range(obj_mq.get_num_messages(json_data["socket_id"])):
            result = obj_mq.receive_message(json_data["socket_id"])
            message_array.append(result[2].decode('utf-8'))
        return jsonify(message_array)
    else:
        return jsonify([])
    
# ----------------------- bot REST ----------------------------
@app.route('/API/bot/check/<boot_id>', methods=['GET'])
def check_bot_availability(boot_id):
    return jsonify(obj_botDB.check_bot_availability(boot_id))

@app.route('/API/bot/show/buildings', methods=['GET'])
def show_buildings_for_bot():
    return jsonify(obj_buildingDB.show_all_buildings())

@app.route('/API/bot/register', methods=['POST'])
def register_bot():
    json_data = json.loads(request.data.decode('utf-8'))
    passw = ''.join(random.sample(string.ascii_lowercase,6))
    obj_botDB.add_bot(json_data["id"], json_data["b_id"], passw)
    return jsonify({"pass" : passw})

@app.route('/API/bot/auth', methods=['POST'])
def authenticate_bot():
    json_data = json.loads(request.data.decode('utf-8'))
    if (json_data["pass"] == obj_botDB.get_pass(json_data["id"])):
        return jsonify({"auth" : 1})
    else:
        return jsonify({"auth" : 0})

@app.route('/API/bot/message', methods=['POST'])
def bot_send_message():
    json_data = json.loads(request.data.decode('utf-8'))
    check = obj_botDB.check_bot_availability(json_data["id"])
    if (not "auth" in check):
        b_id = obj_botDB.get_building(json_data["id"])
        users = obj_userDB.show_users_per_building(b_id)
        json_data["timestamp"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for i in range(len(users)):
            MQ_array = MQ_IDs(users[i]["id"])
            for j in range(len(MQ_array)):
                obj_mq.send_message(MQ_array[j], json.dumps(json_data)) 
        obj_logDB.add_bot_log(json_data["message"], json_data["id"], b_id, json_data["timestamp"])
        message_users = []
        for i in range(len(users)):
            message_users.append(users[i]["id"])
        socketio.emit("new_message", message_users)
    return jsonify(check)
    
# -------------------- admin REST ----------------------------    

@app.route('/API/admin/buildings/add', methods=['POST'])
def add_building():
    json_data = json.loads(request.data.decode('utf-8'))
    obj_buildingDB.add_building(json_data["id"],json_data["name"],json_data["latitude"],json_data["longitude"],json_data["radious"])
    return jsonify([])

@app.route('/API/admin/users/show', methods=['GET'])
def show_all_users():
    return jsonify(obj_userDB.show_all_users())

@app.route('/API/admin/users/show/online', methods=['GET'])
def show_users_online():
    return jsonify(obj_userDB.show_users_online())

@app.route('/API/admin/buildings/show', methods=['GET'])
def show_all_buildings():
    return jsonify(obj_buildingDB.show_all_buildings())

@app.route('/API/admin/users/show/building/<b_id>', methods=['GET'])
def show_users_per_building(b_id):
    return jsonify(obj_userDB.show_users_per_building(b_id))

@app.route('/API/admin/logs/show/user/<u_id>', methods=['GET'])
def show_logs_per_user(u_id):
    return jsonify(obj_logDB.show_logs_per_user(u_id))

@app.route('/API/admin/logs/show/building/<b_id>', methods=['GET'])
def show_logs_per_building(b_id):
    return jsonify(obj_logDB.show_logs_per_building(b_id))

@app.route('/API/admin/bots/update/auth', methods=['POST'])
def update_bot():
    json_data = json.loads(request.data.decode('utf-8'))
    obj_botDB.change_authorization(json_data["id"], json_data["state"])
    return jsonify([])

@app.route('/API/admin/bots/show/auth/<state>', methods=['GET'])
def show_all_bots(state):
    return jsonify(obj_botDB.show_all_bots(int(state)))

#Run flask server
if __name__ == '__main__':
    socketio.run(app, debug = True, port = 80)