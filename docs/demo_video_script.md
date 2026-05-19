# Maahir - Demo Video Script (3-5 Minutes)

Use this storyboard to record your 3-5 minute demo video. Ensure you speak clearly and confidently!

## 1. Introduction (0:00 - 0:30)
*   **Visual:** Start on the Home Screen of the Maahir mobile app (Dark Mode).
*   **Voiceover:** "Hello judges, this is Maahir. Our solution addresses Pakistan's informal economy by connecting users with verified local service providers. We built the mobile app in Flutter and our orchestrator in FastAPI using the Google Gen AI SDK."

## 2. Demonstrating the Core Workflow (0:30 - 1:30)
*   **Visual:** Type a natural language request in Urdu/Roman Urdu into the Chat screen: *"Mujhe G-13 mein ek accha AC mechanic chahiye jo sasta ho."*
*   **Voiceover:** "Users can type naturally in English or Urdu. Watch how fast it works. The backend dynamically intercepts the request and instantly responds with highly relevant local providers."
*   **Visual:** Show the sleek `ProviderCard` rendering the Google Maps Static API image inside the chat bubble.

## 3. Highlighting Agency (1:30 - 3:00)
*   **Visual:** Tap the "Agent Activity Logs" (Reasoning Trace) to expand it. 
*   **Voiceover:** "Here is where the real magic happens. We did not build a rigid pipeline. We built the Antigravity Supervisor architecture. You can see the **Planner Agent** parsing the intent, the **Discovery Match Agent** scoring providers using a 10-factor algorithm, and the **Booking Agent** securing the slot dynamically."
*   **Visual:** Scroll through the reasoning trace to show the tools being called (e.g., `calculate_distances`, `score_providers`).

## 4. Innovation & Resilience (3:00 - 4:00)
*   **Visual:** Ask the bot to book the provider.
*   **Voiceover:** "Our biggest innovation is Agentic Resilience. If a provider rejects a booking or is unavailable, the Supervisor automatically detects the failure and loops back to the Discovery agent to find the *next* best provider, completely autonomously, without throwing an error to the user."
*   **Visual:** Show the final `BookingCard` with the confirmation message.

## 5. Conclusion (4:00 - 4:30)
*   **Visual:** Show the Navigation Drawer with multiple chat sessions.
*   **Voiceover:** "Maahir is production-ready, highly localized to Pakistan, and fully multi-modal. Thank you for your time."
