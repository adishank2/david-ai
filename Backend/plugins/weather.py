"""Weather plugin example for David AI Assistant."""

from plugins.base import BasePlugin
from typing import Dict, List
import requests
from core.logger import get_logger

logger = get_logger(__name__)

class WeatherPlugin(BasePlugin):
    """Get weather information."""
    
    def get_intents(self) -> List[str]:
        return ["weather", "forecast"]
    
    def get_description(self) -> str:
        return "Get current weather and forecast information"
    
    def get_prompt_examples(self) -> str:
        return """weather:
{
  "intent": "weather",
  "location": "city name" (optional, defaults to user location)
}

forecast:
{
  "intent": "forecast",
  "location": "city name" (optional),
  "days": 3 (optional, 1-7 days)
}"""
    
    def execute(self, intent: Dict) -> str:
        """Execute weather query."""
        intent_type = intent.get("intent")
        location = intent.get("location", "auto")
        
        try:
            if intent_type == "weather":
                return self._get_current_weather(location)
            elif intent_type == "forecast":
                days = intent.get("days", 3)
                return self._get_forecast(location, days)
            else:
                return "Unknown weather command."
                
        except Exception as e:
            logger.error(f"Weather plugin error: {e}")
            return "Sorry, I couldn't get the weather information."
    
    def _get_current_weather(self, location: str) -> str:
        """Get current weather (using free API)."""
        try:
            # Using wttr.in - free weather API
            url = f"https://wttr.in/{location}?format=%C+%t+%h+%w"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                weather_data = response.text.strip()
                return f"Current weather: {weather_data}"
            else:
                return "Couldn't fetch weather data."
                
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            return "Weather service unavailable."
    
    def _get_forecast(self, location: str, days: int) -> str:
        """Get weather forecast."""
        try:
            # Using wttr.in for forecast
            url = f"https://wttr.in/{location}?format=%C+%t+%h+%w&days={days}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                return f"Weather forecast: {response.text.strip()}"
            else:
                return "Couldn't fetch forecast data."
                
        except Exception as e:
            logger.error(f"Forecast API error: {e}")
            return "Forecast service unavailable."
