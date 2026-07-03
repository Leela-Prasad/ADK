from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm

root_agent = Agent(
    model=LiteLlm(model='openai/gpt-4o-mini'),
    
    # Agent Name where other models will use to call
    name='root_agent',
    
    # This descripiton is used by other agents 
    # to discover dynamically at runtime
    description='A helpful assistant for user questions.',
    
    # system prompt for the agent or the Role of the agent
    instruction='Answer user questions to the best of your knowledge',
)
