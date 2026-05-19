import asyncio
import uuid
import time
from main import chat, ChatRequest, session_service

async def run_test():
    session_id = str(uuid.uuid4())
    req = ChatRequest(message="Mujhe kal subah G-13 mein AC technician chahiye", session_id=session_id)
    
    start = time.time()
    try:
        resp = await chat(req)
        print("Response:", resp.response)
        print("Trace steps:", [t.agent + " (" + t.status + ")" for t in resp.trace_steps])
        if resp.booking:
            print("Booking generated:", resp.booking.id)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_test())
