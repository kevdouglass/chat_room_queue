import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
# Get data from DB 
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from channels.routing import ChannelNameRouter
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from .models import Message, Room
from django.utils import timezone

class ChatMessageConsumer( AsyncWebsocketConsumer ):
    '''
       > Synchronous Chat Consumer.
        self.connect : Obtains the 'room_name' param fro the UrlRoute in chat/routing.py that opened the WS connection to this Consumer.
            Every consumer has a 'Scope' that contains information about its connection, including kwargs fro the URL route and currently authenticated user, through request.<method> (if any)
                    - room_group_name: constructs a Channels Group name directly fro the user-specified room name, without any weird characters (quoting or escaping)
                    - async_to_sync( channel_layer.<GROUP_ADD> ): Joins a Group. the 'async_to_sync( ... )' wrapper is REQUIRED* because ChatConsumer is a synchronous WsConsumer but is calling an Async channels layer method (All channel layer methods are Async. calls). 
                    - self.accept():  Accepts Ws connection. If you don't call accept, the connection will be rejected and closed (you may want this behavior when a requesting user is not authorized to perform this requested action (Not yet signed Up)). 
        self.disconnect :            
                    - async_to_sync( channel_layer.<GROUP_DISCARD> ): When user leaves the Group (logout)
        self.receive :
                    - async_to_sync( channel_layer.<GROUP_SEND> ):  Sends an Event to a Group. An Event has a special 'type' key corresponding to the name of the METHOD that should be invoked on Consumers that receive the event.

        > Read more (Channels Docs): https://channels.readthedocs.io/en/stable/tutorial/part_2.html
    '''
    # Attrs:
    # user_waiting_room_list = {}
    user_queue = {}
    # commands = {
    #     'fetch_messages': fetch_messages,
    #     'new_message': new_message,
    # }
    #####################################################
    # Models.Room Sync_to_aSYNC methods
    #####################################################


    #####################################################
    # End of Room Sync_to_aSYNC methods
    #####################################################


    # Helpers
    #####################################################
    @database_sync_to_async
    def get_User_obj(self):
        return User.objects.get(id=self.scope['user'].id, name=self.scope['user'].username)
    
    @database_sync_to_async
    def get_current_room(self, room_name):
        '''Return the current room the user is in'''
        return Room.objects.get(name=room_name)
    
    @database_sync_to_async
    def get_real_time_users_from_room(self, room_name):
        this_room = Room.objects.get(name=room_name)
        this_room_real_time_users = []
        all_real_time_users = this_room.users.exclude(id=self.user.id)
        if this_room and all_real_time_users:
            print("DB.real-Time: ", all_real_time_users)
            print("\n\nYiup..")

            for person in all_real_time_users:
                print(person.id, person.username)
                this_room_real_time_users.append({'id': person.id , 'username':person.username})
        return this_room_real_time_users
    
    @database_sync_to_async
    def fetch_saved_messages(self, room):
        """Retrieve CHAT objects (currently called 'Messages') that point to this.Room_name """
        # return User.objects.filter(idcurrent_logged_in_user_ids)
        # Query Message Model to see which user is currently logged in to this channel?
        message_list = Message.objects.filter(room=room)
        savedChatHash = []
        for chat in message_list:
            savedChatHash.append({'user':{'id': chat.user.id, 'username':chat.user.username}, 'room':{'id':chat.room.id, 'name':chat.room.name}, 'content':chat.content})
        # print("chatHash--Message List: {}".format(savedChatHash)) 

        return savedChatHash

    @database_sync_to_async
    def save_users_to_room(self, user, room_name):
        print(f"Saving. New [User: {user.username}] Joined [{room_name}]")
        saved_room = Room.objects.create(users=user,name=room_name )
        # saved_room

    @database_sync_to_async
    def get_all_logged_in_user_sessions(self, this_user_username):
        # print("\n\nGet ALl Other Users:")
        print("Query Sessions Model")
        # Query all non-expired Sessions

        sessions = Session.objects.filter(expire_date__gte=timezone.now())
        current_logged_in_user_ids = []
        for sess in sessions:
            data = sess.get_decoded()
            # print(data['_auth_user_id'])
            session_user_id = data['_auth_user_id']
            current_logged_in_user_ids.append(session_user_id)
            
        print("Display cur_User_ids; {}".format(current_logged_in_user_ids))
        return current_logged_in_user_ids
        # return User.objects.filter(idcurrent_logged_in_user_ids)
        # Query Message Model to see which user is currently logged in to this channel?
        # this_message_room = Message.objects.filter(room=self.room_name)
        # print(f"******This->MessageRoom: {this_message_room}\n\n")
    
    @database_sync_to_async
    def new_message(self, data):
        '''
        # Message.user 
        # Message.room 
        # Message.content 
        '''
        this_user = User.objects.get(id=self.scope['user'].id)
        chat_data = {'user':this_user, 'room':Room.objects.get(name=self.room_name), 'msg_content':data}
        # Message.objects.create(
            # user=chat_data['user'], 
            # room=chat_data['room'], 
            # content=chat_data['msg_content']
            # )
 

    @database_sync_to_async
    def real_time_user_count_db(self, room_name):
        """Returns list of ALL real-time users (including the user whose session this is)"""
        # Get Current Room, check how many user are there
        this_room = Room.objects.get(name=room_name)
        if this_room is not None:
            return this_room.users.count()
        return 0

    @database_sync_to_async
    def dequeue_user_from_db(self, user, room_name):
        '''
        Need to Handle request.GET when User refreshes page, they should not necessarily be removed
        '''
        print('---'*25)
        print("DB.DEQUE..")
        this_room = Room.objects.get(name=room_name)
        if user and this_room is not None:
            print(f"Deque [{user.username}] from [{this_room.name}]")
            this_room.users.remove( user )

    @database_sync_to_async
    def enqueue_user_to_db(self, room_name, user):
        # Room.objects.get(name=room_name)
        print("DB.enqueue_user")
        this_room = Room.objects.get(name=room_name)
        print("Room Name: ",this_room.name)
        if this_room is not None: 
            print(f"[{user.username}]: Added to Room ({room_name})")
            this_room.users.add(user)
        return this_room
        # return [new_room_created, this_room]
 
    async def enqueue_user(self, user):
        '''waiting Q is differentiated by key-value:[list] dictionary of 
                current room-names being keys and each key containing a list of user_names
                of users inside
                 '''
        # if user is an authenticated User
        # if await User.objects.filter(id=user.id).exists():
            # Check if this user is in waiting list for game-room yet
            # authenticated_users = User.objects.get(id=user.id)
        # await Room.enqueue_user(user)
        if self.scope['user'].is_authenticated:
            print(f"\n[User: {user}] Authenticated!!")
            this_room_queue = await self.enqueue_user_to_db(room_name=self.room_name,user=self.user)
            # print(f"This->Room.Queue: {this_room_queue}")

            this_room_name = this_room_queue.name
            if this_room_name not in self.user_queue:
                self.user_queue[this_room_name] = []

                # print("Waiting Queue: ", self.user_queue)
                # print("User.is_authenticated When Room:{} == Room:{}".format(self.room_name,this_room.name ))
                if user.username not in self.user_queue[this_room_name]:
                    print(f"****\t\tAdding {str(user)} to UserQueue!!\n")
                    self.user_queue[this_room_name].append(user.username)

        


    async def connect(self):
        '''Make handshake & connect Consumer to WS'''
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        # Get current User obj
        self.user = self.scope['user']  # Other User is: ['url_route']['kwargs']['']
        self.user_id = self.user.id
        # Join Room Group through WS
        await self.channel_layer.group_add(
            self.room_group_name, 
            self.channel_name
        )
        
        await self.enqueue_user(self.scope['user'])
        real_time_users = await self.get_real_time_users_from_room(self.room_name)
        real_time_user_count = await self.real_time_user_count_db(self.room_name)
        print(f"[Counting-({real_time_user_count})-real_time_users]: {real_time_users}")
        # print("Now: ", self.user_queue)
        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "user_broadcast",
                "real_time_users": real_time_users,
                "count" : real_time_user_count
            }
        )
        await self.accept()


    async def disconnect(self, disconnect_code):
        ''' Leave a Room (Group)'''
        await self.dequeue_user_from_db(user=self.scope['user'], room_name=self.room_name)
        print(f"Channel info (DISCONNECT {self.scope['user'].username} FROM {self.room_name})")
        # removed_user = self.user_queue[self.room_name].pop( self.user_queue.index(self.scope['user'].username) )
        # print(self.user_queue)
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name 
        )


    async def receive(self, text_data):
        '''Receive message FROM WS:'''
        '''calls group_send message after determining which command waas called'''
        text_data_json = json.loads(text_data)
        await self.new_message(text_data_json['message'])
        this_room_name = await self.get_current_room(self.room_name)
        saved_chatroom_messages = await self.fetch_saved_messages(this_room_name)
        real_time_users = await self.get_real_time_users_from_room(self.room_name)
        real_time_user_count = await self.real_time_user_count_db(self.room_name)
        print(f"[Counting-({real_time_user_count})-real_time_users]: {real_time_users}")
        
        # all_user_sessions = await self.get_all_logged_in_user_sessions(self.user.username)
        # print("SHOW All other Users: ".format(all_user_sessions))

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': text_data_json['message'],
                'user_id' : self.user_id,
                'user_username' : self.user.username,
                "real_time_users": real_time_users,
                "count" : real_time_user_count,
                # 'user_queue_nodes':self.user_queue,
                # 'all_other_users' : self.all_other_users,
            }
        )

    async def chat_message(self, event):
        '''Receives messages from our Group and Broadcast it to Client-Websocket'''
        # Send message to WS 
        await self.send(text_data=json.dumps({ 
            'message' : event['message'],
            'user_id' : event['user_id'],
            'user_username': event['user_username'],
            "real_time_users": event['real_time_users'],
            "count" : event['count'],
            # 'user_queue_nodes': event['user_queue_nodes'],
            # 'all_other_users' : event['all_other_users']
        }))
    


    async def user_broadcast(self, event):
        await self.send(text_data=json.dumps({ 
            "real_time_users": event['real_time_users'],
            "count" : event['count'],
            # 'user_queue_nodes' : event['user_queue_nodes'],
        }))



















    # def set_message(self, message_data):
    #     msg = Message(user=self.user, content=message_data)
    #     msg.save()
    # def isNewRoom(self, _room_name):
    #     # Room.objects.filter(name=_room_name).
    #     if Room.objects.filter(name=_room_name).exists():
    #         return redirect
    
    # def set_room(self, _room_name, _user_name):
    #     this_room_name = _room_name
    #     this_user_name = _user_name
    #     print(f"User: {this_user_name} is CREATING New Room: {this_room_name}")
        
    #     room = Room(name=this_room_name, user=this_user_name)
    #     room.save()





