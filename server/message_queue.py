import pika
import logging
import json

filename = "credentials.json"

class message_queue:
    
    def __init__(self):    
        url = json.load(open(filename, encoding='utf-8'))["rabbitMQ"]["url"]
        self.params = pika.URLParameters(url)
            
    def open_connection(self):
        self.connection = pika.BlockingConnection(self.params)            
        self.channel = self.connection.channel()
            
    def close_connection(self):
        self.connection.close()
        
    def declare_queue(self, name):
        try:
            self.open_connection()
            self.channel.queue_declare(queue=name) #declare queue
            self.close_connection()
        except Exception as e:
            logging.error(e)
            
    def send_message(self, name, message):
        try:
            self.open_connection()
            self.channel.basic_publish(exchange='', routing_key=name, body=message)
            self.close_connection()
        except Exception as e:
            logging.error(e)
            
    def get_num_messages(self, name):
        try:
            self.open_connection()
            queue = self.channel.queue_declare(queue=name)
            self.close_connection()
            return queue.method.message_count
        except Exception as e:
            logging.error(e)
            return 0
        
    def receive_message(self, name):
        try:
            self.open_connection()
            msg = self.channel.basic_get(queue=name, no_ack=True)
            self.close_connection()
            return msg
        except Exception as e:
            logging.error(e)
            return ""
        
    def delete_queue(self, name):
        try:
            self.open_connection()
            self.channel.queue_delete(queue=name)
            self.close_connection()
        except Exception as e:
            logging.error(e)