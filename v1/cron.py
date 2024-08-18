import logging
from django.forms import ValidationError
from django_cron import CronJobBase, Schedule

from quiz2.settings import EMAIL_HOST_USER

from .utils import SendEmail, check_completeness
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
        subject = f'Deletion reminder'

        for room in rooms:
            completeness = check_completeness(room.id)
            if completeness['sender_completed'] and completeness['receiver_completed']:
                message_sender = f'This room ({room.id}) will be deleted in 48 hours. Thanks for playing.'
                message_receiver = f'This room ({room.id}) will be deleted in 48 hours. Thanks for playing.'
            elif completeness['sender_completed'] and not completeness['receiver_completed']:
                message_sender = f'The room with room id {room.id} you have with {room.other_person_name} will be deleted in 48 hours due inactivity. ' 
                message_receiver = f'The room created by {room.user_name} to share with you, is close to be deleted due inactivity. Only your answers are missing. Hurry up!'
            elif completeness['receiver_completed'] and not completeness['sender_completed']:
                message_sender= f'The room with id {room.id} you created is close to be deleted. {room.other_person_name} has already replied and waiting for your answers. Hurry up!'
                message_receiver = f'Unfortunately, {room.user_name} hasnt yet replied, and the room {room.id} is close to be deleted due inactivity. '
            elif not completeness['sender_completed'] and not completeness['receiver_completed']:
                message_sender=f'The room you created with id {room.id} will deleted due inactivity.  '
                message_receiver= f'The room {room.user_name} created and shared with you, will be deleted due inactivity.'
            try:
                logging.info(f'Enviando recordatorio a {room.sender_email} y a {room.receiver_email} para el room {room.id}')
                
                try:
                    SendEmail(room.receiver_email, EMAIL_HOST_USER, subject, message_receiver)
                except (ValidationError, Exception) as e:
                    logging.error(f'Error al enviar el recordatorio al receiver ({room.receiver_email}) para el room {room.id}: {e}')
                
                # Intenta enviar el segundo correo
                try:
                    SendEmail(room.sender_email, EMAIL_HOST_USER, subject, message_sender)
                except (ValidationError, Exception) as e:
                    logging.error(f'Error al enviar el recordatorio al sender ({room.sender_email}) para el room {room.id}: {e}')
                
                logging.info(f'Recordatorios enviados para el room {room.id}')

            except Exception as e:
                logging.error(f'Error general en el proceso de envío de recordatorios para el room {room.id}: {e}')
