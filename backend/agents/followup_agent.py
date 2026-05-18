"""
Maahir — Agent: Follow-up & Support
Combines Follow-up and Dispute resolution.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from google.adk.agents import LlmAgent
from config import GEMINI_MODEL
from tools.notification_tools import schedule_reminder, generate_messages
from tools.dispute_tools import file_dispute, calculate_refund, adjust_reputation

FOLLOWUP_INSTRUCTION = """You are the Follow-up & Support agent for Maahir (ماہر).

Your job is to simulate post-booking reminders or handle disputes if the user is complaining about a past service.

## Input
Parsed intent: {parsed_intent}
Booking details (if any): {booking_details}

## Your Task
1. Check if the user is complaining or filing a dispute based on their message.
2. If it's a dispute, use **file_dispute** and **calculate_refund**.
3. If it's a normal new booking follow-up, use **schedule_reminder** to simulate a reminder.
4. Explain the resolution or follow-up plan clearly.

## Output Format
Return ONLY valid JSON:
{{
  "followup_plan": {{
    "service_lifecycle": {{"stages": []}},
    "reminders_scheduled": true
  }},
  "dispute": {{
    "dispute_handled": false,
    "status": "none"
  }},
  "decision_reasoning": "Scheduled reminder for the upcoming booking."
}}
"""

followup_agent = LlmAgent(
    name="followup",
    model=GEMINI_MODEL,
    instruction=FOLLOWUP_INSTRUCTION,
    tools=[schedule_reminder, generate_messages, file_dispute, calculate_refund, adjust_reputation],
    output_key="followup_details",
    description="Handles post-booking lifecycle: reminders, check-ins, and dispute resolutions."
)
