"""
Maahir — Scheduling Intelligence Tools v2.0
Double-booking prevention, travel buffers, waitlists, auto-reschedule.
"""
import logging, json, uuid, sys, os
from datetime import datetime, timedelta
from dateutil import parser as dp

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import SCHEDULING_CONFIG

logger = logging.getLogger(__name__)


def check_scheduling_conflicts(tool_context, provider_id: str, requested_time: str, duration_minutes: int = 90) -> dict:
    """Check for double-booking conflicts and travel buffer violations.
    Returns conflict status, existing bookings, and alternative slots."""
    try:
        cfg = SCHEDULING_CONFIG
        req_dt = dp.parse(requested_time)
        req_end = req_dt + timedelta(minutes=duration_minutes)
        buffer = timedelta(minutes=cfg["travel_buffer_minutes"])
        # Get existing bookings from state
        bookings = tool_context.state.get("provider_bookings", [])
        if isinstance(bookings, str):
            try: bookings = json.loads(bookings)
            except: bookings = []
        conflicts = []
        for b in bookings:
            if not isinstance(b, dict) or b.get("provider_id") != provider_id: continue
            try:
                b_start = dp.parse(b.get("scheduled_time", ""))
                b_end = b_start + timedelta(minutes=b.get("duration_minutes", 90))
                # Check overlap including buffer
                if (req_dt < b_end + buffer) and (req_end + buffer > b_start):
                    conflicts.append({"booking_id": b.get("id",""), "time": b.get("scheduled_time",""), "conflict_type": "overlap" if (req_dt < b_end and req_end > b_start) else "buffer_violation"})
            except: continue
        # Count daily bookings
        req_date = req_dt.date()
        daily_count = sum(1 for b in bookings if isinstance(b,dict) and b.get("provider_id")==provider_id and dp.parse(b.get("scheduled_time","2000-01-01")).date()==req_date)
        over_limit = daily_count >= cfg["max_daily_bookings"]
        has_conflict = len(conflicts) > 0 or over_limit
        # Generate alternatives if conflict
        alternatives = []
        if has_conflict:
            alternatives = _suggest_alternatives(req_dt, duration_minutes, bookings, provider_id, cfg)
        result = {
            "provider_id": provider_id, "requested_time": requested_time, "has_conflict": has_conflict,
            "conflicts": conflicts, "daily_booking_count": daily_count, "daily_limit": cfg["max_daily_bookings"],
            "over_daily_limit": over_limit, "travel_buffer_minutes": cfg["travel_buffer_minutes"],
            "suggested_alternatives": alternatives,
            "reasoning": _conflict_reasoning(conflicts, over_limit, daily_count, cfg)
        }
        tool_context.state["scheduling_result"] = json.dumps(result, default=str)
        return result
    except Exception as e:
        return {"provider_id": provider_id, "has_conflict": False, "error": str(e)}


