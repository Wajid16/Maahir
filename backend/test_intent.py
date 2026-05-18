import asyncio
import os
from dotenv import load_dotenv
load_dotenv(override=True)
import sys
sys.path.insert(0, os.path.dirname(__file__))
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agents.intent_parser import intent_parser_agent

async def run():
    session_service = InMemorySessionService()
    session = await session_service.create_session('maahir', 'user1', 'session1')
    message = types.Content(role='user', parts=[types.Part.from_text(text='I need a plumber in F-8')])
    print(f"Agent model: {intent_parser_agent.model}")
    print(f"API Key start: {os.getenv('GOOGLE_API_KEY')[:10]}")
    try:
        response = await intent_parser_agent.run(session=session, new_message=message)
        print("Response:", response)
        print("State:", session.state)
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    asyncio.run(run())
