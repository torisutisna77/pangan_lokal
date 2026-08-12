import requests
from config import OPENWEATHER_API_KEY

def get_weather(lat: float, lon: float):
    if not OPENWEATHER_API_KEY:
        return None
    try:
        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric&lang=id"
        )
        res = requests.get(url, timeout=8)
        if res.status_code == 200:
            data = res.json()
            return {
                "suhu": data["main"]["temp"],
                "terasa_seperti": data["main"]["feels_like"],
                "kelembaban": data["main"]["humidity"],
                "tekanan": data["main"]["pressure"],
                "cuaca": data["weather"][0]["description"].title(),
                "angin": data["wind"]["speed"],
            }
    except Exception:
        return None
    return None