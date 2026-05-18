"""
Maahir — DateTime Tools
Handles parsing of natural language time expressions in Urdu, Roman Urdu, and English.
Also checks provider availability against requested times.
"""

import logging
from datetime import datetime, timedelta
from dateutil import parser as dateutil_parser
import json

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import DEFAULT_TIMEZONE

logger = logging.getLogger(__name__)

# ── Roman Urdu / Urdu time keyword mappings ──────────────────────────────────

TIME_KEYWORDS = {
    # "now" variants
    "abhi": {"offset_hours": 0, "is_urgent": True},
    "abi": {"offset_hours": 0, "is_urgent": True},
    "right now": {"offset_hours": 0, "is_urgent": True},
    "foran": {"offset_hours": 0, "is_urgent": True},
    "turant": {"offset_hours": 0, "is_urgent": True},
    "jaldi": {"offset_hours": 1, "is_urgent": True},
    "urgent": {"offset_hours": 0, "is_urgent": True},
    "urgently": {"offset_hours": 0, "is_urgent": True},

    # "morning" variants
    "subah": {"hour": 9, "minute": 0},
    "morning": {"hour": 9, "minute": 0},
    "savere": {"hour": 7, "minute": 0},

    # "afternoon" variants
    "dopahar": {"hour": 13, "minute": 0},
    "dupahar": {"hour": 13, "minute": 0},
    "afternoon": {"hour": 13, "minute": 0},

    # "evening" variants
    "sham": {"hour": 17, "minute": 0},
    "shaam": {"hour": 17, "minute": 0},
    "evening": {"hour": 17, "minute": 0},
    "evenings": {"hour": 17, "minute": 0},

    # "night" variants
    "raat": {"hour": 20, "minute": 0},
    "night": {"hour": 20, "minute": 0},
}

DAY_KEYWORDS = {
    # "today"
    "aaj": 0,
    "today": 0,
    "aj": 0,

    # "tomorrow"
    "kal": 1,
    "kal ko": 1,
    "tomorrow": 1,

    # "day after tomorrow"
    "parson": 2,
    "parso": 2,
    "day after tomorrow": 2,
}

WEEKDAY_MAP = {
    "monday": 0, "somwar": 0, "pir": 0,
    "tuesday": 1, "mangal": 1,
    "wednesday": 2, "budh": 2,
    "thursday": 3, "jumeraat": 3, "jumerat": 3,
    "friday": 4, "juma": 4,
    "saturday": 5, "hafta": 5,
    "sunday": 6, "itwar": 6, "itwaar": 6,
}


def parse_datetime(tool_context, time_expression: str) -> dict:
    """Parse a natural language time expression (Roman Urdu, Urdu, or English) into a structured datetime.
    
    Handles expressions like:
    - "kal subah" (tomorrow morning)
    - "abhi" (right now)  
    - "parson sham" (day after tomorrow evening)
    - "Friday morning"
    - "evenings"
    
    Args:
        tool_context: ADK ToolContext for state access.
        time_expression: Natural language time string to parse.
    
    Returns:
        dict with keys: datetime (ISO format), is_urgent (bool), parsed_day, parsed_time, original.
    """
    try:
        now = datetime.now()
        expr_lower = time_expression.lower().strip()
        
        target_date = now
        target_hour = None
        target_minute = 0
        is_urgent = False
        parsed_day = "today"
        parsed_time = "unspecified"

        # ── Step 1: Detect day offset ────────────────────────────────────
        day_offset = None
        for keyword, offset in sorted(DAY_KEYWORDS.items(), key=lambda x: -len(x[0])):
            if keyword in expr_lower:
                day_offset = offset
                parsed_day = keyword
                break
        
        if day_offset is not None:
            target_date = now + timedelta(days=day_offset)

        # ── Step 2: Detect weekday ───────────────────────────────────────
        if day_offset is None:
            for keyword, weekday_num in WEEKDAY_MAP.items():
                if keyword in expr_lower:
                    days_ahead = weekday_num - now.weekday()
                    if days_ahead <= 0:
                        days_ahead += 7
                    target_date = now + timedelta(days=days_ahead)
                    parsed_day = keyword
                    break

        # ── Step 3: Detect time of day ───────────────────────────────────
        for keyword, time_info in sorted(TIME_KEYWORDS.items(), key=lambda x: -len(x[0])):
            if keyword in expr_lower:
                if "is_urgent" in time_info:
                    is_urgent = time_info["is_urgent"]
                    target_hour = now.hour
                    target_minute = now.minute
                    parsed_time = "now"
                    if time_info.get("offset_hours", 0) > 0:
                        target_date = now + timedelta(hours=time_info["offset_hours"])
                        target_hour = target_date.hour
                        target_minute = target_date.minute
                else:
                    target_hour = time_info["hour"]
                    target_minute = time_info.get("minute", 0)
                    parsed_time = keyword
                break

        # ── Step 4: Try dateutil as fallback ─────────────────────────────
        if target_hour is None:
            try:
                parsed = dateutil_parser.parse(expr_lower, fuzzy=True)
                if parsed.hour != 0 or "am" in expr_lower or "pm" in expr_lower:
                    target_hour = parsed.hour
                    target_minute = parsed.minute
                    parsed_time = f"{target_hour}:{target_minute:02d}"
            except (ValueError, OverflowError):
                pass

        # ── Step 5: Default to 9 AM if no time detected ─────────────────
        if target_hour is None:
            target_hour = 9
            target_minute = 0
            parsed_time = "morning (default)"

        # ── Build final datetime ─────────────────────────────────────────
        result_dt = target_date.replace(
            hour=target_hour,
            minute=target_minute,
            second=0,
            microsecond=0
        )

        # If the time is in the past for today, push to tomorrow
        if result_dt < now and not is_urgent:
            result_dt += timedelta(days=1)

        result = {
            "datetime": result_dt.isoformat() + "+05:00",
            "is_urgent": is_urgent,
            "parsed_day": parsed_day,
            "parsed_time": parsed_time,
            "original": time_expression
        }

        # Save to state
        tool_context.state["parsed_datetime"] = result
        logger.info(f"Parsed datetime: {time_expression} → {result['datetime']}")
        return result

    except Exception as e:
        logger.error(f"Error parsing datetime '{time_expression}': {e}")
        # Graceful fallback: tomorrow 9 AM
        fallback = datetime.now() + timedelta(days=1)
        fallback = fallback.replace(hour=9, minute=0, second=0, microsecond=0)
        result = {
            "datetime": fallback.isoformat() + "+05:00",
            "is_urgent": False,
            "parsed_day": "tomorrow",
            "parsed_time": "morning (fallback)",
            "original": time_expression,
            "error": str(e)
        }
        tool_context.state["parsed_datetime"] = result
        return result


