import hashlib
import base64
from .models import shortURL

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