def manage_waitlist(tool_context, provider_id: str, requested_time: str, user_id: str = "") -> dict:
    """Add user to waitlist for a provider's busy slot."""
    try:
        cfg = SCHEDULING_CONFIG
        wl_key = f"waitlist_{provider_id}_{requested_time[:10]}"
        waitlist = tool_context.state.get(wl_key, [])
        if isinstance(waitlist, str):
            try: waitlist = json.loads(waitlist)
            except: waitlist = []
        if len(waitlist) >= cfg["waitlist_max_size"]:
            return {"status": "waitlist_full", "position": -1, "max_size": cfg["waitlist_max_size"],
                    "message": "Waitlist is full for this slot. Please choose an alternative time."}
        entry = {"user_id": user_id or f"user_{uuid.uuid4().hex[:6]}", "requested_time": requested_time,
                 "added_at": datetime.now().isoformat() + "+05:00", "status": "waiting"}
        waitlist.append(entry)
        tool_context.state[wl_key] = json.dumps(waitlist, default=str)
        return {"status": "added_to_waitlist", "position": len(waitlist), "total_waiting": len(waitlist),
                "message": f"You're #{len(waitlist)} on the waitlist. You'll be notified if the slot opens up.",
                "message_ur": f"آپ ویٹنگ لسٹ میں #{len(waitlist)} نمبر پر ہیں۔ سلاٹ خالی ہونے پر مطلع کیا جائے گا۔"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def auto_reschedule(tool_context, cancelled_booking_id: str, original_provider_id: str, service_type: str, original_time: str) -> dict:
    """Auto-reschedule when a provider cancels. Finds next best provider."""
    try:
        cfg = SCHEDULING_CONFIG
        max_attempts = cfg["reschedule_attempts"]
        matched = tool_context.state.get("matched_providers", [])
        if isinstance(matched, str):
            try: matched = json.loads(matched)
            except: matched = []
        # Filter out the cancelled provider
        candidates = [p for p in matched if isinstance(p,dict) and p.get("id") != original_provider_id]
        if not candidates:
            return {"status": "no_alternatives", "cancelled_booking_id": cancelled_booking_id,
                    "message": "No alternative providers available. Please try a different time or service.",
                    "message_ur": "کوئی متبادل فراہم کنندہ دستیاب نہیں۔ مختلف وقت یا سروس آزمائیں۔"}
        # Try each candidate
        for i, candidate in enumerate(candidates[:max_attempts]):
            # Simulate availability check
            avail = candidate.get("availability", [])
            try:
                req_dt = dp.parse(original_time)
                day_name = req_dt.strftime("%A").lower()
                req_hour = req_dt.hour
                for sched in avail:
                    if isinstance(sched,dict) and sched.get("day","").lower() == day_name:
                        for slot in sched.get("slots",[]):
                            start_h = int(slot.split("-")[0].split(":")[0])
                            end_h = int(slot.split("-")[1].split(":")[0])
                            if start_h <= req_hour < end_h:
                                return {
                                    "status": "rescheduled", "cancelled_booking_id": cancelled_booking_id,
                                    "new_provider": {"id": candidate.get("id"), "name": candidate.get("name"),
                                                     "business_name": candidate.get("business_name"), "rating": candidate.get("rating")},
                                    "scheduled_time": original_time, "attempt": i+1,
                                    "message": f"Rescheduled with {candidate.get('name','provider')}. Same time slot confirmed.",
                                    "message_ur": f"{candidate.get('name','provider')} کے ساتھ دوبارہ شیڈول ہو گیا۔ وقت اسی رہے گا۔"}
            except: continue
        return {"status": "partial_reschedule", "cancelled_booking_id": cancelled_booking_id,
                "message": "Could not find exact time match. Here are alternative providers and times.",
                "alternatives": [{"provider": c.get("name"), "id": c.get("id")} for c in candidates[:3]]}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def get_provider_workload(tool_context, provider_id: str, date_str: str = "") -> dict:
    """Get provider's workload for optimization and fair distribution."""
    try:
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")
        cfg = SCHEDULING_CONFIG
        bookings = tool_context.state.get("provider_bookings", [])
        if isinstance(bookings, str):
            try: bookings = json.loads(bookings)
            except: bookings = []
        target_date = dp.parse(date_str).date()
        day_bookings = [b for b in bookings if isinstance(b,dict) and b.get("provider_id")==provider_id and dp.parse(b.get("scheduled_time","2000-01-01")).date()==target_date]
        from config import PROVIDER_CONFIG
        return {
            "provider_id": provider_id, "date": date_str, "bookings_today": len(day_bookings),
            "optimal_daily_jobs": PROVIDER_CONFIG["optimal_daily_jobs"],
            "max_daily_bookings": cfg["max_daily_bookings"],
            "utilization_pct": round(len(day_bookings) / max(cfg["max_daily_bookings"],1) * 100, 1),
            "is_overloaded": len(day_bookings) >= cfg["max_daily_bookings"],
            "recommended_action": "available" if len(day_bookings) < PROVIDER_CONFIG["optimal_daily_jobs"] else "near_capacity" if len(day_bookings) < cfg["max_daily_bookings"] else "at_capacity",
        }
    except Exception as e:
        return {"provider_id": provider_id, "error": str(e)}


def _suggest_alternatives(req_dt, duration, bookings, provider_id, cfg):
    """Suggest alternative time slots."""
    alts = []
    for offset_hours in [1, 2, 3, -1, -2, 4]:
        alt_dt = req_dt + timedelta(hours=offset_hours)
        if alt_dt.hour < 8 or alt_dt.hour > 18: continue
        has_conflict = False
        for b in bookings:
            if not isinstance(b, dict) or b.get("provider_id") != provider_id: continue
            try:
                b_start = dp.parse(b.get("scheduled_time",""))
                b_end = b_start + timedelta(minutes=b.get("duration_minutes",90))
                buf = timedelta(minutes=cfg["travel_buffer_minutes"])
                if (alt_dt < b_end + buf) and (alt_dt + timedelta(minutes=duration) + buf > b_start):
                    has_conflict = True; break
            except: continue
        if not has_conflict:
            alts.append({"datetime": alt_dt.isoformat()+"+05:00", "display": alt_dt.strftime("%I:%M %p, %B %d"), "offset_hours": offset_hours})
        if len(alts) >= cfg["suggested_alternatives"]: break
    return alts


def _conflict_reasoning(conflicts, over_limit, daily_count, cfg):
    parts = []
    if conflicts:
        parts.append(f"Found {len(conflicts)} scheduling conflict(s) with existing bookings.")
        for c in conflicts: parts.append(f"  - {c['conflict_type']}: conflicts with booking {c.get('booking_id','?')}")
    if over_limit:
        parts.append(f"Provider has {daily_count}/{cfg['max_daily_bookings']} bookings today (at capacity).")
    if not conflicts and not over_limit:
        parts.append("No scheduling conflicts found. Slot is available.")
    return " ".join(parts)
