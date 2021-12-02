from django import forms
from django.forms import ModelForm
from .models import Room

class RoomForm(ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    class Meta:
        model = Room
        fields = ('name',)