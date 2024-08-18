from .models import Room, Question
from django.core.mail import EmailMessage
from django.conf import settings

def SendEmail(to_email, from_email, subject, html_message):
    email = EmailMessage(
        subject=subject,
        body=html_message,
        from_email=from_email,
        to=[to_email],
    )
    email.content_subtype = "html"  # Esto asegura que el mensaje sea tratado como HTML
    email.send(fail_silently=False)

def check_completeness(room_id):
    
    try:
        Room.objects.get(id=room_id)
    except Room.DoesNotExist:
        return{'sender_completed':False, 'receiver_completed':False}

    questions=Question.objects.filter(room=room_id)
    sender_completed=all(q.self_a and q.other_a for q in questions)
    receiver_completed=all(q.self_b and q.other_b for q in questions)
    return{'sender_completed':sender_completed, 'receiver_completed':receiver_completed}
