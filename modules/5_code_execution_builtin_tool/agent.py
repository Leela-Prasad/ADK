from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.code_executors import BuiltInCodeExecutor

from dotenv import load_dotenv
load_dotenv()

root_agent = Agent(
    name="code_exec_agent",
    model="gpt-4o-mini",
    description="An agent that can write and execute Python code",
    instruction="""You are a helpful assistant that can write and execute Python code.
    When given a mathematical problem, data analysis task or any computation,
    write Python code to solve it. Return the result clearly to the user.
    You can also use Google Search for factual information.
    """,
    tools=[google_search],
    code_executor=BuiltInCodeExecutor()  #Enables code execution
)