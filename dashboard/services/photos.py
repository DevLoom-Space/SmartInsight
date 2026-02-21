import requests

def get_city_photos(city: str, limit: int = 6):
    """
    Fetches photo thumbnails for a city using Wikipedia page images.
    Returns a list of image URLs.
    """
    city = (city or "").strip()
    if not city:
        return []

    # Wikipedia API: get page images
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": city,
        "prop": "pageimages",
        "pithumbsize": 900,
        "pilimit": limit,
        "redirects": 1,
    }

    try:
        r = requests.get(url, params=params, timeout=8)
        if r.status_code != 200:
            return []
        data = r.json()
    except requests.RequestException:
        return []

    pages = (data.get("query") or {}).get("pages") or {}
    for _, page in pages.items():
        # if page exists and has thumbnail
        thumb = page.get("thumbnail", {}).get("source")
        if thumb:
            # return 1 image from the main city page
            # (we'll combine with Commons below)
            return [thumb]

    return []


def get_commons_photos(query: str, limit: int = 6):
    q = (query or "").strip()
    if not q:
        return []

    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": f"{q} city",
        "gsrlimit": limit,
        "prop": "imageinfo",
        "iiprop": "url",
        "iiurlwidth": 1200,
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code != 200:
            return []
        data = r.json()
    except requests.RequestException:
        return []

    pages = (data.get("query") or {}).get("pages") or {}
    urls = []
    for _, p in pages.items():
        info = (p.get("imageinfo") or [])
        if info:
            u = info[0].get("thumburl") or info[0].get("url")
            if u:
                urls.append(u)

    # remove duplicates and return
    seen = set()
    out = []
    for u in urls:
        if u not in seen:
            out.append(u)
            seen.add(u)
    return out[:limit]