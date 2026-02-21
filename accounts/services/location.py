import requests

def get_client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")

def detect_city_from_ip(ip: str):
    if not ip:
        return None
    try:
        r = requests.get(f"https://ipapi.co/{ip}/json/", timeout=5)
        if r.status_code != 200:
            return None
        data = r.json()
        return data.get("city")
    except requests.RequestException:
        return None