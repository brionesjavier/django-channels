from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json
from . import models
from django.contrib.auth.models import User
from datetime import datetime

class ChatConsumer(WebsocketConsumer):
    
    def connect(self):
        # Acepta la conexión WebSocket
        self.accept()
        #print("Nueva conexión WebSocket establecida")
        #self.send('{ "type":"accept", "status":"accepted" }')

        '''
        # prueba de scope completo 
        #print(self.scope)

        # prueba de scope con user 
        #print(self.scope.get("user"))
        #print(self.scope.get("user").id)
        #print(self.scope.get("user").last_name)
        #print(self.scope.get("user").first_name)

        # prueba de scope con session
        #print(self.scope.get("session"))
        #print(self.scope.get("session").get("get_me_from_the_consumer"))

        # prueba de scope con url_route
        #print(self.scope.get("url_route"))
        #print(self.scope.get("url_route").get("kwargs"))
        #print(self.scope.get("url_route").get("kwargs").get("name")) 
     
        # prueba de channel_layer
        #print(type(self.channel_layer))
        #print(self.channel_name)
        #print(self.channel_layer)
        #print(self.channel_layer.channels)
        
        # prueba de channel_layer con groups
        #async_to_sync(self.channel_layer.group_add)("momo_group",self.channel_name)
        #async_to_sync(self.channel_layer.group_add)("group_channels",self.channel_name)
        #print(self.channel_layer.groups)

        #data = {"type":"receiver_function", "message":"hi my name is javier", "my las name is":"briones" }
        #async_to_sync(self.channel_layer.send)(self.channel_name,{"type":"chat.message","message":"hello"})
        #async_to_sync(self.channel_layer.send)(self.channel_name, data)

        #async_to_sync(self.channel_layer.group_send)("group_channels", data)
        '''
        try:
            user_channel = models.UserChannel.objects.get(user=self.scope.get("user"))
            user_channel.channel_name = self.channel_name
            user_channel.save()
        except:
            user_channel = models.UserChannel()
            user_channel.user = self.scope.get("user")
            user_channel.channel_name = self.channel_name
            user_channel.save()
        #async_to_sync(self.channel_layer.group_add)("test",self.channel_name)
        self.person_id = self.scope["url_route"]["kwargs"]["id"]
        #print(self.scope.get("url_route").get("kwargs").get("id")) 

    def receive(self, text_data):
        # Maneja los mensajes recibidos
        print(text_data)
        #self.send('{ "type":"event_arrive", "status":"arrived" }')

        # Puedes responder algo al cliente
        #self.send(text_data="Servidor recibió: " + text_data)
        text_data = json.loads(text_data)
        type = text_data.get("type")
        message = text_data.get("message")
        print(type)
        print(message)

        now = datetime.now()
        date = now.date()
        time = now.time()
        #print("date:", date)
        #print("time:", time)
        other_user = User.objects.get(id=self.person_id)

        if(text_data.get("type")=="new_message"):

            new_message = models.Message()
            new_message.from_who = self.scope.get("user")
            new_message.to_who= other_user
            new_message.message = text_data.get("message")
            new_message.date = date
            new_message.time = time
            new_message.has_been_seen = False
            new_message.save() 

            try:
                user_channel_name = models.UserChannel.objects.get(user=other_user)
                print("user_channel_name:", user_channel_name)

                data = {
                    "type":"receiver_function",
                    "type_of_data":"new_message",
                    "data":text_data.get("message")
                }
                async_to_sync(self.channel_layer.send)(user_channel_name.channel_name, data)
            except:
                pass
        elif(text_data.get("type")=="messages_received"):

            messages = models.Message.objects.filter(from_who=other_user, to_who=self.scope.get("user"), has_been_seen=False)
            for message in messages:
                message.has_been_seen = True
                message.save()

            try:
                user_channel_name = models.UserChannel.objects.get(user=other_user)
                print("user_channel_name:", user_channel_name)

                data = {
                    "type":"receiver_function",
                    "type_of_data":"messages_seen",
                }
                async_to_sync(self.channel_layer.send)(user_channel_name.channel_name, data)
                print("mensajes marcados como vistos")
                messages_seen = models.Message.objects.filter(from_who=other_user, to_who=self.scope.get("user"))
                messages_seen.update(has_been_seen=True)
            except:
                pass
        else:
            print("no action")
            pass
        
    def disconnect(self, close_code):
        # Lógica cuando el cliente se desconecta
        print(f"Conexión cerrada con código: {close_code}")
    
    def receiver_function(self, text_data):
        data = json.dumps(text_data)
        print("Data received in receiver_function:", data)
        self.send(data)