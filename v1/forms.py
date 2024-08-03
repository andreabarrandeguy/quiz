from pyexpat import model
from attr import fields
from django import forms
from v1.models import TemporaryQuestion, Room

class NewRoomForm(forms.ModelForm):
    user_name=forms.CharField(max_length=255, label=False, widget=forms.TextInput(attrs={
        'placeholder':'Your name',
        'class': 'inputNames_field'}))
    other_person_name=forms.CharField(max_length=255, label=False, widget=forms.TextInput(attrs={
        'placeholder':'Who will receive this?',
        'class': 'inputNames_field'}))
    sender_email=forms.EmailField(max_length=255, label=False, widget=forms.EmailInput(attrs={
        'placeholder':'Your mail',
        'class': 'inputNames_field'}))
    receiver_email=forms.EmailField(max_length=255, label=False, widget=forms.EmailInput(attrs={
        'placeholder':'Receiver mail',
        'class': 'inputNames_field'}))
    class Meta:
        model=Room
        fields=['user_name', 'other_person_name', 'sender_email', 'receiver_email']


class NewQuestionForm(forms.ModelForm):
    question = forms.CharField(
        label=False,
        required=False,
        max_length=255,
        widget=forms.TextInput(
            attrs={
                'class': 'question-input',
                'placeholder': 'e.g. A weakness'
            }
        )
    )

    class Meta:
        model=TemporaryQuestion
        fields=['question']
