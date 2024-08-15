from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, Question, TemporaryQuestion, shortURL
from .forms import NewQuestionForm, NewRoomForm
import random
from .utils import shorten_url, SendEmail, check_completeness

def index(request):
    return render(request, 'v1/index.html')

def create(request): #blablabla

    if 'room_data' not in request.session:
        request.session['room_data'] = {}
    if 'temp_questions' not in request.session:
        request.session['temp_questions'] = []
            
    room_data = request.session['room_data']
    temp_questions = request.session['temp_questions']

    room_form = NewRoomForm(initial=room_data)
    question_form = NewQuestionForm()      

     # delete temporary questions
    if 'delete_question_id' in request.GET:
        question_id = int(request.GET.get('delete_question_id'))
        if 0 <= question_id < len(temp_questions):
            temp_questions.pop(question_id)
            request.session['temp_questions'] = temp_questions
            return redirect('create')

    
    if request.method == 'POST' and 'add_question' in request.POST:      
        question_form = NewQuestionForm(request.POST)
        if question_form.is_valid():
            temp_question = question_form.cleaned_data['question']
            temp_questions = request.session.get('temp_questions', [])
            temp_questions.append(temp_question)
            request.session['temp_questions'] = temp_questions
            room_data = {
                'user_name': request.POST.get('user_name', ''),
                'other_person_name': request.POST.get('other_person_name', ''),
                'sender_email': request.POST.get('sender_email', ''),
                'receiver_email': request.POST.get('receiver_email', '')
            }
            request.session['room_data'] = room_data
            room_form = NewRoomForm(initial=room_data) #Conserve sender and receiver names within form
        return render(request, 'v1/create.html', {
            "room_form": room_form,
            "question_form": NewQuestionForm(),  # Reset question_form
            "questions": temp_questions
        })

        # Create room
    if request.method == 'POST' and 'create' in request.POST:
        room_form = NewRoomForm(request.POST)
        if room_form.is_valid():
            room = room_form.save()
            temp_questions = request.session.get('temp_questions', [])
            for temp_question in temp_questions:
                Question.objects.create(room=room, question=temp_question)
            request.session.pop('temp_questions', None)
            request.session.pop('room_data', None)
        return redirect(f'/{room.id}/{room_form.cleaned_data["user_name"]}/')

    temp_questions = request.session.get('temp_questions', [])
    return render(request, 'v1/create.html', {
        "room_form": room_form,
        "question_form": question_form,
        "questions": temp_questions
    })


def sender(request, room_id, sender):

    room = get_object_or_404(Room, id=room_id)
    questions = Question.objects.filter(room=room)
    receiver = room.other_person_name #Receiver wasn't specified
    receiver_email=room.receiver_email
    long_url=f'/{room_id}/share/{receiver}/'
    short_url=shorten_url(request, long_url)

    # After form is submitted
    if request.method == 'POST':
               
        questions = Question.objects.filter(room=room)        

        # For each question
        for question in questions:
            # SENDER replies about themselves (self_a)
            question.self_a = request.POST.get(f'self_a_{question.question_id}')
            # SENDER replies about RECEIVER (other_a)
            question.other_a = request.POST.get(f'other_a_{question.question_id}')
            question.save()
            completeness=check_completeness(room_id)
            
        #Notification when sender replies and receiver doesn't. 
        if completeness['sender_completed'] and not completeness['receiver_completed']:
            subject= f'{sender} has already answered about you.'
            message=f'Hi {receiver}, {sender} has already answered about you and waiting for your answers. Here is the link to your questions: {request.scheme}://{request.get_host()}/s/{short_url}' #Receiver gets link to answer
            SendEmail(request, receiver_email, room.id, room.user_name, subject, message)
        elif completeness['sender_completed'] and completeness['receiver_completed']:
            subject= f'{sender} has already answered about you.'
            message=f'Hi {receiver}, {sender} has already answered about you. Check out how much you know each other here: ______________' #TODO Receiver gets link to its room
            SendEmail(request, receiver_email, room.id, room.user_name, subject, message)
        
        # Redirects to room page (more in the "room" function)
        return redirect(f'/{room.id}/')
    
    # if method = "GET", obtains room id, related questions and RECEIVER name to display sender.html template
    
    subject = f'New room created'
    message = f'Hi!, {sender} just created a new room with you, please enter this link to answer the questions: {request.scheme}://{request.get_host()}/s/{short_url} '
    receiver_email = room.receiver_email
    SendEmail(request, receiver_email, room.id, room.user_name, subject, message)
    
    sender_email = room.sender_email
    message_sender= f'Hi,{sender}. You have succesfully created a new room, visit {request.scheme}://{request.get_host()}/{room.id}. You will receive a notification when {receiver} answer.'
    SendEmail(request, sender_email, room.id, room.user_name, subject, message_sender)

    
    return render(request, 'v1/sender.html', {
        'room_id': room.id, 
        'sender': sender, 
        'questions': questions, 
        'receiver': receiver,
        'short_url':short_url
        })

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

def redirect_short_url(request, short_url):
    short_url_instance = get_object_or_404(shortURL, short_url=short_url)
    return redirect(short_url_instance.long_url)