# #########################################
# Synchronous WS Consumer
##############################################33



# class ChatMessageConsumer( WebsocketConsumer ):
#     '''
#        > Synchronous Chat Consumer.
#         self.connect : Obtains the 'room_name' param fro the UrlRoute in chat/routing.py that opened the WS connection to this Consumer.
#             Every consumer has a 'Scope' that contains information about its connection, including kwargs fro the URL route and currently authenticated user, through request.<method> (if any)
#                     - room_group_name: constructs a Channels Group name directly fro the user-specified room name, without any weird characters (quoting or escaping)
#                     - async_to_sync( channel_layer.<GROUP_ADD> ): Joins a Group. the 'async_to_sync( ... )' wrapper is REQUIRED* because ChatConsumer is a synchronous WsConsumer but is calling an Async channels layer method (All channel layer methods are Async. calls). 
#                     - self.accept():  Accepts Ws connection. If you don't call accept, the connection will be rejected and closed (you may want this behavior when a requesting user is not authorized to perform this requested action (Not yet signed Up)). 
#         self.disconnect :            
#                     - async_to_sync( channel_layer.<GROUP_DISCARD> ): When user leaves the Group (logout)
#         self.receive :
#                     - async_to_sync( channel_layer.<GROUP_SEND> ):  Sends an Event to a Group. An Event has a special 'type' key corresponding to the name of the METHOD that should be invoked on Consumers that receive the event.

