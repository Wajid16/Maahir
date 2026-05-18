"""
Maahir — Agent 7: Follow-Up v2.0
Service lifecycle simulation: en-route, completion, feedback, rating impact.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from google.adk.agents import LlmAgent
from config import GEMINI_MODEL
from tools.notification_tools import schedule_reminder, generate_messages

FOLLOWUP_INSTRUCTION = """You are the Follow-Up & Service Lifecycle agent for Maahir (ماہر).

Your job is to set up the COMPLETE post-booking automation including service tracking, feedback, and rating updates.

## Input
Booking details: {booking_details}
Parsed intent: {parsed_intent}
Pricing details: {pricing_details}

## Your Task
1. If booking_details shows needs_clarification=true or no booking, skip and pass through
2. Use **schedule_reminder** to create a reminder 1 hour before appointment
3. Use **generate_messages** to create all lifecycle messages in user's language
4. Create the FULL service lifecycle simulation:

### Service Lifecycle Stages
1. **Pre-Service**: Reminder 1 hour before, provider notification
2. **En-Route**: "Provider is on the way, ETA 15 minutes" (simulated)
3. **In-Progress**: "Service has started" notification
4. **Completion**: Service completion checklist
5. **Evidence**: Photo/video evidence placeholder
6. **Feedback**: Customer rating request (punctuality, quality, professionalism, value)
7. **Rating Update**: How new rating impacts provider's overall score
8. **Future Impact**: How feedback affects future matching

## Tools Available
- **schedule_reminder**: Schedule reminder (booking_id, reminder_time, message)
- **generate_messages**: Generate all messages (booking_id, language)

## Output Format
You MUST respond with ONLY a valid JSON object:
{{
  "followup_plan": {{
    "reminder_scheduled": true,
    "reminder_time": "ISO datetime",
    "messages_generated": true,
    "service_lifecycle": {{
      "stages": [
        {{"stage": "pre_service", "time": "-1 hour", "action": "Reminder sent to customer and provider", "status": "scheduled"}},
        {{"stage": "en_route", "time": "-15 min", "action": "Provider en-route notification with ETA", "status": "scheduled"}},
        {{"stage": "arrival", "time": "0 min", "action": "Provider arrived confirmation", "status": "pending"}},
        {{"stage": "in_progress", "time": "+5 min", "action": "Service started notification", "status": "pending"}},
        {{"stage": "completion", "time": "+90 min", "action": "Service completion checklist submitted", "status": "pending",
          "checklist": ["Work area inspected", "Equipment tested", "Customer walkthrough done", "Area cleaned up"]}},
        {{"stage": "evidence", "time": "+95 min", "action": "Provider uploads photo/video evidence of completed work", "status": "pending"}},
        {{"stage": "feedback", "time": "+2 hours", "action": "Customer feedback request sent",
          "criteria": ["Punctuality", "Work Quality", "Professionalism", "Value for Money"], "status": "pending"}},
        {{"stage": "rating_update", "time": "+2.5 hours", "action": "Provider rating recalculated based on feedback",
          "impact": "New rating will affect future matching rank", "status": "pending"}}
      ]
    }},
    "feedback_config": {{
      "criteria": ["punctuality", "quality", "professionalism", "value"],
      "scale": "1-5 stars",
      "allows_text_review": true,
      "allows_photo_evidence": true,
      "rating_impact_explanation": "Your feedback directly impacts this provider's future ranking and visibility."
    }}
  }},
  "needs_clarification": false
}}"""

followup_agent = LlmAgent(
    name="followup",
    model=GEMINI_MODEL,
    instruction=FOLLOWUP_INSTRUCTION,
    tools=[schedule_reminder, generate_messages],
    output_key="followup_plan",
    description="Manages complete service lifecycle: reminders, en-route tracking, completion checklist, evidence collection, feedback, and rating impact."
)
