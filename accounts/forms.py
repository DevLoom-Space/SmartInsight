from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=False)
    birth_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )

    class Meta:
        model = User
        fields = ("username", "email", "birth_date", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # add bootstrap classes to default fields
        self.fields["username"].widget.attrs.update({"class": "form-control"})
        self.fields["email"].widget.attrs.update({"class": "form-control"})
        self.fields["password1"].widget.attrs.update({"class": "form-control"})
        self.fields["password2"].widget.attrs.update({"class": "form-control"})


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("city", "zodiac")
        widgets = {
            "city": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g., Nairobi"}
            ),
            "zodiac": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g., aries"}
            ),
        }