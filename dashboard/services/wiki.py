import requests

def get_wikipedia_summary(title: str):
    if not title:
        return None

    name = title.strip().replace(" ", "%20")
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{name}"

    try:
        r = requests.get(url, timeout=8)
    except requests.RequestException:
        return None

    if r.status_code != 200:
        return None

    return r.json()