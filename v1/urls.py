from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create, name='create'),
    path('<uuid:room_id>/<str:user_name>/', views.sender, name='sender'),
    path('<uuid:room_id>/share/<str:other_person_name>/', views.receiver, name='receiver'),
    path('<uuid:room_id>/', views.room, name='room'),
]
