import os
import requests
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
NEWS_API_KEY = os.getenv("NEWSAPI_KEY")


class VerificationAgent:
    def __init__(self):
        self.weather_key = WEATHER_API_KEY
        self.news_key = NEWS_API_KEY

    def get_weather(self, city):
        """Fetch current weather for a city."""
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"q": city, "appid": self.weather_key, "units": "metric"}
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return {
                "condition": data["weather"][0]["main"],
                "description": data["weather"][0]["description"],
                "temp_c": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "rain_last_hour_mm": data.get("rain", {}).get("1h", 0)
            }
        except Exception as e:
            return {"error": str(e)}

    def get_recent_news(self, query, max_results=5):
        """Search recent news related to a query (e.g. 'landslide Pakistan')."""
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "sortBy": "publishedAt",
            "language": "en",
            "pageSize": max_results,
            "apiKey": self.news_key
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            articles = [
                {"title": a["title"], "source": a["source"]["name"], "publishedAt": a["publishedAt"]}
                for a in data.get("articles", [])
            ]
            return articles
        except Exception as e:
            return {"error": str(e)}

    def verify(self, detection_type, city):
        """
        Cross-check a detection against weather + news.
        detection_type: 'fire' or 'landslide'
        Returns a verification summary with a simple plausibility flag.
        """
        weather = self.get_weather(city)
        news = self.get_recent_news(f"{detection_type} {city}")

        plausible = True
        reasons = []

        if detection_type == "fire" and "error" not in weather:
            if weather["humidity"] > 80 or weather["rain_last_hour_mm"] > 0:
                plausible = False
                reasons.append("High humidity/rain makes fire less likely")

        if detection_type == "landslide" and "error" not in weather:
            if weather["rain_last_hour_mm"] == 0 and weather["condition"] not in ["Rain", "Thunderstorm"]:
                plausible = False
                reasons.append("No recent rain detected — landslide risk factor absent, verify manually")

        news_supports = isinstance(news, list) and len(news) > 0
        if news_supports:
            reasons.append(f"Found {len(news)} recent news article(s) mentioning {detection_type} near {city}")

        return {
            "detection_type": detection_type,
            "city": city,
            "weather": weather,
            "news": news,
            "plausible": plausible,
            "reasons": reasons
        }


if __name__ == "__main__":
    agent = VerificationAgent()
    result = agent.verify(detection_type="fire", city="Rawalpindi")
    print("Verification Report:")
    print(result)