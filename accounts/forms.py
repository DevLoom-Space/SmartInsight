from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Profile


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=False)
    zodiac = forms.CharField(required=True, max_length=20)

    class Meta:
        model = User
        fields = ("username", "email", "zodiac", "password1", "password2")
        
        

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("city", "zodiac")
        widgets = {
            "city": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., Nairobi"}),
            "zodiac": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., aries"}),
        }        