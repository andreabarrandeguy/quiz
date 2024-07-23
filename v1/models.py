from django.db import models
import uuid

class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_name = models.CharField(max_length=100)
    other_person_name = models.CharField(max_length=100)

class Question(models.Model):
    question_id = models.AutoField(primary_key=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    user_name_reply = models.CharField(max_length=255, null=True, blank=True)
    other_person_name_reply = models.CharField(max_length=255, null=True, blank=True)
