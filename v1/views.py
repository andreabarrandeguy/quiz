from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, Question

def index(request):
    return render(request, 'v1/index.html')

def create(request):
    if request.method == 'POST':
        # Takes sender, receiver and questions
        sender = request.POST['sender']
        receiver = request.POST['receiver']
        questions = [
            request.POST['question1'],
            request.POST['question2'],
            request.POST['question3'],
            request.POST['question4'],
            request.POST['question5']
        ]
        # Creates new room object, with sender and receiver information gathered above
        room = Room.objects.create(user_name=sender, other_person_name=receiver)
        # For each of the questions, it creates a new question object tied to the room ID
        for q in questions:
            Question.objects.create(room=room, question=q)
        # Redirects for SENDER to answer the questions (more in the "sender" function)  
        return redirect(f'/{room.id}/{sender}/')
    return render(request, 'v1/create.html')

def sender(request, room_id, sender):
    # After form is submitted
    if request.method == 'POST':
        # Obtains room id from url, and its related questions
        room = get_object_or_404(Room, id=room_id)
        questions = Question.objects.filter(room=room)
        # For each question
        for question in questions:
            # SENDER replies about themselves (self_a)
            question.self_a = request.POST.get(f'self_a_{question.question_id}')
            # SENDER replies about RECEIVER (other_a)
            question.other_a = request.POST.get(f'other_a_{question.question_id}')
            question.save()
        # Redirects to room page (more in the "room" function)    
        return redirect(f'/{room.id}/')
    
    # if method = "GET", obtains room id, related questions and RECEIVER name to display sender.html template
    room = get_object_or_404(Room, id=room_id)
    questions = Question.objects.filter(room=room)
    receiver = room.other_person_name #Receiver wasn't specified
    return render(request, 'v1/sender.html', {'room_id': room.id, 'sender': sender, 'questions': questions, 'receiver': receiver}) #Change 'room_id':room_id for 'room_id':room.id

def receiver(request, room_id, receiver):
    # After form is submitted
    if request.method == 'POST':
        # Obtains room id from url, and its related questions
        room = get_object_or_404(Room, id=room_id)
        questions = Question.objects.filter(room=room)
        # For each question
        for question in questions:
            # RECEIVER replies about themselves (self_b)
            question.self_b = request.POST.get(f'self_b_{question.question_id}')
            # RECEIVER replies about SENDER (other_b)
            question.other_b = request.POST.get(f'other_b_{question.question_id}')
            question.save()
        # Redirects to room page (more in the "room" function)      
        return redirect(f'/{room.id}/')
    
    # if method = "GET", obtains room id, related questions and SENDER name to display receiver.html template
    room = get_object_or_404(Room, id=room_id)
    questions = Question.objects.filter(room=room)
    sender = room.user_name
    receiver = room.other_person_name
    return render(request, 'v1/receiver.html', {'room_id': room.id, 'sender': sender, 'questions': questions, 'receiver': receiver}) #'room_id':room_id for 'room_id':room.id

def room(request, room_id):
    # Obtains room id from url, looks for sender, receiver in model + All questions and answers
    room = get_object_or_404(Room, id=room_id)
    sender = room.user_name
    receiver = room.other_person_name
    questions = Question.objects.filter(room=room)
    return render(request, 'v1/room.html', {'room_id': room_id, 'questions': questions, 'sender': sender, 'receiver': receiver})