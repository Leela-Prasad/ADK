from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.tools import ToolContext
from google.genai import types
import asyncio

from dotenv import load_dotenv
load_dotenv()


# ToolContext will be automatically injected
def save_preference(key: str, value: str, tool_context: ToolContext) -> dict:
    """Saves a user preference to session state
    
    Args:
      key: The preference name(eg: theme, language)
      value: The preference value(eg: dark, python)
      
    Returns:
      A confirmation dictionary
    """
    
    print("save_preference tool invoked")
    tool_context.state[key] = value
    
    saved_keys = tool_context.state.get("_saved_keys", [])
    if key not in saved_keys:
        saved_keys.append(key)
    tool_context.state["_saved_keys"] = saved_keys 
    
    return {"status": "saved", "key": key, "value": value}
    
    
def get_preference(key: str, tool_context: ToolContext) -> dict:
    """Retrieves a user preference from session state
    
    Args:
      key: The preference name to lookup
      
    Returns:
      A dictionary with the preference value or an error message
    """
    
    print("get_preference tool invoked")
    value = tool_context.state.get(key)
    
    if value is not None:
        return {"status": "found", "key": key, "value": value}
    return {"status": "not_found", "key": key, "message": f"No preference found for '{key}'"}


def list_preferences(tool_context: ToolContext) -> dict:
    """Lists all saved user preferences from session state
    
    Returns:
      A dictionary with all stored preferences
    """
    
    print("list_preferences tool invoked")
    saved_keys = tool_context.state.get("_saved_keys", [])
    prefs = {}
    for k in saved_keys:
        val = tool_context.state.get(k)
        if val is not None:
            prefs[k] = val
    
    if prefs:
        return {"status": "success", "preferences": prefs}
    return {"status": "empty", "message": "No preferences saved yet"}


agent = Agent(
    name="preferences_agent",
    model="gpt-4o-mini",
    description="A personal assistant that remembers user preferences using session state",
    instruction="""You are a personal assistant that manages user preferences.
    
    You have threee tools:
    - save_preference: Save a key-value preference (eg: theme, language)
    - get_preference: Look up a specific preference by key
    - list_preferences: Show all saved preferences
    
    When the user tells you something about themselves or their preferences,
    proactively save it using save_preference.
    When asked about preferences, retrieve them using appropriate tool.
    Be friendly and confirm when you save something
    """,
    tools=[save_preference, get_preference, list_preferences]
)

session_service = InMemorySessionService()
APP_NAME = "state_demo"
USER_ID = "user_1"
SESSION_ID = "session_001"

asyncio.run(
    session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
)

runner = Runner(
    agent=agent,
    app_name=APP_NAME,
    session_service=session_service
)


def call_agent(query):
    print(f"\n>>> User: {query}")
    message = types.Content(role="user", parts=[types.Part(text=query)])
    
    final_response = "No response received"
    for event in runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response = event.content.parts[0].text
    
    print(f"<<< Agent: {final_response}")
    

print("=" * 60)
print("PART 1: Saving preference through conversation")
print("=" * 60)

call_agent("My name is Leela")
call_agent("I prefer dark mode")
call_agent("My favourite programming language is Java")
call_agent("Set my timezone is EST")


print("=" * 60)
print("PART 2: Retrieve preferences")
print("=" * 60)

call_agent("What is my name?")
call_agent("What theme do I prefer?")
call_agent("List all my preferences.")

print("=" * 60)
print("PART 3: Inspecting session state programatically")
print("=" * 60)

session = asyncio.run(
            session_service.get_session(
                app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
            )
        )


# Here session.state and tool_context.state refers to same state
print("Session state contents:")
for k,v in session.state.items():
    print(f"{k} = {v}")