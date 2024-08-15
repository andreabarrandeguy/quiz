from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, Question, TemporaryQuestion, shortURL
from .forms import NewQuestionForm, NewRoomForm
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


def room2(request, room_id, name):

    room = get_object_or_404(Room, id=room_id) #GET ROOM OBJECTS
    
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

    #TODO: INSERTAR LINKS EN CORREOS

    #IF BOTH COMPLETED REDIRECT TO ROOM
    if completeness['sender_completed'] and completeness['receiver_completed']:
        return render(request, 'v1/room2.html', {
            'user_sender': user_sender,
            'user_receiver': user_receiver,
            'completeness': completeness,
            'room_id': room.id,
            'questions': questions,
            'name':name
        })
    
    if user_sender and not completeness['sender_completed']:
        if request.method == 'POST':   
        # For each question
            for question in questions:
                # SENDER replies about themselves (self_a)
                question.self_a = request.POST.get(f'self_a_{question.question_id}')
                # SENDER replies about RECEIVER (other_a)
                question.other_a = request.POST.get(f'other_a_{question.question_id}')
                question.save()

            #Notification when sender replies
            subject= f'{name} has already answered about you.'
            message=f'Hi {room.other_person_name}, {name} has already answered about you. Here is the link to your questions:______________' #Receiver gets link to answer
            SendEmail(request, receiver_email, room.id, room.user_name, subject, message)

            return render(request, 'v1/room2.html', {
                'user_sender': user_sender,
                'user_receiver': user_receiver,
                'completeness': completeness,
                'room_id': room.id,
                'questions': questions,
                'name':name
                })
            
        return render(request, 'v1/answers.html', {
        'user_sender': user_sender,
        'user_receiver': user_receiver,
        'completeness': completeness,
        'room_id': room.id,
        'questions': questions,
        'name':name
        })      
        
        
    if user_receiver and not completeness['receiver_completed']:
        if request.method == 'POST':
            for question in questions:
                # RECEIVER replies about themselves (self_b)
                question.self_b = request.POST.get(f'self_b_{question.question_id}')
                # RECEIVER replies about SENDER (other_b)
                question.other_b = request.POST.get(f'other_b_{question.question_id}')
                question.save()

            subject= f'{name} has already answered about you.'
            message=f'Hi {room.user_name}, {name} has already answered about you. Take a look'
            SendEmail(request, sender_email, room.id, room.user_name, subject, message)    
        
            return render(request, 'v1/room2.html', {
            'user_sender': user_sender,
            'user_receiver': user_receiver,
            'completeness': completeness,
            'room_id': room.id,
            'questions': questions,
            'name':name
            })
        
        return render(request, 'v1/answers.html', {
        'user_sender': user_sender,
        'user_receiver': user_receiver,
        'completeness': completeness,
        'room_id': room.id,
        'questions': questions,
        'name':name
        })      
        
        
    return render(request, 'v1/room2.html', {
    'user_sender': user_sender,
    'user_receiver': user_receiver,
    'completeness': completeness,
    'room_id': room.id,
    'questions': questions,
    'name':name
    })
    

def answers(request):
    return render(request, 'v1/answers.html')


def redirect_short_url(request, short_url):
    short_url_instance = get_object_or_404(shortURL, short_url=short_url)
    return redirect(short_url_instance.long_url)