
    ##########################################
#   Async Test/Example Consumer
    ##########################################
# (1)

# class ChatConsumer( AsyncWebsocketConsumer ):
#     '''
#        > Asynchronous Chat Consumer.
#        -----------------------------
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
#     async def connect(self):
#         '''Make handshake & connect Consumer to WS'''
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.room_group_name = 'chat_%s' % self.room_name

#         # Join Room Group through WS
#         await self.channel_layer.group_add(
#             self.room_group_name, 
#             self.channel_name
#         )

#         await self.accept()

#     async def disconnect(self, disconnect_code):
#         ''' Leave a Room (Group)'''
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name 
#         )


#     async def receive(self, text_data):
#         '''Receive message FROM WS:'''
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']
#         this_user = 'Avatar' #text_data_json['this_user']

#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message,
#             }
#         )
#         print(f"Async.Print : \t\t **Received New Message.\n User: {this_user}, Message: {message}")

#     async def chat_message(self, event):
#         '''Receives messages from our Group'''
#         message = event['message']
#         # this_user = event['user']
#         # Send message to WS 
#         await self.send(text_data=json.dumps({ 
#             'message' : message,
#         }))


########################################################################################################################################################################
########################################################################################################################################################################



########################################################################################################################################################################
########################################################################################################################################################################
# (2)