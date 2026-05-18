"""
Maahir — Agent: Booking Simulation
Combines Pricing, Scheduling, and Booking into a single action node.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from google.adk.agents import LlmAgent
from config import GEMINI_MODEL
from tools.pricing_tools import calculate_dynamic_price, get_market_average
from tools.scheduling_tools import check_scheduling_conflicts, get_provider_workload
from tools.firestore_tools import create_booking, update_availability, contact_provider
from tools.notification_tools import generate_messages

BOOKING_SIMULATION_INSTRUCTION = """You are the Booking Simulation agent for Maahir (ماہر).

Your job is to finalize pricing, check scheduling, and simulate the booking.

## Input
Parsed intent: {parsed_intent}
Discovered providers (with chosen top provider): {discovered_providers}

## Your Task
1. Extract the selected provider and requested time from the state.
2. Use **calculate_dynamic_price** to generate the pricing quote.
3. Use **check_scheduling_conflicts** to ensure the provider is free.
4. **CRITICAL:** Use **contact_provider** to verify if the provider accepts the job.
   - If `contact_provider` returns `error` (e.g., "Provider Busy / Rejected"), you MUST stop and return an error state: `{"error": "Provider Busy", "failed_provider_id": "prov_xyz"}`. DO NOT proceed to create a booking.
5. If the provider is available, use **create_booking** to simulate booking in the system.
6. Use **generate_confirmation** to create the final user message.
7. Return the finalized booking details.

## Output Format
Return ONLY valid JSON:
{{
  "pricing": {{
    "price_range": {{"min": 1500, "max": 2000, "currency": "PKR"}},
    "pricing_reasoning": "Standard base rate applied."
  }},
  "scheduling": {{
    "slot_available": true,
    "confirmed_time": "2026-05-19T10:00:00Z"
  }},
  "booking": {{
    "id": "book_123",
    "provider_id": "prov_001",
    "provider_name": "Provider Name",
    "status": "confirmed",
    "confirmation_message": "Your booking is confirmed for..."
  }},
  "decision_reasoning": "Booking confirmed successfully without conflicts."
}}
"""

booking_simulation_agent = LlmAgent(
    name="booking_simulation",
    model=GEMINI_MODEL,
    instruction=BOOKING_SIMULATION_INSTRUCTION,
    tools=[calculate_dynamic_price, get_market_average, check_scheduling_conflicts, 
           get_provider_workload, contact_provider, create_booking, update_availability, generate_messages],
    output_key="booking_details",
    description="Calculates pricing, verifies schedules, contacts the provider, and simulates the booking."
)
