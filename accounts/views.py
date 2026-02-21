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
            zodiac = form.cleaned_data.get("zodiac", "").strip().lower()

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