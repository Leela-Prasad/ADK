from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
import asyncio

from dotenv import load_dotenv
load_dotenv()

agent = Agent(
    name="session_agent",
    model="gpt-4o-mini",
    description="A helpful assistant that demonstrates session based memory",
    instruction="""You are a friendly and concise assistant
    Answer user questions clearly.
    When asked to recall previous conversation, use the conversation history available to you
    """
)

session_service = InMemorySessionService()
APP_NAME = "session_demo"
USER_ID = "user_1"

runner = Runner(
    agent=agent,
    app_name=APP_NAME,
    session_service=session_service
)


def call_agent(user_id, session_id, query):
    print(f"\n>>> User: {query}")
    message = types.Content(role="user", parts=[types.Part(text=query)])
    
    final_response = "No response received"
    for event in runner.run(user_id=user_id, session_id=session_id, new_message=message):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response = event.content.parts[0].text
    
    print(f"<<< Agent: {final_response}")
    

print("=" * 60)
print("PART 1: Multi turn conversation (same session)")
print("=" * 60)

SESSION_1 = "session_001"
asyncio.run(
    session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_1
    )
)

call_agent(USER_ID, SESSION_1, "My Name is Leela and I live in Chennai")
call_agent(USER_ID, SESSION_1, "What is my name?")
call_agent(USER_ID, SESSION_1, "Which city I live in")
call_agent(USER_ID, SESSION_1, "Summarize everything we have discussed so far")

print("=" * 60)
print("PART 2: New Session (context is lost)")
print("=" * 60)

SESSION_2 = "session_002"
asyncio.run(
    session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_2
    )
)

call_agent(USER_ID, SESSION_2, "What is my name?")
call_agent(USER_ID, SESSION_2, "Which city I live in")
call_agent(USER_ID, SESSION_2, "Summarize everything we have discussed so far")