def check_availability(tool_context, provider_id: str, requested_time: str) -> dict:
    """Check if a specific provider is available at the requested time.
    
    Looks up the provider's availability schedule and checks if the requested
    time falls within any of their available slots.
    
    Args:
        tool_context: ADK ToolContext for state access.
        provider_id: The provider's unique ID (e.g., "prov_001").
        requested_time: ISO format datetime string for the requested appointment.
    
    Returns:
        dict with keys: available (bool), provider_id, requested_time, slot_matched, reason.
    """
    try:
        # Get providers from state
        providers_data = tool_context.state.get("all_providers", [])
        if isinstance(providers_data, str):
            try:
                providers_data = json.loads(providers_data)
            except json.JSONDecodeError:
                providers_data = []

        provider = None
        for p in providers_data:
            if isinstance(p, dict) and p.get("id") == provider_id:
                provider = p
                break

        if not provider:
            return {
                "available": False,
                "provider_id": provider_id,
                "requested_time": requested_time,
                "slot_matched": None,
                "reason": f"Provider {provider_id} not found in data"
            }

        # Parse requested time
        try:
            req_dt = dateutil_parser.parse(requested_time)
        except (ValueError, OverflowError):
            req_dt = datetime.now() + timedelta(days=1)
            req_dt = req_dt.replace(hour=9, minute=0)

        day_name = req_dt.strftime("%A").lower()
        req_hour = req_dt.hour
        req_minute = req_dt.minute
        req_time_str = f"{req_hour:02d}:{req_minute:02d}"

        availability = provider.get("availability", [])
        slot_matched = None

        for day_schedule in availability:
            if isinstance(day_schedule, dict) and day_schedule.get("day", "").lower() == day_name:
                for slot in day_schedule.get("slots", []):
                    try:
                        start_str, end_str = slot.split("-")
                        start_h, start_m = map(int, start_str.split(":"))
                        end_h, end_m = map(int, end_str.split(":"))
                        start_total = start_h * 60 + start_m
                        end_total = end_h * 60 + end_m
                        req_total = req_hour * 60 + req_minute

                        if start_total <= req_total < end_total:
                            slot_matched = slot
                            break
                    except (ValueError, AttributeError):
                        continue
                break

        is_available = slot_matched is not None
        reason = f"Slot {slot_matched} is available on {day_name}" if is_available else f"No available slot on {day_name} at {req_time_str}"

        result = {
            "available": is_available,
            "provider_id": provider_id,
            "requested_time": requested_time,
            "slot_matched": slot_matched,
            "reason": reason
        }

        logger.info(f"Availability check: {provider_id} at {requested_time} → {is_available}")
        return result

    except Exception as e:
        logger.error(f"Error checking availability for {provider_id}: {e}")
        return {
            "available": True,
            "provider_id": provider_id,
            "requested_time": requested_time,
            "slot_matched": "assumed",
            "reason": f"Assumed available (error: {str(e)})"
        }
