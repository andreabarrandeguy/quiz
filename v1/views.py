
from django.shortcuts import render, redirect, get_object_or_404

from quiz2.settings import EMAIL_HOST_USER
from .models import Room, Question
from .forms import NewQuestionForm, NewRoomForm
from .utils import SendEmail, check_completeness

def index(request):
    return render(request, 'v1/index.html')

def create(request):

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

        #SEND MAIL TO RECEIVER
        scheme = request.scheme
        link = request.get_host()
        subject_receiver= f'Room | Join {room.user_name}!'
        message_receiver=f'Hi {room.other_person_name}, {room.user_name} is challenging you to join Room and answer questions about each other. How well do you know each other? Visit this <a href="{scheme}://{link}/{room.id}/{room.other_person_name}">link</a> and find out!'
        SendEmail(room.receiver_email, EMAIL_HOST_USER, subject_receiver, message_receiver)
        #SEND MAIL TO SENDER
        subject_sender=f'Room Created'
        message_sender=f'Hi {room.user_name}, you have successfully created a Room. If you havent already, please answer the questions about {room.other_person_name} and yourself by visiting this <a href="{scheme}://{link}/{room.id}/{room.user_name}">link</a>.'
        SendEmail(room.sender_email, EMAIL_HOST_USER, subject_sender, message_sender)
         
        return redirect(f'/{room.id}/{room_form.cleaned_data["user_name"]}/')

    temp_questions = request.session.get('temp_questions', [])
    return render(request, 'v1/create.html', {
        "room_form": room_form,
        "question_form": question_form,
        "questions": temp_questions
    })


