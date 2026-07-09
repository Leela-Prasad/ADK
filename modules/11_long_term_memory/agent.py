from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.tools import load_memory
from google.genai import types
import asyncio

from dotenv import load_dotenv
load_dotenv()

APP_NAME = "memory_demo"
USER_ID = "user_001"
MODEL = "openai/gpt-4o-mini"


info_capture_agent = LlmAgent(
    model=MODEL,
    name="info_capture_agent",
    instruction="""You are a friendly assistant that acknowledges and confirms
    information when the user shares with you. Whe the user tells you facts about
    themselves, repeat back what you heard to confirm you understood.
    """
)


memory_recall_agent = LlmAgent(
    model=MODEL,
    name="memory_recall_agent",
    instruction="""You are a helpful assistant that answers questions
    Use the 'load_memory' tool to search past conversations for relevant information.
    Always try to use load_memory before saying you don't know something.
    """,
    tools=[load_memory]
)


session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()

async def run_demo():
    print("=" * 60)
    print("PART 1: Capturing information (Session A)")
    print("=" * 60)
    
    runner1 = Runner(
        agent=info_capture_agent,
        app_name=APP_NAME,
        session_service=session_service,
        # This is for longterm memory
        memory_service=memory_service
    )
    
    session_a_id = "session_capture"
    await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=session_a_id
    )
    
    facts = [
        "My Name is Leela and I am Integration Specialist",
        "I live in Chennai",
        "My Favourite programming language in Java",
    ]
    
    for fact in facts:
        print(f"\n>>> User: {fact}")
        message = types.Content(role="user", parts=[types.Part(text=fact)])
        
        response_text = "No response"
        async for event in runner1.run_async(user_id=USER_ID, session_id=session_a_id, new_message=message):
            if event.is_final_response() and event.content and event.content.parts:
                response_text = event.content.parts[0].text
                
        print(f"<<< Agent: {response_text}")
    
    
    print("=" * 60)
    print("PART 2: Storing session in long term memory")
    print("=" * 60)
    
    completed_session = await session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=session_a_id
    )
    
    # This will add only the summary of the session, 
    # but not all events in the session using vector db
    await memory_service.add_session_to_memory(completed_session)
    print("Session A has been added to long term memory")
    print(f"Session has {len(completed_session.events)} events")
    
    
    print("=" * 60)
    print("PART 3: Recalling information (New Session B)")
    print("=" * 60)
    print("Note: This is brand new session - the agent has NO")
    print("conversation history. It must use load_memory to recall facts")
    
    runner2 = Runner(
        agent=memory_recall_agent,
        app_name=APP_NAME,
        session_service=session_service,
        # Here we are the same memory service
        # used by info_capture_agent
        memory_service=memory_service
    )
    
    session_b_id = "session_recall"
    await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=session_b_id
    )
    
    questions = [
        "what is my name?",
        "Where do I live",
        "what programming language do I prefer"
    ]

    for question in questions:
        print(f"\n>>> User: {question}")
        message = types.Content(role="user", parts=[types.Part(text=question)])
        
        reponse_text = "No Response"
        async for event in runner2.run_async(user_id=USER_ID, session_id=session_b_id, new_message=message):
            if event.is_final_response() and event.content and event.content.parts:
                response_text = event.content.parts[0].text
        
        print(f"<<< Agent: {response_text}")
        
        
if __name__ == "__main__":
    asyncio.run(run_demo())