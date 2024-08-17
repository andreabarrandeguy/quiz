import hashlib
import base64
from .models import shortURL, Room, Question
from django.core.mail import send_mail, EmailMessage
from django.conf import settings

def shorten_url(request, long_url):
    
    host = request.get_host()
    if host in long_url:
        # Obtener solo el path de la URL larga
        path = long_url.split(host, 1)[-1]  # Obtiene el path después del host
    else:
        path = long_url  # Asumimos que long_url ya es un path relativo

    hash_object=hashlib.sha256(path.encode())
    base64_enconded=base64.urlsafe_b64encode(hash_object.digest())
    short_url=base64_enconded[:8].decode('utf-8')

    short_url_instance, created = shortURL.objects.get_or_create(
        short_url=short_url,
        defaults={'long_url':long_url}
    )

    return short_url_instance.short_url


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
    
    #send_mail(subject, message, email_from, recipient_list, headers={'Reply-To':'no-reply@quiz.com'})


def check_completeness(room_id):
    
    try:
        Room.objects.get(id=room_id)
    except Room.DoesNotExist:
        return{'sender_completed':False, 'receiver_completed':False}

    questions=Question.objects.filter(room=room_id)
    sender_completed=all(q.self_a and q.other_a for q in questions)
    receiver_completed=all(q.self_b and q.other_b for q in questions)
    return{'sender_completed':sender_completed, 'receiver_completed':receiver_completed}
