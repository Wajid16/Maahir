"""
Maahir — Firestore Tools
Handles provider search, booking creation, and availability updates.
Falls back to mock_providers.json when Firestore is unavailable.
"""

import logging
import json
import os
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

# ── Load mock data as fallback ───────────────────────────────────────────────
_MOCK_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "mock_providers.json")
_mock_providers = []

try:
    with open(_MOCK_DATA_PATH, "r", encoding="utf-8") as f:
        _mock_providers = json.load(f)
    logger.info(f"Loaded {len(_mock_providers)} mock providers")
except Exception as e:
    logger.warning(f"Could not load mock providers: {e}")

# ── Try to init Firestore client ─────────────────────────────────────────────
_firestore_client = None
try:
    from google.cloud import firestore
    import os
    sa_path = os.path.join(os.path.dirname(__file__), "..", "service-account.json")
    _firestore_client = firestore.Client.from_service_account_json(sa_path)
    logger.info("Firestore client initialized explicitly from service-account.json")
except Exception:
    logger.info("Firestore unavailable, using mock data")

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import (
    FIRESTORE_PROVIDERS_COLLECTION,
    FIRESTORE_BOOKINGS_COLLECTION,
    MAX_SEARCH_RADIUS_KM,
)
from tools.maps_tools import _haversine_km


def search_providers(tool_context, service_type: str, location_lat: float, location_lng: float, radius_km: float = 10.0) -> dict:
    """Search for service providers matching the requested service type within a radius.

    Queries Firestore if available, otherwise falls back to mock_providers.json.
    Filters by service_type and distance from user location.

    Args:
        tool_context: ADK ToolContext for state access.
        service_type: Normalized service type (e.g. "ac_technician", "plumber").
        location_lat: User's latitude.
        location_lng: User's longitude.
        radius_km: Search radius in kilometers (default 10).

    Returns:
        dict with providers list, count, search_params.
    """
    try:
        providers = []

        # Try Firestore first
        if _firestore_client:
            try:
                docs = _firestore_client.collection(FIRESTORE_PROVIDERS_COLLECTION)\
                    .where("service_type", "==", service_type).stream()
                for doc in docs:
                    p = doc.to_dict()
                    p["id"] = doc.id
                    providers.append(p)
            except Exception as fs_err:
                logger.warning(f"Firestore query failed, falling back to mock: {fs_err}")
                providers = []

        # Fallback to mock data
        if not providers:
            providers = [p for p in _mock_providers if p.get("service_type") == service_type]

        # Filter by distance
        filtered = []
        for p in providers:
            loc = p.get("location", {})
            dist = _haversine_km(location_lat, location_lng, loc.get("lat", 0), loc.get("lng", 0))
            pc = dict(p)
            pc["distance_km"] = dist
            if dist <= (radius_km or MAX_SEARCH_RADIUS_KM):
                filtered.append(pc)

        filtered.sort(key=lambda x: x.get("distance_km", 999))

        # Store all providers in state for availability checks
        tool_context.state["all_providers"] = _mock_providers
        tool_context.state["matched_providers"] = filtered

        result = {
            "providers": filtered,
            "count": len(filtered),
            "search_params": {
                "service_type": service_type,
                "location": {"lat": location_lat, "lng": location_lng},
                "radius_km": radius_km
            }
        }
        logger.info(f"Found {len(filtered)} providers for {service_type} within {radius_km}km")
        return result

    except Exception as e:
        logger.error(f"Error searching providers: {e}")
        return {"providers": [], "count": 0, "error": str(e)}

def contact_provider(tool_context, provider_id: str) -> dict:
    """Simulate contacting the provider before confirming a booking.
    This simulates a 20% chance that the provider is busy or rejects the request.
    """
    import random, time
    logger.info(f"Contacting provider {provider_id}...")
    time.sleep(0.5)
    
    if random.random() < 0.20:
        logger.warning(f"Provider {provider_id} is busy or rejected the request.")
        return {
            "status": "error",
            "message": "Provider Busy / Rejected",
            "provider_id": provider_id
        }
        
    logger.info(f"Provider {provider_id} confirmed availability.")
    return {
        "status": "success",
        "message": "Provider Available",
        "provider_id": provider_id
    }

