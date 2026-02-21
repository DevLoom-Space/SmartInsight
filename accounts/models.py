

# Create your models here.
from django.conf import settings
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    zodiac = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=120, blank=True, default="Nairobi")

    def __str__(self):
        return f"{self.user.username} Profile"