from .models import Room, Question
from django.core.mail import EmailMessage
from django.conf import settings

def SendEmail(receiver_email, sender, subject=None, message=None):

    email_from = f'Room <no-reply@quiz.com>'
    recipient_list = [receiver_email]

    email = EmailMessage(
        subject,
        message,
        email_from,
        recipient_list,
        headers={'Reply-To': 'no-reply@quiz.com'},  # Cambia a la dirección que desees
    )
    email.send()


def check_completeness(room_id):
    
    try:
        Room.objects.get(id=room_id)
    except Room.DoesNotExist:
        return{'sender_completed':False, 'receiver_completed':False}

    questions=Question.objects.filter(room=room_id)
    sender_completed=all(q.self_a and q.other_a for q in questions)
    receiver_completed=all(q.self_b and q.other_b for q in questions)
    return{'sender_completed':sender_completed, 'receiver_completed':receiver_completed}
