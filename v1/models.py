from django.db import models
import uuid


class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_name = models.CharField(max_length=100) # SENDER/Creator of form
    other_person_name = models.CharField(max_length=100) #RECEIVER of form
    sender_email = models.EmailField(default='1234@gmail.com')
    receiver_email = models.EmailField(default='1234@gmail.com')
    last_modification = models.DateField(auto_now=True)

class Question(models.Model):
    question_id = models.AutoField(primary_key=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE) # Links to "id" from Room above
    question = models.CharField(max_length=255)
    self_a = models.CharField(max_length=255, null=True, blank=True) # SENDER about themselves
    self_b = models.CharField(max_length=255, null=True, blank=True) # RECEIVER about themselves
    other_a = models.CharField(max_length=255, null=True, blank=True) # SENDER about RECEIVER
    other_b = models.CharField(max_length=255, null=True, blank=True) # RECEIVER about SENDER
