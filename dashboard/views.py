from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from accounts.models import Profile
from favorites.models import QuoteFavorite, QuoteHistory
from .models import SearchHistory
from .services.apininjas import (
    APIError,
    get_weather,
    get_horoscope,
    get_random_quote,
    geocode_city,
)
from .services.openmeteo import get_daily_forecast, ForecastError
from .services.wiki import get_wikipedia_summary
from .services.photos import get_city_photos, get_commons_photos
from .services.pexels import search_photos, PexelsError

ZODIAC_CHOICES = [
    "aries",
    "taurus",
    "gemini",
    "cancer",
    "leo",
    "virgo",
    "libra",
    "scorpio",
    "sagittarius",
    "capricorn",
    "aquarius",
    "pisces",
]

ZODIAC_TRAITS = {
    "aries": {"element": "Fire", "strengths": "Bold, driven", "focus": "Action"},
    "taurus": {
        "element": "Earth",
        "strengths": "Stable, loyal",
        "focus": "Consistency",
    },
    "gemini": {
        "element": "Air",
        "strengths": "Curious, quick-minded",
        "focus": "Communication",
    },
    "cancer": {"element": "Water", "strengths": "Intuitive, caring", "focus": "Home"},
    "leo": {"element": "Fire", "strengths": "Confident, warm", "focus": "Leadership"},
    "virgo": {
        "element": "Earth",
        "strengths": "Precise, practical",
        "focus": "Systems",
    },
    "libra": {
        "element": "Air",
        "strengths": "Balanced, diplomatic",
        "focus": "Harmony",
    },
    "scorpio": {"element": "Water", "strengths": "Intense, loyal", "focus": "Depth"},
    "sagittarius": {
        "element": "Fire",
        "strengths": "Optimistic, adventurous",
        "focus": "Growth",
    },
    "capricorn": {
        "element": "Earth",
        "strengths": "Disciplined, ambitious",
        "focus": "Results",
    },
    "aquarius": {
        "element": "Air",
        "strengths": "Independent, visionary",
        "focus": "Innovation",
    },
    "pisces": {
        "element": "Water",
        "strengths": "Empathic, creative",
        "focus": "Imagination",
    },
}


@login_required
@require_POST
def clear_history(request):
    SearchHistory.objects.filter(user=request.user).delete()
    messages.success(request, "History cleared.")
    return redirect("dashboard_home")


@login_required
def dashboard_home(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    default_city = profile.city or "Nairobi"
    default_zodiac = profile.zodiac or "aries"

    city = request.GET.get("city", default_city)
    zodiac = request.GET.get("zodiac", default_zodiac)

    weather_data, horoscope_data, quote_data = None, None, None
    weather_error, horoscope_error, quote_error = None, None, None

    weather_key = f"weather_{city.lower().strip()}"
    horoscope_key = f"horoscope_{zodiac.lower().strip()}"
    quote_key = "quote:daily"

    weather_data = cache.get(weather_key)
    if weather_data is None:
        try:
            weather_data = get_weather(city)
            cache.set(weather_key, weather_data, timeout=10 * 60)
            SearchHistory.objects.create(
                user=request.user, search_type="weather", query=city
            )
        except APIError as e:
            weather_error = str(e)

    horoscope_data = cache.get(horoscope_key)
    if horoscope_data is None:
        try:
            horoscope_data = get_horoscope(zodiac)
            cache.set(horoscope_key, horoscope_data, timeout=6 * 60 * 60)
            SearchHistory.objects.create(
                user=request.user, search_type="horoscope", query=zodiac
            )
        except APIError as e:
            horoscope_error = str(e)

    quote_data = cache.get(quote_key)
    if quote_data is None:
        try:
            quote_data = get_random_quote()
            cache.set(quote_key, quote_data, timeout=60 * 60)
        except APIError as e:
            quote_error = str(e)

    recent_searches = SearchHistory.objects.filter(user=request.user)[:6]

    return render(
        request,
        "dashboard/home.html",
        {
            "city": city,
            "zodiac": zodiac,
            "zodiac_choices": ZODIAC_CHOICES,
            "weather_data": weather_data,
            "weather_error": weather_error,
            "horoscope_data": horoscope_data,
            "horoscope_error": horoscope_error,
            "quote_data": quote_data,
            "quote_error": quote_error,
            "recent_searches": recent_searches,
        },
    )


@login_required
def weather_detail(request):
    city = request.GET.get("city", "Nairobi").strip()

    weather, weather_error = None, None
    trend, trend_error = [], None
    photos = []

    try:
        weather = get_weather(city)

        place = geocode_city(city)
        lat = place.get("latitude")
        lon = place.get("longitude")

        if lat is not None and lon is not None:
            try:
                trend = get_daily_forecast(lat, lon)
            except ForecastError as e:
                trend_error = str(e)

        q = city.replace(" ", "+")
        photos = get_city_photos(city, limit=1) + get_commons_photos(city, limit=6)
        photos = photos[:6]  # limit total photos to 6
    except APIError as e:
        weather_error = str(e)

    labels = [d["date"] for d in trend]
    max_t = [d["max"] for d in trend]
    min_t = [d["min"] for d in trend]
    precip = [d["precip"] for d in trend]

    return render(
        request,
        "dashboard/weather_detail.html",
        {
            "city": city,
            "weather": weather,
            "weather_error": weather_error,
            "trend_error": trend_error,
            "trend": trend,
            "photos": photos,
            "chart_labels": labels,
            "chart_max": max_t,
            "chart_min": min_t,
            "chart_precip": precip,
        },
    )


@login_required
def horoscope_detail(request):
    zodiac = request.GET.get("zodiac", "aries").strip().lower()

    data, error = None, None
    traits = ZODIAC_TRAITS.get(zodiac)

    photos = [
        f"https://source.unsplash.com/featured/?{zodiac},constellation",
        "https://source.unsplash.com/featured/?moon,night-sky",
        "https://source.unsplash.com/featured/?astrology,illustration",
    ]

    try:
        data = get_horoscope(zodiac)
    except APIError as e:
        error = str(e)

    return render(
        request,
        "dashboard/horoscope_detail.html",
        {
            "zodiac": zodiac,
            "data": data,
            "error": error,
            "traits": traits,
            "photos": photos,
        },
    )


@login_required
def quote_detail(request):
    category = request.GET.get("category", "")
    data, error = None, None
    author_info = None

    try:
        data = get_random_quote(category=category if category else None)

        QuoteHistory.objects.create(
            user=request.user,
            quote=data.get("quote", ""),
            author=data.get("author", ""),
            category=data.get("category", ""),
        )

        if data and data.get("author"):
            author_info = get_wikipedia_summary(data["author"])

    except APIError as e:
        error = str(e)

    recent = QuoteHistory.objects.filter(user=request.user)[:8]

    return render(
        request,
        "dashboard/quote_detail.html",
        {
            "data": data,
            "error": error,
            "category": category,
            "recent": recent,
            "author_info": author_info,
        },
    )


@login_required
@require_POST
def save_quote(request):
    quote = request.POST.get("quote", "")
    author = request.POST.get("author", "")
    category = request.POST.get("category", "")

    if not quote.strip():
        messages.error(request, "Nothing to save.")
        return redirect("quote_detail")

    QuoteFavorite.objects.get_or_create(
        user=request.user,
        quote=quote.strip(),
        author=(author or "").strip(),
        category=(category or "").strip(),
    )

    messages.success(request, "Saved to favorites.")
    return redirect("favorites_home")
