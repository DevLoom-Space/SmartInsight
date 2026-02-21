import requests
from django.conf import settings

BASE_URL = "https://api.api-ninjas.com"

class APIError(Exception):
    pass

def _get(path: str, params: dict | None = None):
    if not settings.API_NINJAS_KEY:
        raise APIError("Missing API_NINJAS_KEY")

    url = f"{BASE_URL}{path}"
    headers = {"X-Api-Key": settings.API_NINJAS_KEY}

    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
    except requests.RequestException:
        raise APIError("Network error. Try again.")

    if r.status_code != 200:
        # show real reason in terminal
        body = r.text[:300] if r.text else ""
        print(f"[API Ninjas] {r.status_code} {url} params={params} body={body}")
        raise APIError("API request failed. Try again later.")

    return r.json()
    
    
    
def get_weather(city: str):
    place = geocode_city(city)
    lat = place.get("latitude")
    lon = place.get("longitude")

    if lat is None or lon is None:
        raise APIError("Could not resolve location.")

    return _get("/v1/weather", {"lat": lat, "lon": lon})


def get_horoscope(zodiac: str):
    zodiac = (zodiac or "").strip().lower()
    if not zodiac:
        raise APIError("Zodiac sign is required.")
    return _get("/v1/horoscope", {"zodiac": zodiac})



def geocode_city(city: str):
    city = (city or "").strip()
    if not city:
        raise APIError("City is required.")
    data = _get("/v1/geocoding", {"city": city})
    if not data:
        raise APIError("City not found.")
    return data[0]  # best match


def get_random_quote(category: str | None = None):
    params = {}
    if category:
        params["category"] = category.strip().lower()
    data = _get("/v1/quotes", params)
    if not data:
            raise APIError("No quotes found for this category.")    
    return data[0]