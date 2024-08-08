import hashlib
import base64
from .models import shortURL
from django.core.mail import send_mail
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


def SendEmail(request, receiver_email, room_id, sender):

    long_url = f"/{room_id}/"
    short_key = shorten_url(request, long_url) 
    short_url = f"{request.scheme}://{request.get_host()}/s/{short_key}"

    subject = 'New room created'
    message = f'Hi! {sender} has created a new room for you, please click the following link:  {short_url}'
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [receiver_email]
    
    send_mail(subject, message, email_from, recipient_list)
