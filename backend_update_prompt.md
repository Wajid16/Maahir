# Backend Update Instructions

You must update your **Google Antigravity Python Backend** to mirror the new features we added to the Flutter frontend. 

Copy and paste the following prompt into your backend development AI agent or follow the instructions manually:

***

## Prompt for Backend Orchestrator

"I am updating my Google Antigravity backend for the Google AI Hackathon Challenge 2. I need you to implement the following changes to our multi-agent pipeline and SSE streaming response:

**1. Auto-Reroute Simulation (Agentic Resilience)**
Currently, the `booking` agent always succeeds. I need you to update the `matcher` and `booking` agents to handle a failure state. 
*   **Action:** Modify the tool logic so that 20% of the time, the `contact_provider` tool returns a `Provider Busy / Rejected` error.
*   **Action:** The Supervisor must detect this error and invoke a `select_next_best_provider` tool, rerouting the request back to the `matcher` to pick the 2nd best provider, and then successfully book them.
*   **SSE Output:** Ensure the `traceSteps` streamed to the frontend clearly show the sequence: `Attempting to Book -> Error: Provider Busy -> Auto-Rerouting -> Booking Confirmed`. This is critical for the hackathon judging.

**2. Follow-Up Feedback Action**
Currently, the `followup` agent just schedules a reminder. 
*   **Action:** Add a new asynchronous task that triggers exactly 4 seconds after a successful booking stream completes.
*   **SSE Output:** Stream a new standard text message from the Orchestrator saying: `It looks like your booking was confirmed! 🚀 To help our community, please rate your experience with [Provider Name] once the job is done.`

**3. Telephone Links**
*   **Action:** Ensure that the `phone` field in the `ServiceProvider` schema passed down in the JSON response is perfectly formatted with the country code (e.g., `+92-300-1234567`) so the Flutter frontend can correctly launch the native `tel:` dialer.

Please update the FastAPI endpoints and Antigravity tool definitions to support this."
