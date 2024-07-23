from django.db import models
import uuid

class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_name = models.CharField(max_length=100)
    other_person_name = models.CharField(max_length=100)

class Question(models.Model):
    question_id = models.AutoField(primary_key=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    question = models.CharField(max_length=255)
    self_a = models.CharField(max_length=255, null=True, blank=True) 
    self_b = models.CharField(max_length=255, null=True, blank=True)
    other_a = models.CharField(max_length=255, null=True, blank=True)
    other_b = models.CharField(max_length=255, null=True, blank=True)
