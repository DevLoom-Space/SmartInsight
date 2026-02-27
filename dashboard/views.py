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
from .services.pexels import search_photos, PexelsError


ZODIAC_CHOICES = [
    "aries", "taurus", "gemini", "cancer", "leo", "virgo",
    "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces",
]

ZODIAC_TRAITS = {
    "aries": {"element": "Fire", "strengths": "Bold, driven", "focus": "Action"},
    "taurus": {"element": "Earth", "strengths": "Stable, loyal", "focus": "Consistency"},
    "gemini": {"element": "Air", "strengths": "Curious, quick-minded", "focus": "Communication"},
    "cancer": {"element": "Water", "strengths": "Intuitive, caring", "focus": "Home"},
    "leo": {"element": "Fire", "strengths": "Confident, warm", "focus": "Leadership"},
    "virgo": {"element": "Earth", "strengths": "Precise, practical", "focus": "Systems"},
    "libra": {"element": "Air", "strengths": "Balanced, diplomatic", "focus": "Harmony"},
    "scorpio": {"element": "Water", "strengths": "Intense, loyal", "focus": "Depth"},
    "sagittarius": {"element": "Fire", "strengths": "Optimistic, adventurous", "focus": "Growth"},
    "capricorn": {"element": "Earth", "strengths": "Disciplined, ambitious", "focus": "Results"},
    "aquarius": {"element": "Air", "strengths": "Independent, visionary", "focus": "Innovation"},
    "pisces": {"element": "Water", "strengths": "Empathic, creative", "focus": "Imagination"},
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

    city = (request.GET.get("city") or default_city).strip()
    zodiac = (request.GET.get("zodiac") or default_zodiac).strip().lower()

    # --- cache keys ---
    weather_key = f"weather:{city.lower()}"
    horoscope_key = f"horoscope:{zodiac}"
    quote_key = "quote:daily"

    # --- result containers ---
    weather_data, horoscope_data, quote_data = None, None, None
    weather_error, horoscope_error, quote_error = None, None, None

    # =========================
    # Weather (cache 10 min)
    # =========================
    weather_data = cache.get(weather_key)
    if weather_data is None:
        try:
            weather_data = get_weather(city)
            cache.set(weather_key, weather_data, timeout=10 * 60)
            SearchHistory.objects.create(user=request.user, search_type="weather", query=city)
        except APIError as e:
            weather_error = str(e)

    # ✅ Weather tip + weather mode (for hero animation)
    weather_tip = "Balanced weather. Perfect for steady progress today ✅"
    weather_mode = "mild"  # mild | sunny | cloudy | rainy
    is_rainy = False

    if weather_data:
        temp = weather_data.get("temp")
        cloud = weather_data.get("cloud_pct")
        humidity = weather_data.get("humidity")
        wind = weather_data.get("wind_speed")

        # detect rainy vibe
        if isinstance(cloud, (int, float)) and isinstance(humidity, (int, float)):
            is_rainy = cloud >= 80 and humidity >= 75

        if is_rainy:
            weather_mode = "rainy"
            weather_tip = "High chance of rain ☔ Carry an umbrella and avoid light shoes."
        elif isinstance(temp, (int, float)) and temp >= 27:
            weather_mode = "sunny"
            weather_tip = "Warm day ☀️ Drink water and take shade breaks."
        elif isinstance(cloud, (int, float)) and cloud >= 70:
            weather_mode = "cloudy"
            weather_tip = "Mostly cloudy ☁️ A light jacket might help."
        elif isinstance(temp, (int, float)) and temp <= 15:
            weather_mode = "mild"
            weather_tip = "Cool conditions 🧥 Wear layers and keep warm later."
        elif isinstance(wind, (int, float)) and wind >= 8:
            weather_mode = "mild"
            weather_tip = "Windy outside 🌬️ Secure loose items and wear a light jacket."

    # =========================
    # Horoscope (cache 6 hours)
    # =========================
    horoscope_data = cache.get(horoscope_key)
    if horoscope_data is None:
        try:
            horoscope_data = get_horoscope(zodiac)
            cache.set(horoscope_key, horoscope_data, timeout=6 * 60 * 60)
            SearchHistory.objects.create(user=request.user, search_type="horoscope", query=zodiac)
        except APIError as e:
            horoscope_error = str(e)

    # =========================
    # Quote (cache 1 hour)
    # =========================
    quote_data = cache.get(quote_key)
    if quote_data is None:
        try:
            quote_data = get_random_quote()
            cache.set(quote_key, quote_data, timeout=60 * 60)
        except APIError as e:
            quote_error = str(e)

    # =========================
    # Daily brief (rule-based)
    # =========================
    daily_brief = "Today is steady and balanced."

    if horoscope_data and weather_data:
        element = (ZODIAC_TRAITS.get(zodiac) or {}).get("element", "")
        temp = weather_data.get("temp")
        humidity = weather_data.get("humidity")
        cloud = weather_data.get("cloud_pct")

        mood_map = {
            "Fire": "Push forward with bold decisions.",
            "Water": "Trust intuition and stay emotionally aware.",
            "Air": "Communicate clearly and avoid assumptions.",
            "Earth": "Focus on structure and practical wins.",
        }
        mood = mood_map.get(element, "Stay balanced and composed.")

        weather_note = ""
        if isinstance(temp, (int, float)):
            if temp < 15:
                weather_note = "Cool weather suggests patience."
            elif temp > 30:
                weather_note = "High heat calls for measured action."
            else:
                weather_note = "Conditions are balanced today."

        if isinstance(cloud, (int, float)) and cloud >= 75:
            weather_note += " Cloud cover may slow momentum."

        humidity_note = ""
        if isinstance(humidity, (int, float)) and humidity > 70:
            humidity_note = " Energy may feel heavier than usual."

        daily_brief = f"{mood} {weather_note}{humidity_note}".strip()

    recent_searches = SearchHistory.objects.filter(user=request.user).order_by("-id")[:6]

    return render(request, "dashboard/home.html", {
        "city": city,
        "zodiac": zodiac,
        "zodiac_choices": ZODIAC_CHOICES,

        "weather_data": weather_data,
        "weather_error": weather_error,
        "weather_tip": weather_tip,
        "weather_mode": weather_mode,
        "is_rainy": is_rainy,

        "horoscope_data": horoscope_data,
        "horoscope_error": horoscope_error,

        "quote_data": quote_data,
        "quote_error": quote_error,

        "recent_searches": recent_searches,
        "daily_brief": daily_brief,
    })


@login_required
def weather_detail(request):
    city = (request.GET.get("city") or "Nairobi").strip()

    weather, weather_error = None, None
    trend, trend_error = [], None

    # Weather + forecast
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

    except APIError as e:
        weather_error = str(e)

    # Weather mode for the page (optional use)
    weather_mode = "mild"
    if weather:
        temp = weather.get("temp")
        cloud = weather.get("cloud_pct")
        humidity = weather.get("humidity")

        if isinstance(cloud, (int, float)) and isinstance(humidity, (int, float)) and cloud >= 80 and humidity >= 75:
            weather_mode = "rainy"
        elif isinstance(temp, (int, float)) and temp >= 27:
            weather_mode = "sunny"
        elif isinstance(cloud, (int, float)) and cloud >= 70:
            weather_mode = "cloudy"

    # Pexels images (cached) — safe fallback
    photos, photos_error = [], None
    photo_cache_key = f"pexels:weather:{city.lower()}"
    cached = cache.get(photo_cache_key)

    if cached is not None:
        photos = cached
    else:
        try:
            raw = []
            raw += search_photos(f"{city} city skyline", per_page=4)
            raw += search_photos(f"{city} street road", per_page=4)
            raw += search_photos(f"{city} landscape", per_page=4)

            seen = set()
            unique = []
            for u in raw:
                if u and u not in seen:
                    unique.append(u)
                    seen.add(u)

            photos = unique[:9]
            cache.set(photo_cache_key, photos, timeout=6 * 60 * 60)

        except PexelsError as e:
            photos_error = str(e)
        except Exception:
            photos_error = "Image service unavailable."

    labels = [d["date"] for d in trend]
    max_t = [d["max"] for d in trend]
    min_t = [d["min"] for d in trend]
    precip = [d["precip"] for d in trend]

    return render(request, "dashboard/weather_detail.html", {
        "city": city,
        "weather": weather,
        "weather_error": weather_error,

        "trend_error": trend_error,
        "trend": trend,

        "photos": photos,
        "photos_error": photos_error,

        "chart_labels": labels,
        "chart_max": max_t,
        "chart_min": min_t,
        "chart_precip": precip,

        "weather_mode": weather_mode,
    })


@login_required
def horoscope_detail(request):
    zodiac = (request.GET.get("zodiac") or "aries").strip().lower()

    data, error = None, None
    traits = ZODIAC_TRAITS.get(zodiac)

    # Photos via Pexels (cached)
    photos, photos_error = [], None
    photo_cache_key = f"pexels:horoscope:{zodiac}"
    cached = cache.get(photo_cache_key)

    if cached is not None:
        photos = cached
    else:
        try:
            raw = []
            raw += search_photos(f"{zodiac} constellation night sky", per_page=4)
            raw += search_photos("moon night sky stars", per_page=3)
            raw += search_photos("astrology illustration zodiac", per_page=3)

            seen = set()
            unique = []
            for u in raw:
                if u and u not in seen:
                    unique.append(u)
                    seen.add(u)

            photos = unique[:9]
            cache.set(photo_cache_key, photos, timeout=6 * 60 * 60)

        except PexelsError as e:
            photos_error = str(e)
        except Exception:
            photos_error = "Image service unavailable."

    # Horoscope content
    try:
        data = get_horoscope(zodiac)
    except APIError as e:
        error = str(e)

    spotlight = None
    if traits:
        spotlight = {
            "element": traits.get("element"),
            "strengths": traits.get("strengths"),
            "focus": traits.get("focus"),
        }

    zodiac_element = (traits.get("element", "Air") if traits else "Air").lower()

    return render(request, "dashboard/horoscope_detail.html", {
        "zodiac": zodiac,
        "data": data,
        "error": error,
        "traits": traits,
        "spotlight": spotlight,
        "photos": photos,
        "photos_error": photos_error,
        "zodiac_element": zodiac_element,
    })


@login_required
def quote_detail(request):
    category = request.GET.get("category", "").strip()

    data, error = None, None
    author_info = None
    photos, photos_error = [], None

    try:
        data = get_random_quote(category=category if category else None)

        QuoteHistory.objects.create(
            user=request.user,
            quote=data.get("quote", ""),
            author=data.get("author", ""),
            category=data.get("category", ""),
        )

        if data and data.get("author"):
            author = data["author"]
            author_info = get_wikipedia_summary(author)

            cache_key = f"pexels:author:{author.lower()}"
            cached = cache.get(cache_key)

            if cached:
                photos = cached
            else:
                raw = search_photos(f"{author} portrait", per_page=6)
                photos = raw[:6]
                cache.set(cache_key, photos, timeout=6 * 60 * 60)

    except APIError as e:
        error = str(e)
    except PexelsError:
        photos_error = "Image service unavailable."

    recent = QuoteHistory.objects.filter(user=request.user).order_by("-id")[:8]

    return render(request, "dashboard/quote_detail.html", {
        "data": data,
        "error": error,
        "category": category,
        "recent": recent,
        "author_info": author_info,
        "photos": photos,
        "photos_error": photos_error,
    })


@login_required
@require_POST
def save_quote(request):
    quote = (request.POST.get("quote") or "").strip()
    author = (request.POST.get("author") or "").strip()
    category = (request.POST.get("category") or "").strip()

    if not quote:
        messages.error(request, "Nothing to save.")
        return redirect("quote_detail")

    QuoteFavorite.objects.get_or_create(
        user=request.user,
        quote=quote,
        author=author,
        category=category,
    )

    messages.success(request, "Saved to favorites.")
    return redirect("favorites_home")