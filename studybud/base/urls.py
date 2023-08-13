from django.urls import path
from .views import *
urlpatterns = [
    path('login/', login_page, name='login'),
    path('logout/', logout_user, name='logout'),
    path('register/', register_page, name='register'),
    path('', home, name='home'),
    path('room/<str:pk>/', room, name='room'),
    path('profile/<str:pk>/', user_profile, name='user-profile'),
    path('create-room/', create_room, name='create-room'),
    path('update-room/<str:pk>/', update_room, name='update-room'),
    path('delete-room/<str:pk>/', delete_room, name='delete-room'),
    path('delete-message/<str:pk>/', delete_message, name='delete-message'),
    path('update-user/', update_user, name='update-user'),
    path('topics/', topics_page, name='topics'),
    path('activities/', activity_page, name='activities'),
]