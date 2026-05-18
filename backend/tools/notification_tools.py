"""
Maahir — Notification Tools
Handles scheduling reminders and generating multilingual messages.
"""

import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

# Try Firestore for persistence
_firestore_client = None
try:
    from google.cloud import firestore
    _firestore_client = firestore.Client()
except Exception:
    pass

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import FIRESTORE_REMINDERS_COLLECTION


def schedule_reminder(tool_context, booking_id: str, reminder_time: str, message: str) -> dict:
    """Schedule a reminder notification for an upcoming booking.

    Creates a reminder record that will trigger a notification to the user
    before their appointment. Stores in Firestore if available.

    Args:
        tool_context: ADK ToolContext for state access.
        booking_id: The booking ID to create a reminder for.
        reminder_time: ISO format datetime for when to send the reminder.
        message: The reminder message text.

    Returns:
        dict with reminder_id, booking_id, reminder_time, status.
    """
    try:
        reminder_id = f"rem_{uuid.uuid4().hex[:8]}"

        reminder = {
            "id": reminder_id,
            "booking_id": booking_id,
            "reminder_time": reminder_time,
            "message": message,
            "status": "scheduled",
            "created_at": datetime.now().isoformat() + "+05:00"
        }

        if _firestore_client:
            try:
                _firestore_client.collection(FIRESTORE_REMINDERS_COLLECTION).document(reminder_id).set(reminder)
            except Exception as fs_err:
                logger.warning(f"Firestore reminder write failed: {fs_err}")

        tool_context.state["scheduled_reminder"] = reminder
        logger.info(f"Scheduled reminder {reminder_id} for booking {booking_id} at {reminder_time}")
        return reminder

    except Exception as e:
        logger.error(f"Error scheduling reminder: {e}")
        return {
            "id": f"rem_{uuid.uuid4().hex[:8]}",
            "booking_id": booking_id,
            "reminder_time": reminder_time,
            "message": message,
            "status": "scheduled_with_errors",
            "error": str(e)
        }


def generate_messages(tool_context, booking_id: str, language: str = "auto") -> dict:
    """Generate confirmation and follow-up messages for a booking in the user's language.

    Creates a set of messages including booking confirmation, provider notification,
    pre-appointment reminder, and post-service feedback request.

    Args:
        tool_context: ADK ToolContext for state access.
        booking_id: The booking ID to generate messages for.
        language: Language preference ("ur", "en", "roman_urdu", or "auto").

    Returns:
        dict with confirmation, reminder, feedback messages and language used.
    """
    try:
        booking = tool_context.state.get("current_booking", {})
        if isinstance(booking, str):
            import json
            try:
                booking = json.loads(booking)
            except Exception:
                booking = {}

        provider_name = booking.get("provider_name", "Service Provider")
        service_type = booking.get("service_type", "service").replace("_", " ")
        scheduled_time = booking.get("scheduled_time", "scheduled time")
        phone = ""

        # Try to get phone from provider data
        all_providers = tool_context.state.get("all_providers", [])
        if isinstance(all_providers, list):
            for p in all_providers:
                if isinstance(p, dict) and p.get("id") == booking.get("provider_id"):
                    phone = p.get("phone", "")
                    break

        # Detect language
        lang = language.lower() if language else "auto"
        if lang == "auto":
            lang = tool_context.state.get("detected_language", "en")

        if lang in ("ur", "roman_urdu"):
            messages = {
                "confirmation": (
                    f"Assalam o Alaikum! Aapki {service_type} ki booking confirm ho gayi hai. "
                    f"{provider_name} aapki service ke liye {scheduled_time} par aayenge. "
                    f"Contact: {phone}" if phone else
                    f"Assalam o Alaikum! Aapki {service_type} ki booking confirm ho gayi hai. "
                    f"{provider_name} aapki service ke liye {scheduled_time} par aayenge."
                ),
                "reminder": (
                    f"Yaad dehani: Aapki {service_type} ki appointment 1 ghanta baad hai. "
                    f"{provider_name} jaldi aa rahe hain."
                ),
                "feedback": (
                    f"Kya aap {provider_name} ki service se khush hain? "
                    f"Apna tajurba share karein aur rating dein. Shukriya!"
                ),
                "provider_notification": (
                    f"Naye booking ka notification: {service_type} service, "
                    f"waqt: {scheduled_time}. Booking ID: {booking_id}"
                )
            }
        else:
            messages = {
                "confirmation": (
                    f"Your {service_type} has been booked successfully! "
                    f"{provider_name} will arrive at {scheduled_time}. "
                    f"Contact: {phone}" if phone else
                    f"Your {service_type} has been booked successfully! "
                    f"{provider_name} will arrive at {scheduled_time}."
                ),
                "reminder": (
                    f"Reminder: Your {service_type} appointment is in 1 hour. "
                    f"{provider_name} is on the way."
                ),
                "feedback": (
                    f"How was your experience with {provider_name}? "
                    f"Please rate the service and share your feedback. Thank you!"
                ),
                "provider_notification": (
                    f"New booking notification: {service_type} service, "
                    f"time: {scheduled_time}. Booking ID: {booking_id}"
                )
            }

        result = {
            "booking_id": booking_id,
            "language": lang,
            "messages": messages,
            "channels": ["sms", "whatsapp", "in_app"]
        }

        tool_context.state["generated_messages"] = result
        logger.info(f"Generated messages for booking {booking_id} in {lang}")
        return result

    except Exception as e:
        logger.error(f"Error generating messages: {e}")
        return {
            "booking_id": booking_id,
            "language": language,
            "messages": {
                "confirmation": "Your booking has been confirmed.",
                "reminder": "Reminder: Your appointment is coming up.",
                "feedback": "How was your experience? Please rate the service.",
                "provider_notification": f"New booking: {booking_id}"
            },
            "error": str(e)
        }
