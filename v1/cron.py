import logging
from django.forms import ValidationError
from django_cron import CronJobBase, Schedule

from quiz2.settings import EMAIL_HOST_USER

from .utils import SendEmail
from .models import Room
from datetime import date, datetime, timedelta

class DeleteOldRoom(CronJobBase):
    RUN_EVERY_MINS = 1440

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'app.delete_old_room'

    
    def do(self):
        limit_date = datetime.now() - timedelta(days=10)
        Room.objects.filter(last_modification__lt=limit_date).delete()

class SendReminderDeletion(CronJobBase):
    RUN_EVERY_MINS = 1440
    
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'app.send_reminder_deletion'

    def do(self):
        logging.info('Ejecutando SendReminderDeletion')
        reminder = date.today() - timedelta(days=8)
        rooms = Room.objects.filter(last_modification__lt=reminder)
        logging.info(f'Se encontraron {rooms.count()} rooms para enviar recordatorio.')

        for room in rooms:
            try:
                logging.info(f'Enviando recordatorio a {room.sender_email} y a {room.receiver_email} para el room {room.id}')
                subject = 'Deletion reminder'
                message = f'This is a reminder that in 48 hours, the room ({room.id}) will be deleted due to inactivity.'
                
                # Intenta enviar el primer correo
                try:
                    SendEmail(room.receiver_email, EMAIL_HOST_USER, subject, message)
                except (ValidationError, Exception) as e:
                    logging.error(f'Error al enviar el recordatorio al receiver ({room.receiver_email}) para el room {room.id}: {e}')
                
                # Intenta enviar el segundo correo
                try:
                    SendEmail(room.sender_email, EMAIL_HOST_USER, subject, message)
                except (ValidationError, Exception) as e:
                    logging.error(f'Error al enviar el recordatorio al sender ({room.sender_email}) para el room {room.id}: {e}')
                
                logging.info(f'Recordatorios enviados para el room {room.id}')

            except Exception as e:
                logging.error(f'Error general en el proceso de envío de recordatorios para el room {room.id}: {e}')
