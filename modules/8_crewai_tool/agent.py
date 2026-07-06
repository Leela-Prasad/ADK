from google.adk.agents import Agent
from google.adk.tools.crewai_tool import CrewaiTool

from dotenv import load_dotenv
load_dotenv()

from crewai_tools import ScrapeWebsiteTool

# create cerwai tool
scrapper_crewai = ScrapeWebsiteTool()

# Wrap with ADKs CrewaiTool wrapper
scrapper_tool = CrewaiTool(
    tool=scrapper_crewai,
    name="scrape_website",
    description="Scrape and extract text content from any website URL. Use this to read articles, blog posts, or any web page content"
)


root_agent = Agent(
    name="web_reader_agent",
    model="openai/gpt-4o-mini",
    tools=[scrapper_tool],
    description="An agent that can read and summarize web pages",
    instruction="""You are a web content anlayst
    Use the scrape_website tool to read content from URLs provided by the user.
    After scrapping, provide a clear summary of the page content.
    If the user asks about a specific topic on the page, focus on that.
    Always mention the source URL in your response.
    """
)