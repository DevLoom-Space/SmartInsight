from django.urls import path
from .views import profile_settings, signup

urlpatterns = [
    path("signup/", signup, name="signup"),
    path("profile/", profile_settings, name="profile_settings"),
]