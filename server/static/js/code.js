//Global variables
var coord_timer;
const coord_timer_time = 30000; //30 seconds
var latitude;
var longitude;
var flag = false;
var messages_array = [];
const message_array_size = 10;
var user_id;
var token;  
var socket_id;
  
$(document).ready(function() { 
	getLocation();
	document.getElementById('message').value = "";
	user_id = document.getElementById('user_id').value;
	token = document.getElementById('token').value;
});

function socketio_client() {
    
    //Connect to socketIO server
    var scheme = window.location.protocol == "https:" ? 'wss://' : 'ws://';
    var webSocketUri =  scheme + window.location.hostname + (location.port ? ':'+location.port: '');
    var socket = io.connect(webSocketUri, {transports: ['websocket']});
    
    //Connection event
	socket.on('connect', function() {
		socket.emit('new_client', {id: user_id, token: token});
		socket_id = socket.io.engine.id;
		update_coordinates();
	});
	
	//New message event
	socket.on('new_message', function(data) {
		for (i = 0; i < data.length; i++) {
			if( data[i] == user_id) {
    			receive_message();
    			break;
    		}
    	}
    });
    
    //New connection 
    socket.on('new_movement', function() {
        check_users_range();
        check_users_building();
    });  
}

function set_coord_timer(time) {
	return setInterval(function(){
		getLocation();
	},time);
}
 
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition);
    } else { 
        alert("Geolocation is not supported by this browser.");
		window.clearInterval(timer);
		flag = true;
    }
}

function showPosition(position) {
	latitude = position.coords.latitude;
    document.getElementById('latitude').value = latitude;
	longitude = position.coords.longitude;
	document.getElementById('longitude').value = longitude;
	update_coordinates();
	if (!flag) {
		flag = true;
		socketio_client(); 
		coord_timer = set_coord_timer(coord_timer_time);
	}
}

function change_manual_state() {
	if (document.getElementById('manual_checkbox').checked) {
		window.clearInterval(coord_timer);
		document.getElementById("latitude").disabled = false;
		document.getElementById("longitude").disabled = false;
		document.getElementById("send_coordinates").disabled = false;
	} else {
		coord_timer = set_coord_timer(coord_timer_time);
		document.getElementById("latitude").disabled = true;
		document.getElementById("longitude").disabled = true;
		document.getElementById("send_coordinates").disabled = true;
		getLocation();
	}
}

function update_coordinates() {
	latitude = document.getElementById('latitude').value;
	longitude = document.getElementById('longitude').value;
	if (!latitude || latitude.length === 0 || !longitude || longitude.length === 0) {
    	alert("Cannot send empty coordinates");
	} else {
    	$.ajax({
    		url: "/API/user/update/coordinates",
    		type: "POST",
    		contentType: "application/json",
    		data: JSON.stringify({	'id': user_id, 
        								'latitude': latitude,
        								'longitude': longitude,
        								'token' : token 
    								}),
    		success: function(result) {
    			document.getElementById('building').innerHTML = result;
    			check_users_range(); 
    		}
    	})
    }
}

function update_range() {
	$.ajax({
		url: "/API/user/update/range",
		type: "POST",
		contentType: "application/json",
		data: JSON.stringify({	'id': user_id,
                        		'token' : token,
    								'radious': parseInt(document.getElementById('range').value)
								}),
		success: function() {
			check_users_range(); 
		}
	})
}

function check_users_building() {
	$.ajax({
		url: "/API/user/show/building",
		type: "POST",
		contentType: "application/json",
		data: JSON.stringify({	'id': user_id,
                            	'token' : token
								}),
		success: function(result) {
			var users = "";
			for (i = 0; i < result.length; i++) { 
			  users += result[i]["id"] + "\n";
			}
			document.getElementById('users_building').value = users;
		}
	})	
}

function check_users_range() {
	$.ajax({
		url: "/API/user/show/range",
		type: "POST",
		contentType: "application/json",
		data: JSON.stringify({	'id': user_id,
    								'latitude': latitude,
    								'longitude': longitude,
                               'radious': parseInt(document.getElementById('range').value),
                        		'token' : token
								}),
		success: function(result) {
			var users = "";
			for (i = 0; i < result.length; i++) { 
			  users += result[i] + "\n";
			}
			document.getElementById('users_range').value = users;
		}
	})	
}

function send_message() {
	var message = document.getElementById('message').value;
	var users = document.getElementById('users_range').value;
	if (!message || message.length === 0) {
		alert("Cannot send empty message!");
	} else if (!users || users.length === 0) {
    	alert("No users in range!");
    	document.getElementById('message').value = ""; 
	} else {
		$.ajax({
			url: "/API/user/message/send",
			type: "POST",
			contentType: "application/json",
			data: JSON.stringify({	'id': user_id, 
        								'users': users,
        								'token' : token,
    									'message' : message
									}),
			success: function() {
				document.getElementById('message').value = "";
			}
		})	
	}
}  

function receive_message() {
    $.ajax({
		url: "/API/user/message/receive",
		type: "POST",
		contentType: "application/json",
		data: JSON.stringify({	'id': user_id,
                        		'socket_id' : socket_id,
    								'token' : token 
								}),
		success: function(result) { 
			
			for (i = 0; i < result.length; i++) { 
			
				var res = JSON.parse(result[i]);					
				var message = res["timestamp"] + " -> [" + res["id"] + "]: " + res["message"] + "\n";
				
				if (messages_array.length == message_array_size) {
					messages_array.splice(message_array_size-1, 1); //Remove last element
				} 
				messages_array.unshift(message); //Add new element
		
			}
			document.getElementById('messages_received').value = messages_array.join("");						
		}
	})	
} 