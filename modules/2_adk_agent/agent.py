import asyncio
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.models import LiteLlm
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "my_app"
USER_ID = "user_1"
SESSION_ID = "session_001"

agent = Agent(
    name = "helpful_agent",
    model=LiteLlm(model="openai/gpt-4o-mini"),
    description="A helpful assistant that answers user questions",
    instruction="You are a friendly and concise assistant. Answer user questions clearly"
)

session_service = InMemorySessionService()

runner = Runner(
    agent=agent,
    app_name=APP_NAME,
    session_service=session_service
)


def call_agent(query: str):
    print(f"\n>>> User: {query}")
    
    # Wrap User Query as a Content Object
    message = types.Content(role="user", parts=[types.Part(text=query)])
    
    final_response = "No response received"
    for event in runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response = event.content.parts[0].text
                
    print(f"<<< Agent: {final_response}")
    

# Create Session
session = asyncio.run(
    session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
)
    
if __name__ == "__main__":
    call_agent("What are the three laws of robotics?")
    call_agent("Who came up with them?")
    call_agent("Summarize our conversation so far in one sentence")