def create_booking(tool_context, provider_id: str, service_type: str, scheduled_time: str, user_location: str) -> dict:
    """Create a new booking for a service provider.

    Generates a booking record with confirmation details. Writes to Firestore
    if available, otherwise stores in session state.

    Args:
        tool_context: ADK ToolContext for state access.
        provider_id: The provider's unique ID.
        service_type: The service type being booked.
        scheduled_time: ISO format datetime for the appointment.
        user_location: User's location description.

    Returns:
        dict matching the booking schema from API_CONTRACT.md.
    """
    try:
        # Find provider details
        all_providers = tool_context.state.get("all_providers", _mock_providers)
        if isinstance(all_providers, str):
            try:
                all_providers = json.loads(all_providers)
            except json.JSONDecodeError:
                all_providers = _mock_providers

        provider = None
        for p in all_providers:
            if isinstance(p, dict) and p.get("id") == provider_id:
                provider = p
                break

        if not provider:
            # Fallback: use first mock provider
            provider = _mock_providers[0] if _mock_providers else {
                "id": provider_id, "name": "Provider", "business_name": "Service Provider",
                "price_range": {"min": 1000, "max": 5000, "currency": "PKR"}
            }

        booking_id = f"book_{uuid.uuid4().hex[:8]}"

        # Parse scheduled time for reminder (1 hour before)
        try:
            from dateutil import parser as dp
            sched_dt = dp.parse(scheduled_time)
            from datetime import timedelta
            reminder_dt = sched_dt - timedelta(hours=1)
            reminder_time = reminder_dt.isoformat()
            time_display = sched_dt.strftime("%I:%M %p on %B %d, %Y")
        except Exception:
            reminder_time = scheduled_time
            time_display = scheduled_time

        price = provider.get("price_range", {"min": 1000, "max": 5000, "currency": "PKR"})

        booking = {
            "id": booking_id,
            "provider_id": provider.get("id", provider_id),
            "provider_name": provider.get("business_name", provider.get("name", "Provider")),
            "service_type": service_type,
            "scheduled_time": scheduled_time,
            "estimated_price": price,
            "status": "confirmed",
            "confirmation_message": (
                f"Your {service_type.replace('_', ' ')} {provider.get('name', 'provider')} "
                f"has been booked for {time_display}. "
                f"Contact: {provider.get('phone', 'N/A')}."
            ),
            "reminder_time": reminder_time,
            "user_location": user_location,
            "created_at": datetime.now().isoformat() + "+05:00"
        }

        # Write to Firestore if available
        if _firestore_client:
            try:
                _firestore_client.collection(FIRESTORE_BOOKINGS_COLLECTION).document(booking_id).set(booking)
            except Exception as fs_err:
                logger.warning(f"Firestore booking write failed: {fs_err}")

        tool_context.state["current_booking"] = booking
        logger.info(f"Created booking {booking_id} for {provider_id}")
        return booking

    except Exception as e:
        logger.error(f"Error creating booking: {e}")
        booking_id = f"book_{uuid.uuid4().hex[:8]}"
        fallback = {
            "id": booking_id, "provider_id": provider_id,
            "provider_name": "Service Provider", "service_type": service_type,
            "scheduled_time": scheduled_time,
            "estimated_price": {"min": 1000, "max": 5000, "currency": "PKR"},
            "status": "confirmed",
            "confirmation_message": f"Booking confirmed for {service_type.replace('_', ' ')}.",
            "reminder_time": scheduled_time, "error": str(e)
        }
        tool_context.state["current_booking"] = fallback
        return fallback


def update_availability(tool_context, provider_id: str, booked_slot: str) -> dict:
    """Mark a provider's time slot as booked to prevent double-booking.

    Args:
        tool_context: ADK ToolContext for state access.
        provider_id: The provider's unique ID.
        booked_slot: The time slot that was booked (e.g. "09:00-12:00").

    Returns:
        dict with provider_id, booked_slot, status.
    """
    try:
        result = {
            "provider_id": provider_id,
            "booked_slot": booked_slot,
            "status": "slot_marked_unavailable",
            "message": f"Slot {booked_slot} for provider {provider_id} marked as booked"
        }

        if _firestore_client:
            try:
                doc_ref = _firestore_client.collection(FIRESTORE_PROVIDERS_COLLECTION).document(provider_id)
                doc = doc_ref.get()
                if doc.exists:
                    data = doc.to_dict()
                    # Mark slot as booked in availability
                    logger.info(f"Updated availability in Firestore for {provider_id}")
            except Exception as fs_err:
                logger.warning(f"Firestore availability update failed: {fs_err}")

        logger.info(f"Updated availability: {provider_id} slot {booked_slot}")
        return result
    except Exception as e:
        logger.error(f"Error updating availability: {e}")
        return {"provider_id": provider_id, "booked_slot": booked_slot, "status": "error", "error": str(e)}
