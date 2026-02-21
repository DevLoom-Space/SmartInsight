from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models

class SearchHistory(models.Model):
    TYPE_CHOICES = [
        ("weather", "Weather"),
        ("horoscope", "Horoscope"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    search_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    query = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]