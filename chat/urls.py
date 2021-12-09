from django.urls import path, re_path
from . import views

urlpatterns = [ 
    # path('/room', views.index, name='chat-index'),
    path('search/', views.room_index, name='chat-index'),
    path('rooms/<str:room_name>/', views.room, name='chat-room'),
    path('rooms/<str:room_name>/fetch/', views.fetch_room_data, name='fetch-room-data'),
    

]