from django_cron import CronJobBase, Schedule
from .models import Room
from datetime import datetime, timedelta

class DeleteOldRoom(CronJobBase):
    RUN_EVERY_MINS = 1440

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'app.delete_old_room'

    
    def do(self):
        limit_date = datetime.now() - timedelta(days=10)
        Room.objects.filter(last_modification__lt=limit_date).delete()