from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create, name='create'), # Create new room
    path('<uuid:room_id>/<str:sender>/', views.sender, name='sender'), # Path for SENDER/Creator of room
    path('<uuid:room_id>/share/<str:receiver>/', views.receiver, name='receiver'), # Path for RECEIVER of room
    path('<uuid:room_id>/', views.room, name='room'), # View room
]
