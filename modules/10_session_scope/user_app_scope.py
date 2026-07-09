import asyncio
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import ToolContext
from google.genai import types

load_dotenv()

# Global Session Service instance to allow tools to cross-reference scopes
session_service = InMemorySessionService()
APP_NAME = "state_demo"


# Helper to fetch or initialize states across different scopes
async def save_to_scope_service(
    scope: str, key: str, value: str, current_user: str
):
    # Determine target coordinates based on scope
    u_id = "GLOBAL_APP" if scope == "app" else current_user
    s_id = (
        "GLOBAL_APP"
        if scope == "app"
        else ("GLOBAL_USER" if scope == "user" else None)
    )

    if s_id:  # For User and App scopes, we use a dedicated persistent session
        try:
            session = await session_service.get_session(
                app_name=APP_NAME, user_id=u_id, session_id=s_id
            )
        except Exception:
            session = await session_service.create_session(
                app_name=APP_NAME, user_id=u_id, session_id=s_id
            )
        session.state[key] = value


def save_preference(
    key: str, value: str, scope: str, tool_context: ToolContext
) -> dict:
    """Saves a preference to a specific scope (session, user, or app).

    Args:
        key: The preference name (eg: theme, language)
        value: The preference value (eg: dark, python)
        scope: The scope level. Must be 'session', 'user', or 'app'.
    """
    scope = scope.lower()
    if scope not in ["session", "user", "app"]:
        return {
            "status": "error",
            "message": "Invalid scope. Choose 'session', 'user', or 'app'.",
        }

    print(f"save_preference tool invoked for [{scope}] scope")

    # 1. Always save to the immediate local tool_context for the current session run
    if scope == "session":
        tool_context.state[f"session_{key}"] = value
    elif scope == "user":
        tool_context.state[f"user_{key}"] = value
        # 2. Persist to User-level global state asynchronously
        asyncio.run(
            save_to_scope_service(
                "user", key, value, current_user=tool_context.user_id
            )
        )
    elif scope == "app":
        tool_context.state[f"app_{key}"] = value
        # 2. Persist to App-level global state asynchronously
        asyncio.run(
            save_to_scope_service(
                "app", key, value, current_user=tool_context.user_id
            )
        )

    return {
        "status": "saved",
        "scope": scope,
        "key": key,
        "value": value,
    }


def get_preference(key: str, tool_context: ToolContext) -> dict:
    """Retrieves a preference, checking session, then user, then app levels."""
    print("get_preference tool invoked")

    # Fallback cascade: Check Session -> Check User -> Check App
    if f"session_{key}" in tool_context.state:
        return {
            "status": "found",
            "scope": "session",
            "value": tool_context.state[f"session_{key}"],
        }

    if f"user_{key}" in tool_context.state:
        return {
            "status": "found",
            "scope": "user",
            "value": tool_context.state[f"user_{key}"],
        }

    if f"app_{key}" in tool_context.state:
        return {
            "status": "found",
            "scope": "app",
            "value": tool_context.state[f"app_{key}"],
        }

    return {
        "status": "not_found",
        "key": key,
        "message": f"No preference found for '{key}' at any scope.",
    }


agent = Agent(
    name="preferences_agent",
    model="gemini-2.5-flash",  # Swapped to standard Gemini model for google-genai compatibility
    description="An assistant that remembers preferences across session, user, and app levels",
    instruction="""You manage user preferences across three scopes:
    - 'session': Temporary things specific to this exact conversation.
    - 'user': Things specific to this user that should cross over to other conversations (e.g. language, name).
    - 'app': Global defaults or application-wide settings.
    
    Proactively ask or decide which scope is appropriate when saving variables.""",
    tools=[save_preference, get_preference],
)

# Set up test environment
USER_ID = "user_1"
SESSION_ID = "session_001"

asyncio.run(
    session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
)

runner = Runner(
    agent=agent, app_name=APP_NAME, session_service=session_service
)


def call_agent(query):
    print(f"\n>>> User: {query}")
    message = types.Content(role="user", parts=[types.Part(text=query)])
    final_response = "No response received"
    for event in runner.run(
        user_id=USER_ID, session_id=SESSION_ID, new_message=message
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response = event.content.parts[0].text
    print(f"<<< Agent: {final_response}")


# Execution test demonstrating multiple scopes
call_agent(
    "Save the app-wide default language as 'Python' at the app level."
)
call_agent("My name is Leela. Save this to my user profile.")
call_agent(
    "For just this current session, set my temporary project folder to '/tmp/build'."
)

print("\n" + "=" * 60)
print("Verification Queries")
print("=" * 60)
call_agent("What is my name?")
call_agent("What is the application default language?")
call_agent("What is my temporary project folder?")