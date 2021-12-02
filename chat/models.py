from os import name
from django.core.checks import messages
from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields.related import ForeignKey
from channels.db import database_sync_to_async
# Create your models here.
class Room(models.Model):
    '''a room can have many users,
        a room has a name,
        a room can have many messages,
    '''
    name = models.CharField(max_length=75, blank=True, null=True)
    users = models.ManyToManyField(User, related_name='rooms')

    @database_sync_to_async
    def enqueue_user(self, room_name, user):
        room, new_room_created = Room.objects.get_or_create(name=room_name)
        room.users.add(user)
        # return self.objects.create(name=room_name)
        return new_room_created

    @database_sync_to_async
    def user_count(self, room_name):
        # Get Current Room, check how many user are there
        this_room = Room.objects.get(name=room_name)
        if this_room.exists():
            return this_room.users.count()
        return 0

    @database_sync_to_async
    def dequeue_user(self, user, room_name):
        this_room = Room.objects.get(name=room_name)
        if this_room.exists():
            this_room.users.remove( user )


class Message(models.Model):
    """
        PARAMS:
        ------
            user,
            room,
            content,
            timestamp(Optional)
        -------------------
        A Room can have MANY messages,
        A User can have MANY messages

    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, blank=True, null=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.content

    def pre_load(self):
        '''load the most recent 10 messages'''
        return Message.objects.order_by('-timestamp').all()[:10]

    
    