def room2(request, room_id, name):

    #GET ROOM OBJECTS
    room = get_object_or_404(Room, id=room_id) 
    
    #BOOLEAN CHECKING IF SENDER OR RECEIVER
    user_sender = False    
    user_receiver = False
    if name == room.user_name:
        user_sender = True
    elif name == room.other_person_name:
        user_receiver = True
    else:
        return render(request, 'v1/404.html')

    #GET QUESTIONS FROM MODEL AND CHECKING IF COMPLETED    
    questions = Question.objects.filter(room=room)    
    completeness = check_completeness(room.id)

    #GETS EMAIL ADRESSES
    sender_email=room.sender_email
    receiver_email=room.receiver_email

    #GETS LINKS FOR MAILS
    scheme = request.scheme
    link = request.get_host()


    #IF BOTH COMPLETED REDIRECT TO ROOM
    if completeness['sender_completed'] and completeness['receiver_completed']:
        return render(request, 'v1/room.html', {
            'user_sender': user_sender,
            'user_receiver': user_receiver,
            'completeness': completeness,
            'room': room,
            'questions': questions,
            'name':name
        })
    
    #SENDER HASN'T REPLIED AND REDIRECT TO ANSWER.
    if user_sender and not completeness['sender_completed']:
        if request.method == 'POST':   
        # For each question
            for question in questions:
                # SENDER replies about themselves (self_a)
                question.self_a = request.POST.get(f'self_a_{question.question_id}')
                # SENDER replies about RECEIVER (other_a)
                question.other_a = request.POST.get(f'other_a_{question.question_id}')
                question.save()
            
            #UPDATE LAST_MODIFICATION AND COMPLETENESS BEFORE MAIL AND REDIRECT
            room.save() 
            completeness=check_completeness(room.id)
            
            #NOTIFICATIONS TO RECEIVER
                #IF RECEIVER HASN'T YET REPLIED
            if not completeness['receiver_completed']:
                subject= f'Room | {name} has just replied about you.'
                message = f'Hi, {room.other_person_name}. {name} is taking the lead and has already answered the questions in Room! Follow this <a href="{scheme}://{link}/{room.id}/{room.other_person_name}">link</a> to catch up!'
                SendEmail(receiver_email, EMAIL_HOST_USER, subject, message)
                #IF RECEIVER REPLIED FIRST - ROOM COMPLETED
            elif completeness['receiver_completed']:
                subject=f'Room | View your results!'
                message=f'Hi, {room.other_person_name}. {name}  has already replied and Room is complete! Visit this <a href="{scheme}://{link}/{room.id}/{room.other_person_name}">link</a> to view your results and find out how well you know each other.'
                SendEmail(receiver_email, EMAIL_HOST_USER, subject, message)

            return render(request, 'v1/room.html', {
                'user_sender': user_sender,
                'user_receiver': user_receiver,
                'completeness': completeness,
                'room': room,
                'questions': questions,
                'name':name
                })
            
        return render(request, 'v1/answers.html', {
        'user_sender': user_sender,
        'user_receiver': user_receiver,
        'completeness': completeness,
        'room': room,
        'questions': questions,
        'name':name
        })      
        
    
    #IF RECEIVER STILL HASN'T REPLIED, REDIRECT TO ANSWER.    
    if user_receiver and not completeness['receiver_completed']:
        if request.method == 'POST':
            for question in questions:
                # RECEIVER replies about themselves (self_b)
                question.self_b = request.POST.get(f'self_b_{question.question_id}')
                # RECEIVER replies about SENDER (other_b)
                question.other_b = request.POST.get(f'other_b_{question.question_id}')
                question.save()
            #UPDATE LAST_MODIFICATION
            room.save()
            #UPDATE COMPLETENESS BEFORE MAILS AND REDIRECT
            completeness=check_completeness(room.id)
            
            #NOTIFICATIONS
                #IF SENDER HASN'T YET REPLIED
            if not completeness['sender_completed']:
                subject= f'Room | {name} has just replied about you.'
                message = f'Hi, {room.user_name}. {name} is taking the lead and has already answered the questions in Room! Follow this <a href="{scheme}://{link}/{room.id}/{room.user_name}">link</a> to catch up!.'
                SendEmail(sender_email, EMAIL_HOST_USER, subject, message)
                #IF SENDER REPLIED FIRST - ROOM COMPLETED
            elif completeness['sender_completed']:
                subject=f'Room | View your results!'
                message=f'Hi, {room.user_name}. {name} has already replied and Room is complete! Visit this <a href="{scheme}://{link}/{room.id}/{room.user_name}">link</a> to view your results and find out how well you know each other.'
                SendEmail(sender_email, EMAIL_HOST_USER, subject, message)    
        
            return render(request, 'v1/room.html', {
            'user_sender': user_sender,
            'user_receiver': user_receiver,
            'completeness': completeness,
            'room': room,
            'questions': questions,
            'name':name
            })
        
        return render(request, 'v1/answers.html', {
        'user_sender': user_sender,
        'user_receiver': user_receiver,
        'completeness': completeness,
        'room': room,
        'questions': questions,
        'name':name
        })      
        
    #SEND MAIL WITH 'SEND REMINDER' BUTTON    
    if request.method =='POST':
        subject = f'Room | {name} is still waiting.'
        if user_sender:
            message = f'Hi {room.other_person_name}, this is a reminder from {name} who is still waiting for your answers in Room. When you get a moment, visit this <a href="{scheme}://{link}/{room.id}/{room.other_person_name}">link</a> and join the fun!'
            SendEmail(room.receiver_email, EMAIL_HOST_USER, subject, message)
        elif user_receiver:
            message = f'Hi {room.user_name}, this is a reminder from {name} who is still waiting for your answers in Room. When you get a moment, visit this <a href="{scheme}://{link}/{room.id}/{room.user_name}">link</a> and join the fun!'
            SendEmail(room.sender_email, EMAIL_HOST_USER, subject, message)
    
    return render(request, 'v1/room.html', {
    'user_sender': user_sender,
    'user_receiver': user_receiver,
    'completeness': completeness,
    'room': room,
    'questions': questions,
    'name':name
    })
    

def error(request):
    return render(request, 'v1/404.html')

def answers(request):
    return render(request, 'v1/answers.html')
