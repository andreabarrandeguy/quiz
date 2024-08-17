
from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, Question, shortURL
from .forms import NewQuestionForm, NewRoomForm
from .utils import shorten_url, SendEmail, check_completeness

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
        subject_receiver= f'{room.user_name} just created a new room.'
        message_receiver=f'Hi {room.other_person_name}, {room.user_name} created a new room. Take a look and answer the questions. Visit: {scheme}://{link}/{room.id}/{room.other_person_name}'
        SendEmail(request, room.receiver_email, room.id, room.user_name, subject_receiver, message_receiver)
        #SEND MAIL TO SENDER
        subject_sender=f'Room Created'
        message_sender=f'Hi {room.user_name}, you have succesfully created a new room. This is your link to answer: {scheme}://{link}/{room.id}/{room.user_name}'
        SendEmail(request, room.sender_email, room.id, room.user_name, subject_sender, message_sender)
         
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
        return redirect('error.html')

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
                subject= f'{name} has just replied about you.'
                message = f'Hi, {room.other_person_name}. {name} has replied about both of you. Please visit {scheme}://{link}/{room.id}/{room.other_person_name} and do your part.'
                SendEmail(request, receiver_email, room.id, room.user_name, subject, message)
                #IF RECEIVER REPLIED FIRST
            elif completeness['receiver_completed']:
                subject=f'{name} has just replied about you.'
                message=f'Hi, {room.other_person_name}. {name} has completed it part of the quiz. Visit this link and take a look how well you know each other: {scheme}://{link}/{room.id}/{room.other_person_name}'
                SendEmail(request, receiver_email, room.id, room.user_name, subject, message)

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
                subject= f'{name} has just replied about you.'
                message = f'Hi, {room.user_name}. {name} has already replied about both of you. Hurry up and visit {scheme}://{link}/{room.id}/{room.user_name}. {name} is still waiting.'
                SendEmail(request, sender_email, room.id, room.user_name, subject, message)
                #IF SENDER REPLIED FIRST
            elif completeness['sender_completed']:
                subject=f'{name} has just replied about you.'
                message=f'Hi, {room.user_name}. {name} has completed it part of the quiz. Visit this link and take a look how well you know each other: {scheme}://{link}/{room.id}/{room.user_name}'
                SendEmail(request, sender_email, room.id, room.user_name, subject, message)    
        
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
        
        
    return render(request, 'v1/room.html', {
    'user_sender': user_sender,
    'user_receiver': user_receiver,
    'completeness': completeness,
    'room': room,
    'questions': questions,
    'name':name
    })
    

def error(request):
    return render(request, 'v1/error.html')

def answers(request):
    return render(request, 'v1/answers.html')


def redirect_short_url(request, short_url):
    short_url_instance = get_object_or_404(shortURL, short_url=short_url)
    return redirect(short_url_instance.long_url)