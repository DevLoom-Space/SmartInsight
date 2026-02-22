from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import ProfileUpdateForm

from .forms import SignUpForm
from .services.location import get_client_ip, detect_city_from_ip

def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard_home")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()

            birth_date = form.cleaned_data.get("birth_date")

            # Calculate zodiac automatically
            zodiac = zodiac_from_date(birth_date.month, birth_date.day)

            ip = get_client_ip(request)
            detected_city = detect_city_from_ip(ip) or "Nairobi"

            profile = user.profile
            profile.zodiac = zodiac
            profile.city = detected_city
            profile.save()

            login(request, user)
            messages.success(request, "Account created successfully.")
            return redirect("dashboard_home")
    else:
        form = SignUpForm()

    return render(request, "accounts/signup.html", {"form": form})




@login_required
def profile_settings(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("dashboard_home")
    else:
        form = ProfileUpdateForm(instance=profile)

    return render(request, "accounts/profile.html", {"form": form})


def zodiac_from_date(month, day):
    if (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "aries"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "taurus"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        return "gemini"
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        return "cancer"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "leo"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "virgo"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "libra"
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return "scorpio"
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
        return "sagittarius"
    elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
        return "capricorn"
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "aquarius"
    elif (month == 2 and day >= 19) or (month == 3 and day <= 20):
        return "pisces"
    return "aries"