"""
Maahir — Centralized Configuration v2.0
All config values in one place. Uses environment variables with defaults.
Multi-API key rotation for reliability.
"""
import os
import random
import logging

logger = logging.getLogger(__name__)

# ── Google Cloud ─────────────────────────────────────────────────────────────
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "aiseekho2026-495022")
GCP_REGION = os.getenv("GCP_REGION", "us-central1")

# ── Multi-API Key Rotation ───────────────────────────────────────────────────
# Supports multiple API keys for reliability. If one hits quota, next activates.
# Set GOOGLE_API_KEY_1, GOOGLE_API_KEY_2, etc. in .env for multiple keys.
def _load_api_keys() -> list[str]:
    """Load all available API keys from environment."""
    keys = []
    # Primary key
    primary = os.getenv("GOOGLE_API_KEY", os.getenv("GEMINI_API_KEY", ""))
    if primary:
        keys.append(primary)
    # Additional keys (GOOGLE_API_KEY_2, _3, etc.)
    for i in range(2, 10):
        key = os.getenv(f"GOOGLE_API_KEY_{i}", "")
        if key:
            keys.append(key)
    return keys

API_KEYS = _load_api_keys()
_current_key_index = 0

def get_active_api_key() -> str:
    """Get the currently active API key."""
    global _current_key_index
    if not API_KEYS:
        return ""
    return API_KEYS[_current_key_index % len(API_KEYS)]

def rotate_api_key() -> str:
    """Rotate to the next API key (call on quota/auth failure)."""
    global _current_key_index
    if len(API_KEYS) <= 1:
        return get_active_api_key()
    _current_key_index = (_current_key_index + 1) % len(API_KEYS)
    new_key = API_KEYS[_current_key_index]
    os.environ["GOOGLE_API_KEY"] = new_key
    logger.info(f"Rotated to API key #{_current_key_index + 1} ({new_key[:8]}...)")
    return new_key

GOOGLE_API_KEY = get_active_api_key()

# ── Vertex AI Configuration ──────────────────────────────────────────────────
# ADK uses Vertex AI when these env vars are set.
# This bypasses API key auth and uses GCP project credentials instead.
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"
os.environ["GOOGLE_CLOUD_PROJECT"] = GCP_PROJECT_ID
os.environ["GOOGLE_CLOUD_LOCATION"] = GCP_REGION

# ── Gemini Model ─────────────────────────────────────────────────────────────
# Using full flash for best reasoning quality (not lite)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Google Maps
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

# ── Firestore Collections ───────────────────────────────────────────────────
FIRESTORE_PROVIDERS_COLLECTION = "providers"
FIRESTORE_BOOKINGS_COLLECTION = "bookings"
FIRESTORE_REMINDERS_COLLECTION = "reminders"
FIRESTORE_DISPUTES_COLLECTION = "disputes"

# ── Server ───────────────────────────────────────────────────────────────────
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("PORT", "8000"))

# ── Agent Config ─────────────────────────────────────────────────────────────
MAX_SEARCH_RADIUS_KM = 10
DEFAULT_TIMEZONE = "Asia/Karachi"
SUPPORTED_SERVICE_TYPES = [
    "ac_technician", "plumber", "electrician", "painter", "carpenter",
    "tutor", "beautician", "cook", "driver", "pest_control"
]

# ── 10-Factor Scoring Weights (Challenge 2 requirement: 6+ factors) ──────────
SCORING_WEIGHTS = {
    "distance":           0.12,  # Closer is better
    "rating":             0.15,  # Overall star rating
    "review_recency":     0.08,  # Penalize stale reviews
    "review_sentiment":   0.07,  # Positive keyword analysis
    "reliability":        0.15,  # On-time score minus cancellation penalty
    "skill_match":        0.12,  # Provider skills match job complexity
    "price":              0.10,  # More affordable is better
    "capacity":           0.08,  # Penalize overbooked providers
    "user_preference":    0.05,  # Language, verified status, gender
    "risk_score":         0.08,  # Composite: cancellation + complaints + recency
}

# ── Dynamic Pricing Config ───────────────────────────────────────────────────
PRICING_CONFIG = {
    # Base rate multipliers by service type (PKR per hour)
    "base_rates": {
        "ac_technician":  2000,
        "plumber":        1500,
        "electrician":    1500,
        "painter":        2500,
        "carpenter":      2000,
        "tutor":          3000,
        "beautician":     2500,
        "cook":           1800,
        "driver":         1200,
        "pest_control":   3000,
    },
    # Urgency multipliers
    "urgency_multiplier": {
        "normal":    1.0,
        "urgent":    1.3,
        "emergency": 1.5,
    },
    # Complexity multipliers
    "complexity_multiplier": {
        "basic":        1.0,
        "intermediate": 1.25,
        "complex":      1.6,
    },
    # Distance surcharge (PKR per km beyond free radius)
    "distance_free_km": 3.0,
    "distance_per_km": 100,
    # Surge pricing thresholds
    "surge_threshold": 3,    # If 3+ concurrent requests for same service_type
    "surge_multiplier": 1.2,
    # Loyalty discount
    "loyalty_discount_pct": 5,  # 5% off for returning customers
    # Visit/inspection fee
    "visit_fee": 500,  # PKR flat inspection/visit charge
}

# ── Scheduling Config ────────────────────────────────────────────────────────
SCHEDULING_CONFIG = {
    "travel_buffer_minutes": 30,       # Buffer between appointments
    "max_daily_bookings": 6,           # Max bookings per provider per day
    "advance_booking_days": 7,         # How far ahead users can book
    "cancellation_window_hours": 2,    # Free cancellation before this
    "waitlist_max_size": 3,            # Max users on waitlist per slot
    "reschedule_attempts": 3,          # Auto-reschedule tries if provider cancels
    "suggested_alternatives": 3,       # Number of alternative slots to suggest
}

# ── Dispute & Escalation Policy ──────────────────────────────────────────────
DISPUTE_POLICY = {
    "refund_rules": {
        "no_show":           100,  # 100% refund
        "late_arrival_30m":   20,  # 20% discount
        "late_arrival_60m":   40,  # 40% discount
        "quality_complaint":  50,  # 50% refund pending investigation
        "price_disagreement":  0,  # Mediation, no auto-refund
        "service_overrun":    10,  # 10% compensation for time overrun
    },
    "provider_penalties": {
        "no_show":           -15,  # -15 reliability points
        "late_arrival":       -5,  # -5 reliability points
        "quality_complaint": -10,  # -10 reliability points
        "cancellation":       -8,  # -8 reliability points
    },
    "blacklist_threshold": 50,     # Reliability below 50 = blacklisted
    "auto_escalation_threshold": 3, # 3+ disputes = human escalation
    "resolution_sla_hours": 24,    # Target resolution time
}

# ── Provider Optimization ────────────────────────────────────────────────────
PROVIDER_CONFIG = {
    "optimal_daily_jobs": 4,       # Ideal number of jobs per day
    "max_travel_km_daily": 30,     # Maximum travel distance per day
    "fair_earning_target": 8000,   # Target daily earning in PKR
    "demand_forecast_days": 7,     # Days to look ahead for demand
}
