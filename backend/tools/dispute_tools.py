"""
Maahir — Dispute & Escalation Tools v2.0
Handles no-show, quality complaints, price disputes, refunds, reputation adjustment.
"""

import logging
import json
import uuid
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import DISPUTE_POLICY

logger = logging.getLogger(__name__)

DISPUTE_TYPES = {
    "no_show": {"label": "Provider No-Show", "label_ur": "فراہم کنندہ نہیں آیا", "severity": "high", "auto_resolve": True, "resolution": "Full refund + auto-rebook with backup provider"},
    "late_arrival": {"label": "Late Arrival", "label_ur": "دیر سے آمد", "severity": "medium", "auto_resolve": True, "resolution": "Partial discount based on delay"},
    "quality_complaint": {"label": "Quality Complaint", "label_ur": "معیار کی شکایت", "severity": "high", "auto_resolve": False, "resolution": "Investigation — re-service or refund"},
    "price_disagreement": {"label": "Price Disagreement", "label_ur": "قیمت پر اختلاف", "severity": "medium", "auto_resolve": False, "resolution": "Mediation between quoted and actual"},
    "service_overrun": {"label": "Service Overrun", "label_ur": "سروس وقت زیادہ", "severity": "low", "auto_resolve": True, "resolution": "Compensation for extra time"},
    "cancellation_by_provider": {"label": "Provider Cancelled", "label_ur": "فراہم کنندہ نے منسوخ کیا", "severity": "high", "auto_resolve": True, "resolution": "Auto-reschedule with next provider"},
    "cancellation_by_user": {"label": "User Cancellation", "label_ur": "صارف نے منسوخ کیا", "severity": "low", "auto_resolve": True, "resolution": "Cancellation policy applied"},
    "safety_concern": {"label": "Safety Concern", "label_ur": "حفاظتی تشویش", "severity": "critical", "auto_resolve": False, "resolution": "Immediate human escalation"},
}


def file_dispute(tool_context, booking_id: str, dispute_type: str, description: str, provider_id: str = "") -> dict:
    """File a dispute for a booking. Returns dispute record with resolution plan and refund info."""
    try:
        dispute_id = f"disp_{uuid.uuid4().hex[:8]}"
        info = DISPUTE_TYPES.get(dispute_type, DISPUTE_TYPES["quality_complaint"])
        booking = tool_context.state.get("current_booking", {})
        if isinstance(booking, str):
            try: booking = json.loads(booking)
            except: booking = {}
        if not provider_id:
            provider_id = booking.get("provider_id", "unknown")
        refund_pct = DISPUTE_POLICY["refund_rules"].get(dispute_type, 0)
        ep = booking.get("estimated_price", {})
        base_amount = ep.get("min", 2000) if isinstance(ep, dict) else 2000
        refund_amount = int(base_amount * refund_pct / 100)
        penalty = DISPUTE_POLICY["provider_penalties"].get(dispute_type.split("_by_")[0] if "_by_" in dispute_type else dispute_type, -5)
        pdc = int(tool_context.state.get(f"dispute_count_{provider_id}", 0)) + 1
        needs_escalation = pdc >= DISPUTE_POLICY["auto_escalation_threshold"] or info["severity"] == "critical"
        steps = _build_steps(dispute_type, refund_amount, needs_escalation)
        dispute = {
            "dispute_id": dispute_id, "booking_id": booking_id, "provider_id": provider_id,
            "dispute_type": dispute_type, "dispute_label": info["label"], "dispute_label_ur": info["label_ur"],
            "severity": info["severity"], "description": description,
            "status": "resolved" if info["auto_resolve"] and not needs_escalation else "under_review",
            "refund": {"eligible": refund_pct > 0, "percentage": refund_pct, "amount": refund_amount, "currency": "PKR"},
            "provider_impact": {"reliability_penalty": penalty, "total_disputes": pdc, "blacklist_risk": pdc >= 3, "warning_issued": pdc >= 2},
            "resolution": {"plan": info["resolution"], "steps": steps, "auto_resolved": info["auto_resolve"] and not needs_escalation,
                           "needs_human_escalation": needs_escalation, "estimated_resolution_hours": DISPUTE_POLICY["resolution_sla_hours"]},
            "created_at": datetime.now().isoformat() + "+05:00",
        }
        tool_context.state["current_dispute"] = json.dumps(dispute, default=str)
        tool_context.state[f"dispute_count_{provider_id}"] = str(pdc)
        return dispute
    except Exception as e:
        return {"dispute_id": f"disp_{uuid.uuid4().hex[:8]}", "booking_id": booking_id, "status": "error", "error": str(e)}


