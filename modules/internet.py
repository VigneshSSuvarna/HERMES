import requests
import wikipedia

class HermesInternet:
    """Handles real-time data fetching from the live internet."""
    def __init__(self):
        print("[Internet]: Global Web Uplink Active.")

    def fetch_weather(self, location: str) -> str:
        """Fetches live weather data for a specific city."""
        target_city = location.strip() if location else "London"
        try:
            # wttr.in is a fast, free weather API
            url = f"https://wttr.in/{target_city}?format=%C+%t"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                weather_data = response.text.strip()
                return f"The current weather in {target_city} is {weather_data}."
            return f"Sir, I could not retrieve the weather for {target_city}."
        except Exception as e:
            return "Sir, the weather satellite uplink failed."

    def fetch_wiki(self, query: str) -> str:
        """Fetches a short factual summary from Wikipedia."""
        try:
            wikipedia.set_lang("en")
            # Get just the first 2 sentences for a crisp voice response
            summary = wikipedia.summary(query, sentences=2)
            return summary
        except wikipedia.exceptions.DisambiguationError as e:
            return f"Sir, there are multiple results for {query}. Please be more specific."
        except Exception:
            return f"Sir, I could not find any live databank records for {query}."