#         > Read more (Channels Docs): https://channels.readthedocs.io/en/stable/tutorial/part_2.html
#     '''
#     def fetch_messages(self, data):
#         pass 

#     def new_message(self, data):
#         pass

#     commands = {
#         'fetch_messages': fetch_messages,
#         'new_message': new_message,
#     }

#     def connect(self):
#         '''Make handshake & connect Consumer to WS'''
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.user = self.scope['user']
#         self.room_group_name = 'chat_%s' % self.room_name
#         print("(1) Django.Connecting")
#         print(f"(Room-Name, Room-Group-Name) : ({self.room_name}, {self.room_group_name}) ")
        
#         # Join Room Group through WS
#         async_to_sync(self.channel_layer.group_add)(
#             self.room_group_name, 
#             self.channel_name
#         )
#         # print(f"Creating New Room: {self.room_name}")
#         # database_sync_to_async()(self.room_name)
#         # self.set_room(self.room_name, self.user)
#         self.accept()

#     def disconnect(self, disconnect_code):
#         ''' Leave a Room (Group)'''
#         async_to_sync(self.channel_layer.group_discard)(
#             self.room_group_name,
#             self.channel_name 
#         )


#     def receive(self, text_data):
#         '''Receive message FROM WS:'''
#         '''calls group_send message after determining which command waas called'''
#         text_data_json = json.loads(text_data)
#         print("(2) Django.Receive")
#         self.user = self.scope['user']  # Other User is: ['url_route']['kwargs']['']
#         print(f"User? {self.user}")

#     # def send_chat_message(self, message):
#         message = text_data_json['message']
#         async_to_sync(self.channel_layer.group_send)(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message,
#             }
#         )

#     def chat_message(self, event):
#         '''Receives messages from our Group'''
#         message = event['message']
#         print("\n(3) chat_message get-EVENT,")
#         print("send-EVENT: \n{}".format(event))
#         # Send message to WS 
#         self.send(text_data=json.dumps({ 
#             'message' : message,
#         }))
    
#     def get_username(self):
#         return User.objects.all()[0].name

    # def set_message(self, message_data):
    #     msg = Message(user=self.user, content=message_data)
    #     msg.save()
    # def isNewRoom(self, _room_name):
    #     # Room.objects.filter(name=_room_name).
    #     if Room.objects.filter(name=_room_name).exists():
    #         return redirect
    
    # def set_room(self, _room_name, _user_name):
    #     this_room_name = _room_name
    #     this_user_name = _user_name
    #     print(f"User: {this_user_name} is CREATING New Room: {this_room_name}")
        
    #     room = Room(name=this_room_name, user=this_user_name)
    #     room.save()