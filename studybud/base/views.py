from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Room, Topic, Message, User
from .forms import *
from django.db.models import Q, Count
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def login_page(request):
    page='login'
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, "User does not exist")

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Username or password does bot exist")
    context = {'page': page}
    return render(request, 'base/login_register.html', context)
def home(request):
    q = request.GET.get('q') if request.GET.get('q') else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | 
        Q(host__username__icontains=q) |
        Q(description__icontains=q))
    topics = Topic.objects.annotate(quantity=Count('room'))[:5]
    room_messages = Message.objects.filter(room__topic__name__icontains=q)

    room_count = rooms.count()
    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context=context)

def room(request, pk):
    room = Room.objects.get(pk=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages, 'participants': participants}
    return render(request, 'base/room.html', context=context)


def user_profile(request, pk):
    user = User.objects.get(pk=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.annotate(quantity=Count('room'))
    room_count = Room.objects.all().count()
    context = {'user': user, 'rooms': rooms, 'room_messages': room_messages, 'topics': topics, 'room_count': room_count}
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        
        Room.objects.create(
            host=request.user,
            topic = topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        return redirect('home')
    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context=context)

@login_required(login_url='login')
def update_room(request, pk):
    room = Room.objects.get(pk=pk)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse("You are not allowed here")


    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = description=request.POST.get('description')
        room.save()
        return redirect('home')
    
    else:
        form = RoomForm(instance=room)
    
    context = {'form': form, 'room': room, 'topics': topics}
    return render(request, 'base/room_form.html', context=context)

@login_required(login_url='login')
def delete_room(request, pk):
    room = Room.objects.get(pk=pk)

    if request.user != room.host:
        return HttpResponse("You are not allowed here")
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})


def logout_user(request):
    logout(request)
    return redirect('home')

def register_page(request):
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "An error occured during registration")
    else:
        form = MyUserCreationForm
    return render(request, 'base/login_register.html', {'form': form})


@login_required(login_url='login')
def delete_message(request, pk):
    message = Message.objects.get(pk=pk)

    if request.user != message.user:
        return HttpResponse("You are not allowed here")
    
    if request.method == 'POST':
        message.delete()
        return redirect('room', message.room.id)
    return render(request, 'base/delete.html', {'obj': message})


@login_required(login_url='login')
def update_user(request):
    user = request.user

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    else:
        form = UserForm(instance=user)
    context = {'form': form}
    return render(request, 'base/update-user.html', context)


def topics_page(request):
    q = request.GET.get('q') if request.GET.get('q') else ''
    topics = Topic.objects.filter(name__icontains=q)
    context = {'topics': topics}
    return render(request, 'base/topics.html', context)


def activity_page(request):
    room_messages = Message.objects.all()
    context = {'room_messages': room_messages}
    return render(request, 'base/activity.html', context)