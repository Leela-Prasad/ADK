from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.tools.base_tool import BaseTool
from google.adk.tools import ToolContext
from google.adk.runners import Runner
from google.genai import types
from typing import Optional, Dict, Any
import asyncio

from dotenv import load_dotenv
load_dotenv()

tool_call_log = []
tool_results_log = []

BLOCKED_CITIES = ["paris", "moscow"]


def get_weather(city: str) -> dict:
    """Gets the current weather for a city
    
    Args:
      city: The city name to check weather for
      
    Returns:
      A dictionary with weather information
    """
    
    weather_data = {
        "new york": {"temp": "22°C", "condition": "Sunny", "humidity": "45%"},
        "london": {"temp": "15°C", "condition": "Cloudy", "humidity": "78%"},
        "tokyo": {"temp": "28°C", "condition": "Clear", "humidity": "60%"},
        "paris": {"temp": "18°C", "condition": "Rainy", "humidity": "85%"},
        "sydney": {"temp": "25°C", "condition": "Partly Cloudy", "humidity": "55%"},
    }
    
    city_lower = city.lower()
    if city_lower in weather_data:
        return {"status": "success", "city": city, **weather_data[city_lower]}
    
    return {"status": "error", "message": f"No weather data for '{city}'"}


def get_stock_price(symbol: str) -> dict:
    """Gets the current stock price for a ticker symbol
    
    Args:
      symbol: The stock ticker symbol (e.g., AAPL, GOOGL)
      
    Returns:
      A dictionary with stock price information
    """
    
    stock_data = {
        "AAPL": {"price": 189.50, "change": "+1.2%"},
        "GOOGL": {"price": 141.80, "change": "-0.5%"},
        "MSFT": {"price": 378.90, "change": "+0.8%"},
    }
    
    symbol_upper = symbol.upper()
    if symbol_upper in stock_data:
        return {"status": "success", "symbol": symbol_upper, **stock_data[symbol_upper]}
    
    return {"status": "error", "message": f"No data for symbol '{symbol}'"}


# Tool Before Callback
def validate_tool_call(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext) -> Optional[Dict]:
    tool_name = tool.name
    
    log_entry = {
        "tool": tool_name,
        "args": dict(args),
        "blocked": False,
        "reason": None
    }
    
    print(f"[BEFORE TOOL] Tool: {tool_name} | Args: {args}")
    
    # Policy: Block weather for restricted cities
    if tool_name == "get_weather":
        city = args.get("city", "").lower()
        if city in BLOCKED_CITIES:
            log_entry["blocked"] = True
            log_entry["reason"] = f"City '{city}' is restricted"
            tool_call_log.append(log_entry)
            
            print(f"[BEFORE TOOL] *** BLOCKED: '{city}' is retricted ***")
            
            return {
                "status": "blocked",
                "message": f"Weather data for '{city}' is restricted by company policy"
            }
    
    print(f"[BEFORE TOOL] Allowed.")
    tool_call_log.append(log_entry)
    return None


# Tool After Callback
def enrich_tool_result(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict) -> Optional[Dict]:
    tool_name = tool.name
    
    print(f"[AFTER TOOL] Tool: {tool_name} | Result: {str(tool_response)}")
    
    if isinstance(tool_response, dict) and tool_response.get("status") == "blocked":
        print(f"[AFTER TOOL] Skipped - cal was blocked by before_tool_callback")
        return None 
    
    tool_results_log.append({
        "tool": tool_name,
        "args": dict(args),
        "status": tool_response.get("status", "unknown") if isinstance(tool_response, dict) else "unknown"
    })
    
    # Enrich the result with metadata
    if isinstance(tool_response, dict):
        enriched = dict(tool_response)
        enriched["_metadata"] = {
            "processed_by": "after_tool_callback",
            "tool_name": tool_name
        }
        
        print(f"[AFTER TOOL] Enriched with _metadata")
        return enriched
    
    return None


agent = Agent(
    name="tool_validator_agent",
    model="gpt-4o-mini",
    description="A weather and stock assistant with tool validation and result enrichment",
    instruction="""You are a helpful assistant with access to weather and stock tools.
    When asked about weather, use the get_weather tool.
    When asked about stocks, use the get_stock_price tool
    Report results clearly and concisely
    """,
    tools=[get_weather, get_stock_price],
    before_tool_callback=validate_tool_call,
    after_tool_callback=enrich_tool_result
)

session_service = InMemorySessionService()
APP_NAME = "tool callback demo"
USER_ID = "user_1"
SESSION_ID = "session_1"

runner = Runner(
    agent=agent,
    app_name=APP_NAME,
    session_service=session_service
)

asyncio.run(
    session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
)

async def call_agent(query: str):
    print(f"\n>>> User: {query}")
    
    # Wrap User Query as a Content Object
    message = types.Content(role="user", parts=[types.Part(text=query)])
    
    final_response = "No response received"
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response = event.content.parts[0].text
                
    print(f"<<< Agent: {final_response}")
    

async def run_demo():    
    # Allowed calls
    print("=" * 60)
    print("Tool Callbacks - Validation & Result Enrichment")
    print("=" * 60)

    await call_agent("Whats the weather in Tokyo")
    await call_agent("Whats the stock price for AAPL")

    # Blocked calls
    print("=" * 60)
    print("Blocked Call - City Restriction")
    print("=" * 60)

    await call_agent("Whats the weather in Paris")


    # Audit Logs
    print("=" * 60)
    print("Reviewing Audit Logs")
    print("=" * 60)

    print("Before Tool Log")
    print(f"Total tool call attempts: {len(tool_call_log)}")
    for i, entry in enumerate(tool_call_log):
        status = "BLOCKED" if entry["blocked"] else "ALLOWED"
        print(f"{i + 1}.  [{status}  {entry["tool"]} {entry["args"]}]")
        

    print("After Tool Log")
    print(f"Total tool call attempts: {len(tool_results_log)}")
    for i, entry in enumerate(tool_results_log):
        print(f"{i + 1}. {entry["status"]} {entry["tool"]} {entry["args"]}")
    

if __name__ == "__main__":
    asyncio.run(run_demo())