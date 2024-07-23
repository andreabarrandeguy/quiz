from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, Question

def index(request):
    return render(request, 'v1/index.html')

def create(request):
    if request.method == 'POST':
        user_name = request.POST['user_name']
        other_person_name = request.POST['other_person_name']
        questions = [
            request.POST['question1'],
            request.POST['question2'],
            request.POST['question3'],
            request.POST['question4'],
            request.POST['question5']
        ]
        room = Room.objects.create(user_name=user_name, other_person_name=other_person_name)
        for q in questions:
            Question.objects.create(room=room, text=q)
        return redirect(f'/{room.id}/{user_name}/')
    return render(request, 'v1/create.html')

def sender(request, room_id, user_name):
    if request.method == 'POST':
        room = get_object_or_404(Room, id=room_id)
        questions = Question.objects.filter(room=room)
        for question in questions:
            question.self_a = request.POST.get(f'self_a_{question.question_id}')
            question.other_a = request.POST.get(f'other_a_{question.question_id}')
            question.save()
        return redirect(f'/{room.id}/')
    
    room = get_object_or_404(Room, id=room_id)
    questions = Question.objects.filter(room=room)
    other_person_name = room.other_person_name if room.user_name == user_name else room.user_name
    return render(request, 'v1/sender.html', {'room_id': room_id, 'user_name': user_name, 'questions': questions, 'other_person_name': other_person_name})

def room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    user_name = room.user_name
    other_person_name = room.other_person_name
    questions = Question.objects.filter(room=room)
    return render(request, 'v1/room.html', {'room_id': room_id, 'questions': questions, 'user_name': user_name, 'other_person_name': other_person_name})