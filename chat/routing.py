# chat/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/rooms/(?P<room_name>\w+)/$', consumers.ChatMessageConsumer.as_asgi()),
    # re_path(r'^room/(<?Pusername>[\w.@+-]+)$', consumers.ChatConsumer.as_asgi()),
]
# Note, the prefix 'ws/' on our re_path is not mandatory