def calculate_refund(tool_context, booking_id: str, dispute_type: str, original_price: int, service_completed_pct: float = 0) -> dict:
    """Calculate fair refund based on dispute type and service completion percentage."""
    try:
        base_pct = DISPUTE_POLICY["refund_rules"].get(dispute_type, 0)
        adjusted_pct = base_pct * ((100 - service_completed_pct) / 100) if service_completed_pct > 0 else base_pct
        refund = int(original_price * adjusted_pct / 100)
        return {"booking_id": booking_id, "original_price": original_price, "refund_percentage": round(adjusted_pct, 1),
                "refund_amount": refund, "currency": "PKR", "service_completed_pct": service_completed_pct,
                "explanation": f"Based on {dispute_type.replace('_',' ')} policy: {adjusted_pct:.0f}% refund (PKR {refund:,}) of PKR {original_price:,}."}
    except Exception as e:
        return {"booking_id": booking_id, "error": str(e)}


def adjust_reputation(tool_context, provider_id: str, dispute_type: str, dispute_outcome: str = "resolved") -> dict:
    """Adjust provider's reputation score and determine blacklist status."""
    try:
        all_provs = tool_context.state.get("all_providers", [])
        if isinstance(all_provs, str):
            try: all_provs = json.loads(all_provs)
            except: all_provs = []
        old_score = 80.0
        for p in all_provs:
            if isinstance(p, dict) and p.get("id") == provider_id:
                old_score = float(p.get("reliability_score", 80.0)); break
        pk = dispute_type.split("_by_")[0] if "_by_" in dispute_type else dispute_type
        penalty = DISPUTE_POLICY["provider_penalties"].get(pk, -5)
        if dispute_outcome == "dismissed": penalty = 0
        elif dispute_outcome == "escalated": penalty *= 2
        new_score = max(0, min(100, old_score + penalty))
        blacklisted = new_score < DISPUTE_POLICY["blacklist_threshold"]
        impact = "Provider blacklisted — removed from searches." if blacklisted else f"Score changed {penalty:+.0f} pts. Ranking adjusted."
        return {"provider_id": provider_id, "old_reliability_score": old_score, "penalty_applied": penalty,
                "new_reliability_score": new_score, "is_blacklisted": blacklisted, "future_impact": impact}
    except Exception as e:
        return {"provider_id": provider_id, "error": str(e)}


def escalate_to_human(tool_context, dispute_id: str, reason: str, priority: str = "high") -> dict:
    """Escalate dispute to human support team."""
    try:
        eid = f"esc_{uuid.uuid4().hex[:8]}"
        sla = {"low": 48, "medium": 24, "high": 12, "critical": 4}
        return {"escalation_id": eid, "dispute_id": dispute_id, "priority": priority, "reason": reason,
                "status": "escalated_to_human", "estimated_response_hours": sla.get(priority, 24),
                "message": f"Case #{eid} escalated with {priority} priority. Response in ~{sla.get(priority,24)}h.",
                "message_ur": f"کیس #{eid} بھیج دیا گیا۔ متوقع جواب: {sla.get(priority,24)} گھنٹے۔"}
    except Exception as e:
        return {"dispute_id": dispute_id, "error": str(e)}


def _build_steps(dtype, refund_amt, escalate):
    steps_map = {
        "no_show": [{"step":1,"action":"Provider marked no-show","status":"completed"},{"step":2,"action":f"Refund PKR {refund_amt:,} initiated","status":"completed"},{"step":3,"action":"Reliability -15 points","status":"completed"},{"step":4,"action":"Searching backup provider...","status":"in_progress"}],
        "late_arrival": [{"step":1,"action":"Late arrival recorded","status":"completed"},{"step":2,"action":f"Discount PKR {refund_amt:,} applied","status":"completed"},{"step":3,"action":"Reliability adjusted","status":"completed"}],
        "quality_complaint": [{"step":1,"action":"Complaint recorded","status":"completed"},{"step":2,"action":"Investigation started","status":"in_progress"},{"step":3,"action":"Re-service or refund pending","status":"pending"}],
        "price_disagreement": [{"step":1,"action":"Quote vs actual compared","status":"completed"},{"step":2,"action":"Scope analysis","status":"in_progress"},{"step":3,"action":"Fair price mediation","status":"pending"}],
        "cancellation_by_provider": [{"step":1,"action":"Cancellation recorded","status":"completed"},{"step":2,"action":"Provider penalized","status":"completed"},{"step":3,"action":"Finding replacement...","status":"in_progress"}],
    }
    s = steps_map.get(dtype, [{"step":1,"action":"Issue recorded","status":"completed"},{"step":2,"action":"Under review","status":"in_progress"}])
    if escalate:
        s.append({"step":len(s)+1,"action":"Escalated to human support","status":"in_progress"})
    return s
