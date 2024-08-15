from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create, name='create'), # Create new room
    path('<uuid:room_id>/<str:name>/', views.room2, name='room2'),
    path('answers/<str:name>/', views.answers, name='answers'),
    
    path('s/<str:short_url>/', views.redirect_short_url, name='redirect_short_url'),
]
