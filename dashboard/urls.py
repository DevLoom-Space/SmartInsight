from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard_home, name="dashboard_home"),
    path("weather/", views.weather_detail, name="weather_detail"),
    path("horoscope/", views.horoscope_detail, name="horoscope_detail"),
    path("quotes/", views.quote_detail, name="quote_detail"),
    path("quotes/save/", views.save_quote, name="save_quote"),

    path("history/clear/", views.clear_history, name="clear_history"),
]

