from django import forms
from .models import *

class ContactForm(forms.Form):
    model = contacted_user
    fields = '__all__'