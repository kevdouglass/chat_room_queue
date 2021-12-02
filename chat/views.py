from django.shortcuts import redirect, render
from .models import Room
from django.contrib.auth.models import User
from .forms import RoomForm
# Create your views here.
def room_index(request):
    # print("Attempting -- \t\t \nChat.views.Create_Room: \t")
    users = User.objects.exclude(username=request.user.username)
    print("Users: {}".format(users))
    if request.method == 'POST':
        if 'create-room' in request.POST:
            print("create-room in Req.POST: \t" , request.POST)
            new_room_form = RoomForm( request.POST )
            if new_room_form.is_valid():
                this_room_name = new_room_form.cleaned_data['name']
                if not Room.objects.filter(name=this_room_name).exists():
                    print("\n\nNew Room {}".format(this_room_name))
                    print("{} does not yet exist in Library!!!".format(this_room_name))
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


# from django_redis import get
# create-rooms
def room(request, room_name:str):
    # print(f"Req.Method: {request}")
    return render(request, 'chat/msg_room.html', { 
        'room_name': room_name,
        'user_list': User.objects.exclude(username=request.user.username),
        'user_name': request.user.username,
    })


def fetch_rooms(request):
    
    return render(request, 'chat/room_index.html', { 
        'chat_rooms': Room.objects.all(), #None, #Room.objects.get(id=room_id)
    })

