from django.http import request
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from .models import Message, Room
from django.contrib.auth.models import User
from .forms import RoomForm


# Create your views here.
def room_index(request):
    # print("Attempting -- \t\t \nChat.views.Create_Room: \t")
    users = User.objects.exclude(username=request.user.username)
    # print("Users: {}".format(users))
    if request.method == 'POST':
        if 'create-room' in request.POST:
            # print("create-room in Req.POST: \t" , request.POST)
            new_room_form = RoomForm( request.POST )
            if new_room_form.is_valid():
                this_room_name = new_room_form.cleaned_data['name']
                if not Room.objects.filter(name=this_room_name).exists():
                    # print("\n\nNew Room {}".format(this_room_name))
                    # print("{} does not yet exist in Library!!!".format(this_room_name))
                    Room.objects.create(name=this_room_name).save()
                return redirect('/chat/rooms/{}'.format(this_room_name))
            else:
                print("Form is NoT VALID")
                return render(request, 'chat/room_index.html', {
                    'newRoomForm': new_room_form,
                    'chat_rooms': Room.objects.all(),                    
                    })
        else:
            # Cancel
            print("Cancel")
            return redirect("/chat/search")
    # else:
    return render(request, 'chat/room_index.html', {
        'newRoomForm': RoomForm, 
        'chat_rooms': Room.objects.all(),
        'users': users,
        })


from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
async def broadcast_users(data):
    print("\n**(1) BroadCast Users")
    room_group_name = 'chat_%s' % data['room_name']
    try:

        sync_channel_layer = get_channel_layer()
        print(f"[{data['user_name']}] Entered: [{data['room_name']}]")
        realtime_user_waitingQ = data['user_list']
        realtime_user_waitingQ__count = len(realtime_user_waitingQ)
        # print(realtime_user_waitingQ)
        # print(realtime_user_waitingQ__count)
        # realtime_user_waitingQ.count()
        print(f"^^View.Room_Group_Name: [{room_group_name}]")
        # await sync_channel_layer.group_send(
        #     room_group_name,{
        #         "type": "user_notification",
        #         "real_time_users": realtime_user_waitingQ,
        #         "countr" : realtime_user_waitingQ__count,
        #     }
        # )
    except AssertionError:
        print("##DEBUG. No Channel Layer To SEND to")
    # return redirect(to='fetch-room-data')
    # async_to_sync(sync_channel_layer.group_send)("user_broadcast")


def fetch_room_data(request, room_name:str):
    # print(f"Req.Method: {request}")
    # User.objects.exclude(username=request.user.username)
    real_time_users = Room.objects.get(name=room_name).users.all()
    userHash = []
    for record in real_time_users:
        userHash.append({'id':record.id, 'username':record.username})
    
    
    
    data = {
        'room_name': room_name,
        'user_list': userHash,
        'user_name': request.user.username,
    }
    async_to_sync(broadcast_users)(data)
    # broadcast_users(data)
    print("(2) BroadCast Users")
    return JsonResponse(data)
    # return render(request, 'chat/msg_room.html', data)

def removeStaleUsers(request, room_name):
    room = Room.objects.get(name=room_name)
    user_list = room.users.all()
    # print(type(user_list))
    print("REQUEST: ", request.user)
    for user in user_list:
        if request.user.username == user.username:
            print(user.username)
            del user
        # user.
    print("[Manage.py Stale Users]: ",Room.objects.get(name=room_name).users)


# create-rooms
def room(request, room_name:str):
    # print(f"Req.Method: {request}")
    # User.objects.exclude(username=request.user.username)
    # removeStaleUsers(request, room_name)

    this_channel = get_channel_layer()
    print(this_channel)
    real_time_room = Room.objects.get(name=room_name)
    real_time_users = real_time_room.users.all()
    userHash = []
    for record in real_time_users:
        userHash.append({'id':record.id, 'username':record.username})

    chats = Message.objects.filter(room=real_time_room)
    # Message.objects.get()
    # for chat in 
 
    return render(request, 'chat/msg_room.html', { 
        'room_name': room_name,
        'user_name': request.user.username,
        'user_list': userHash,
        'saved_chats' : chats,
    })
