from io import open_code
from django import forms
from django.core import validators
from django.forms import fields, widgets
from django.forms.forms import Form
from django.contrib.auth.models import User

from django import forms    # New
# from .models import UserProfile # New



class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

# Define the Form , now needs its own View
class JoinForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete':'new-password'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'size':'30'}))
    class Meta():
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password')
        help_texts = {  # To Turn off AutoComplete in Form
            'username': None
        }


