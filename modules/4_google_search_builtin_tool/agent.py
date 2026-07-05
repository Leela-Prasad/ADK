from google.adk.agents import Agent
from google.adk.tools import google_search

from dotenv import load_dotenv
load_dotenv()

root_agent = Agent(
    name="search_agent",
    model="openai/gpt-5-mini",
    description="An agent that can search the web using Google Search",
    instruction="""You are a helpful research assistant.
    Use Google Search to find current, accurate information for the users questions.
    Always cite your sources when possible.
    If you are unsure abouth something, search for it rather than guessing.
    """,
    tools=[google_search]
)