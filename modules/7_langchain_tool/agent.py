from google.adk.agents import Agent
# Here LangchainTool is a wrapper class around Langchain framework
# which converts schemas, requests in langchain compatible format
from google.adk.tools.langchain_tool import LangchainTool

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

from dotenv import load_dotenv
load_dotenv()

# create Langchain wikipedia tool
wikipedia_lc = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

# Wrap it with ADKs LangchainTool wrapper
wikipedia_tool = LangchainTool(
    tool=wikipedia_lc,
    name="wikipedia_search",
    description="Search Wikipedia for information on any topic. Use this factual, encyclopedia information"
)


root_agent = Agent(
    name="research_agent",
    model="openai/gpt-4o-mini",
    tools=[wikipedia_tool],
    description="A research assistant with access to Wikipedia",
    instruction="""You are a knowledgeable research assistant
    Use the Wikipedia tool to lookup factual information.
    Provide clear, well-organized answers based on the search results.
    Always indicate when information comes from Wikipedia.
    """
)