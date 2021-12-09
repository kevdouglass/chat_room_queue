import json
from asgiref.sync import async_to_sync, sync_to_async
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
from channels.auth import login
from channels.auth import logout 
from channels.auth import user_logged_in, user_logged_out
import requests as Requests

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
    def get_User_obj(self) -> User:
        '''
        PARAMS: None
        RETURN: user:User
        --------------
        Description.
            > Sync to Async. Make a DB.Connection and 
                access user.id, username attributes from self.scope.
            > Return a Single User object. 
        '''
        return User.objects.get(id=self.scope['user'].id, name=self.scope['user'].username)
    
    @database_sync_to_async
    def get_current_room(self, room_name:str):
        '''
        PARAMS: room_name:string
        RETURN: list:Dict
        --------------
        Description.
            > Sync to Async. Given a String called room_name, make a 
                DB.Connection and return the current room
        '''
        return Room.objects.get(name=room_name)
    
    @database_sync_to_async
    def get_real_time_users_from_room(self, room_name:str) -> list:
        """
        PARAMS: room_name:string
        RETURN: list:Dict
        --------------
        Description.
            > Fetch all User objects who have not left the Room. 
            > return list of dictionary containing keys {'id':[int],'username'[string]} 
                such that each entry is a real-time User.
        """
        this_room = Room.objects.get(name=room_name)
        this_room_real_time_users = []
        all_real_time_users = this_room.users.all() #exclude(id=self.user.id)
        if this_room and all_real_time_users:
            for person in all_real_time_users:
                print(person.id, person.username)
                this_room_real_time_users.append({'id': person.id , 'username':person.username})
        return this_room_real_time_users
    
    @database_sync_to_async
    def fetch_saved_messages(self, room:Room) -> list:
        """
        PARAMS: room:Room
        RETURN: list:User 
        -------
        DESCRIPTION.
            > Syncronous to Asyncronous. Handles Retrieval of Message objects 
                that point to this.Room_name. 
            > Query Message Model to see which user is currently logged in to this channel.
            > Take Chat-Messages list and PARSE User, Room, and MSG-Content to be re-used elsewhere. 
        
        *TODO (Model is currently called 'Messages', maybe better called "CHAT") 
        """
        message_list = Message.objects.filter(room=room)
        savedChatHash = []
        for chat in message_list:
            savedChatHash.append({'user':{'id': chat.user.id, 'username':chat.user.username}, 'room':{'id':chat.room.id, 'name':chat.room.name}, 'content':chat.content})
        return savedChatHash

    @database_sync_to_async
    def save_users_to_room(self, user:User, room_name:str) -> None:
        """
            PARAMS: user:User, room_name:string
            RETURN: NONE
            ------------------
            DESCRIPTION.
        """
        print(f"Saving. New [User: {user.username}] Joined [{room_name}]")
        saved_room = Room.objects.create(users=user,name=room_name )
        # saved_room.save()


    @database_sync_to_async
    def new_message(self, data:str) -> None:
        '''
            PARAMS: data:string
            RETURN: NONE
            -------
            DESCRIPTION.
                > Sync to Async. Handles DB.Connection with NEW Message Objects.
                > Messages are saved to Database, where
                    <MESSAGE> => {
                        USER, ROOM, MSG-CONTENT
                    }
        *TODO Message.Create currently commented out so I don't have to continuously Delete the Jiberish from our Database.
        '''
        this_user = User.objects.get(id=self.scope['user'].id)
        chat_data = {'user':this_user, 
                    'room':Room.objects.get(name=self.room_name), 
                    'msg_content':data}
        # Message.objects.create(
            # user=chat_data['user'], 
            # room=chat_data['room'], 
            # content=chat_data['msg_content']
            # )
 

    @database_sync_to_async
    def real_time_user_count_db(self, room_name:str) -> int:
        """
            PARAMS: room_name:string
            RETURN: int
            -------
            DESCRIPTION.
        Returns list of ALL real-time users (including the user whose session this is)"""
        # Get Current Room, check how many user are there
        this_room = Room.objects.get(name=room_name)
        if this_room is not None:
            return this_room.users.count()
        return 0

    @database_sync_to_async
    def dequeue_user_from_db(self, user:User, room_name:str) -> None:
        '''
            PARAMS: user:User, room_name:string
            RETURN: NONE
            -------
            DESCRIPTION.
                > Syncronous to Asyncronous Function. Allows for CRUD operations with Database (in this case D:Delete). 
                > Given a room_name, we make a DB.connection. If the Room object corresponding to 
                    the given room_name EXISTS and the User is an authenticated User (not Anonymous), Remove them from the Room.users specified with 
                    the ManyToMany relation with Users->Room (MxN) 
        *TODO
        Need to Handle request.GET when User refreshes page, they should not necessarily be removed
        '''
        print('---'*75)
        this_room = Room.objects.get(name=room_name)
        print(f"\n\n\nDeque [{user.username}] from [{this_room.name}]")
        print('---'*25)
        if user and this_room is not None:
            print(f"DB.Deque(2) [{user.username}] from [{this_room.name}]")
            print('---'*25)
            this_room.users.remove( user )
        user_li = async_to_sync(self.get_real_time_users_from_room)(this_room.name)
        # self.get_real_time_users_from_room(this_room.name)
        print(f"DB.Deque(3) {user_li}")
        # print(f"DB.Deque(2) [{user.username}] from [{this_room.name}]")
        print('---'*25)
    
    
    @database_sync_to_async
    def enqueue_user_to_db(self, room_name:str, user:User) -> Room:
        """
            PARAMS: room_name:str, user:User
            RETURN: this_room:QuerySet
            ------------------
            DESCRIPTION.
                > Syncronous to Asyncronous. Allows our 
                    AsyncWebsocketConsumer to make Database Connection so we can still apply CRUD operations
        """
        this_room = Room.objects.get(name=room_name)
        if this_room is not None: 
            print(f"[DB.enqueue  {user.username}]: Added to Room ({room_name})")
            this_room.users.add(user)
            
        return this_room
 
    async def enqueue_user(self, user:User) -> None:
        '''
            PARAMS: user:User
            RETURN: NONE
            ---------------------
            DESCRIPTION.
                > Asynchronous. Handles/Clean up the database connnection. 
                    <WAITING QUEUE>
                    ---------------
                        Waiting Q is differentiated by key-value:[list] dictionary of 
                        current room-names being keys and each key containing a list of user_names
                        of users inside
        '''
        if self.scope['user'].is_authenticated:
            this_room_queue = await self.enqueue_user_to_db(room_name=self.room_name,user=self.user)
            # if this_room_queue.name not in self.user_queue:
        print('[SOCKET.enqueu_User]: ', user.username, f" to {this_room_queue.name}")
            #     self.user_queue[this_room_queue.name] = []
            #     if user.username not in self.user_queue[this_room_queue.name]:
            #         self.user_queue[this_room_queue.name].append(user.username)

        

    
    async def connect(self) -> None:
        '''
            PARAMS: NONE
            RETURN: NONE
            -------
            DESCRIPTION.
                > Asynchronous. Make handshake with Javascript-CLIENT (PRODUCER), then,
                > Connect this Consumer to Server-Side WS (Django)
        '''
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        self.user = self.scope['user']  # Other User is: ['url_route']['kwargs']['']
      
        await self.enqueue_user(self.scope['user'])
        real_time_users = await self.get_real_time_users_from_room(self.room_name)
        real_time_user_count = await self.real_time_user_count_db(self.room_name)
        print(f"[Connecting] ... \tCurrently, {real_time_user_count}-real_time_users: {real_time_users}")
        
        # Join Room Group through WS
        await self.channel_layer.group_add(
            self.room_group_name, 
            self.channel_name
        )
        # Broadcast new User connecting to Group
        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "user_broadcast",
                "kind": "userConnectedNotification",
                "real_time_users": real_time_users,
                "count" : real_time_user_count
            }    
        )
        # Accept User connection (CURRENTLY, ALL TIME)
        await self.accept()


    async def disconnect(self, disconnect_code:int) -> None:
        '''     
            PARAMS: disconnect_code:int
            RETURN: NONE
            -------
            DESCRIPTION:
                > Asynchronous. Called upon User Leave a Room & During Refresh state (Group).
        '''
        disconnect_from_room = await self.get_current_room(self.room_name)
        await self.dequeue_user_from_db(user=self.scope['user'], room_name=self.room_name)
        # if self.scope['user'].is_authenticated:
        # await logout(self.scope)
            # self.scope['user'].logout
        # print('---'*25)
        print(f"Logging Out User: {self.user.username}")
        # print('---'*25)
        real_time_users__disconnect = await self.get_real_time_users_from_room(disconnect_from_room.name)
        print(await self.get_real_time_users_from_room(disconnect_from_room.name))
        real_time_users_disconnect__count = await self.real_time_user_count_db(disconnect_from_room.name)
        # removed_user = self.user_queue[self.room_name].pop( self.user_queue.index(self.scope['user'].username) )
        # print(self.user_queue)
        
        # Broadcase users and count to ALL in room
        for record_user in real_time_users__disconnect:

            await self.channel_layer.group_send(
                self.room_group_name, {
                    "type": "user_broadcast",
                    "kind": "userDisconnectedNotification",
                    "real_time_users": record_user,
                    "count" : real_time_users_disconnect__count,
                }
            )
        # Remove Group from channel_layer 
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name 
        )


    async def receive(self, text_data:str) -> None:
        '''
            PARAMS: text_data:string
            RETURN: NONE
            -------
            DESCRIPTION:
                > Asynchronous. Receive message FROM WS.
                > Calls group_send message after determining which 
                    command waas called.
        '''
        text_data_json = json.loads(text_data)
        await self.new_message(text_data_json['message'])
        this_room_name = await self.get_current_room(self.room_name)
        saved_chatroom_messages = await self.fetch_saved_messages(this_room_name)
        real_time_users = await self.get_real_time_users_from_room(self.room_name)
        real_time_user_count = await self.real_time_user_count_db(self.room_name)
        print(f"[There are NOW-({real_time_user_count})   real_time_users]: {real_time_users}")
        
        # PAYLOAD to be sent out (Broadcasted) when User submits a Chat-Message
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': text_data_json['message'],
                'user_id' : self.user.id,
                'user_username' : self.user.username,
                "real_time_users": real_time_users,
                "count" : real_time_user_count,
            }
        )

    async def chat_message(self, event:dict) -> None:
        '''
            PARAMS: event:dict
            RETURN: NONE
            -------
            DESCRIPTION:
                > Asynchronous. Receives messages from our Group and Broadcast it to Client-Websocket'''
        # Send message to WS-Client on Javascript side.
        await self.send(text_data=json.dumps({ 
            'message' : event['message'],
            'user_id' : event['user_id'],
            'user_username': event['user_username'],
            # "real_time_users": event['real_time_users'],
            "count" : event['count'],
        }))
    


    async def user_broadcast(self, event:dict) -> None:
        """    
            PARAMS: event:dict
            RETURN: NONE
            -------
            DESCRIPTION:
                > Asynchronous. Broadcast User(s) after they were Enqueud during the WS_server.CONNECT event to Client-Side Websocket.Receive. 
        """
        # print("EVENT: ", event)
        # print("\n\ncountrr",event['countrr']) 
        # print(f"Consumer.Room_Group_Name: [{self.room_group_name}]")
        if event['kind'] == "userDisconnectedNotification":
            # Broadcast the Disconnect (i.e. what users are still live)
            for record_user in event['real_time_users']:
                await self.send(text_data=json.dumps({
                    "kind" : "userDisconnectedNotification",
                    "real_time_user": record_user,
                }))
        elif event['kind'] == "userConnectedNotification":
            for record_user in event['real_time_users']:

                await self.send(text_data=json.dumps({ 
                    "kind": "userConnectedNotification",
                    "real_time_user": record_user,

                    # "real_time_users": event['real_time_users'],
                    # "count" : event['count'],
                    # 'user_queue_nodes' : event['user_queue_nodes'],
                }))

    async def user_notification(self, event:dict) -> None:
        """    
            PARAMS: event:dict
            RETURN: NONE
            -------
            DESCRIPTION:
                > Asynchronous. Broadcast User(s) after they were Enqueud during the WS_server.CONNECT event to Client-Side Websocket.Receive. 
        """
        print("EVENT: ", event)
        print(f"Consumer.Room_Group_Name: [{self.room_group_name}]")
        for rt_user in event['real_time_users']:

            await self.send(text_data=json.dumps({ 
                "kind": "userConnectedNotification",
                "real_time_user": rt_user,
                # "count" : event['count'],
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