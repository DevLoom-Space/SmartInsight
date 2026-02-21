import requests

class ForecastError(Exception):
    pass

def get_daily_forecast(lat: float, lon: float):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto",
    }

    try:
        r = requests.get(url, params=params, timeout=10)
    except requests.RequestException:
        raise ForecastError("Forecast service unavailable.")

    if r.status_code != 200:
        raise ForecastError("Forecast service failed.")

    data = r.json()
    daily = data.get("daily") or {}

    times = daily.get("time") or []
    tmax = daily.get("temperature_2m_max") or []
    tmin = daily.get("temperature_2m_min") or []
    precip = daily.get("precipitation_sum") or []

    days = []
    for i in range(min(len(times), len(tmax), len(tmin), len(precip))):
        days.append({
            "date": times[i],
            "max": tmax[i],
            "min": tmin[i],
            "precip": precip[i],
        })

    return days