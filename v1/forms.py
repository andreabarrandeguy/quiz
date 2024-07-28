from pyexpat import model
from attr import fields
from django import forms
from v1.models import TemporaryQuestion, Room

class NewRoomForm(forms.ModelForm):
    user_name=forms.CharField(max_length=255, label=False, widget=forms.TextInput({"placeholder":"Your name"}))
    other_person_name=forms.CharField(max_length=255, label=False, widget=forms.TextInput({"placeholder":"Receiver"}))

    class Meta:
        model=Room
        fields=['user_name', 'other_person_name']


class NewQuestionForm(forms.ModelForm):
    question=forms.CharField(label=False, required=False, max_length=255, widget=forms.TextInput({"placeholder":"e.g. A weakeness"}))

    class Meta:
        model=TemporaryQuestion
        fields=['question']
