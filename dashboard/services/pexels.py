import requests
from django.conf import settings

class PexelsError(Exception):
    pass

def search_photos(query: str, per_page: int = 9):
    key = getattr(settings, "PEXELS_API_KEY", "")
    if not key:
        raise PexelsError("Missing PEXELS_API_KEY")

    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": key}
    params = {
        "query": query,
        "per_page": per_page,
        "orientation": "landscape",
        "size": "medium",
    }

    try:
        r = requests.get(url, headers=headers, params=params, timeout=12)
    except requests.RequestException:
        raise PexelsError("Image service unavailable.")

    if r.status_code != 200:
        raise PexelsError(f"Image service failed ({r.status_code}).")

    data = r.json()
    photos = data.get("photos") or []

    # return direct image urls (pick large)
    out = []
    for p in photos:
        src = (p.get("src") or {})
        if src.get("large"):
            out.append(src["large"])
        elif src.get("medium"):
            out.append(src["medium"])

    return out