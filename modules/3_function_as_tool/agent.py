from google.adk.agents import Agent

from dotenv import load_dotenv
load_dotenv()

def get_weather(city: str) -> dict:
    """
    Retrieves the current weather report for a specified city.
    
    Args:
       city: The name of the city to get the weather for.
    
    Returns:
       A dictionary containing weather status and temparature.
    """
    mock_data = {
        "new york": {"status": "success", "report": "Sunny, 22°C. Light breeze from the west"},
        "london": {"status": "success", "report": "Cloudy, 15°C. Chance of rain in the evening"},
        "tokyo": {"status": "success", "report": "Clear skies 20°C. Humidity at 45%"},
        "paris": {"status": "success", "report": "Partly cloudy 18°C. Pleasant conditions"},
        "sydney": {"status": "success", "report": "Warm 28°C. UV index is high"}
    }
    
    city_lower = city.lower().strip()
    if city_lower in mock_data:
        return mock_data[city_lower]
    
    return {"status": "error", "message": f"Weather data not available for '{city}'."}


def get_temparature_unit_conversion(celsius: float) -> dict:
    """
    Converts a temparature from Celsius to Fahrenheit and Kelvin
    
    Args:
      celsius: The temparature in Celsisu to convert
      
    Returns:
      A dictionary with temperature in Fahrenheit and Kelvin  
    """
    fahrenheit = (celsius * 9 / 5) + 32
    kelvin = celsius + 273.15
    return {
        "celsius": celsius,
        "fahrenheit": round(fahrenheit, 2),
        "kelvin": round(kelvin, 2)
    }
    

root_agent = Agent(
    name="weather_agent",
    model="openai/gpt-4o-mini",
    description="A weather assistant that can check weather and also convert temparatures to fahrenheit and kelvin",
    instruction="You are a helpful weather assistant. Always provide clear and friendly responses",
    tools=[get_weather, get_temparature_unit_conversion]
)