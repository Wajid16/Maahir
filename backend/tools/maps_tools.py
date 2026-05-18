"""
Maahir — Maps Tools
Handles geocoding of Islamabad locations and distance calculations.
Uses hardcoded sector coordinates for hackathon demo, with Google Maps API fallback.
"""

import logging
import math
import json
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import GOOGLE_MAPS_API_KEY

logger = logging.getLogger(__name__)

ISLAMABAD_SECTORS = {
    "f-5": {"lat": 33.7230, "lng": 73.0580, "full_name": "F-5, Islamabad"},
    "f-6": {"lat": 33.7180, "lng": 73.0550, "full_name": "F-6, Islamabad"},
    "f-7": {"lat": 33.7140, "lng": 73.0450, "full_name": "F-7, Islamabad"},
    "f-8": {"lat": 33.7100, "lng": 73.0479, "full_name": "F-8, Islamabad"},
    "f-9": {"lat": 33.6950, "lng": 73.0250, "full_name": "F-9, Islamabad"},
    "f-10": {"lat": 33.6938, "lng": 73.0169, "full_name": "F-10, Islamabad"},
    "f-11": {"lat": 33.6830, "lng": 73.0020, "full_name": "F-11, Islamabad"},
    "g-5": {"lat": 33.7280, "lng": 73.0780, "full_name": "G-5, Islamabad"},
    "g-6": {"lat": 33.7210, "lng": 73.0700, "full_name": "G-6, Islamabad"},
    "g-7": {"lat": 33.7150, "lng": 73.0640, "full_name": "G-7, Islamabad"},
    "g-8": {"lat": 33.7050, "lng": 73.0480, "full_name": "G-8, Islamabad"},
    "g-9": {"lat": 33.6900, "lng": 73.0350, "full_name": "G-9, Islamabad"},
    "g-10": {"lat": 33.6780, "lng": 73.0250, "full_name": "G-10, Islamabad"},
    "g-11": {"lat": 33.6651, "lng": 73.0169, "full_name": "G-11, Islamabad"},
    "g-12": {"lat": 33.6540, "lng": 72.9980, "full_name": "G-12, Islamabad"},
    "g-13": {"lat": 33.6425, "lng": 72.9785, "full_name": "G-13, Islamabad"},
    "g-14": {"lat": 33.6300, "lng": 72.9600, "full_name": "G-14, Islamabad"},
    "g-15": {"lat": 33.6150, "lng": 72.9400, "full_name": "G-15, Islamabad"},
    "h-8": {"lat": 33.6980, "lng": 73.0480, "full_name": "H-8, Islamabad"},
    "h-9": {"lat": 33.6850, "lng": 73.0350, "full_name": "H-9, Islamabad"},
    "i-8": {"lat": 33.6900, "lng": 73.0650, "full_name": "I-8, Islamabad"},
    "i-9": {"lat": 33.6780, "lng": 73.0500, "full_name": "I-9, Islamabad"},
    "i-10": {"lat": 33.6650, "lng": 73.0350, "full_name": "I-10, Islamabad"},
    "blue area": {"lat": 33.7294, "lng": 73.0931, "full_name": "Blue Area, Islamabad"},
    "rawalpindi": {"lat": 33.5651, "lng": 73.0169, "full_name": "Rawalpindi"},
    "bahria town": {"lat": 33.5200, "lng": 73.0900, "full_name": "Bahria Town, Rawalpindi"},
}


def _haversine_km(lat1, lng1, lat2, lng2):
    """Calculate great-circle distance between two points in kilometers."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlng / 2) ** 2)
    return round(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 2)


def geocode_location(tool_context, location_text: str) -> dict:
    """Convert a location name to geographic coordinates.
    
    Supports Islamabad sector names (G-13, F-8), landmarks (Blue Area),
    and common areas. Uses hardcoded coordinates for instant response.
    
    Args:
        tool_context: ADK ToolContext for state access.
        location_text: Location name to geocode (e.g. "G-13", "Blue Area").
    
    Returns:
        dict with lat, lng, sector, city, full_name, source.
    """
    try:
        loc_lower = location_text.lower().strip()
        for prefix in ["sector ", "islamabad ", "isb "]:
            loc_lower = loc_lower.replace(prefix, "")
        loc_lower = loc_lower.strip()

        if loc_lower in ISLAMABAD_SECTORS:
            coords = ISLAMABAD_SECTORS[loc_lower]
            result = {
                "lat": coords["lat"], "lng": coords["lng"],
                "sector": location_text.strip(), "city": "Islamabad",
                "full_name": coords["full_name"], "source": "hardcoded_sectors"
            }
            tool_context.state["user_location"] = result
            return result

        # Fuzzy match
        normalized = loc_lower.replace(" ", "").replace("-", "")
        for key, coords in ISLAMABAD_SECTORS.items():
            if normalized == key.replace(" ", "").replace("-", ""):
                result = {
                    "lat": coords["lat"], "lng": coords["lng"],
                    "sector": location_text.strip(), "city": "Islamabad",
                    "full_name": coords["full_name"], "source": "fuzzy_match"
                }
                tool_context.state["user_location"] = result
                return result

        # Google Maps API fallback
        if GOOGLE_MAPS_API_KEY:
            try:
                import googlemaps
                gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
                res = gmaps.geocode(f"{location_text}, Islamabad, Pakistan")
                if res:
                    loc = res[0]["geometry"]["location"]
                    result = {
                        "lat": loc["lat"], "lng": loc["lng"],
                        "sector": location_text.strip(), "city": "Islamabad",
                        "full_name": res[0].get("formatted_address", location_text),
                        "source": "google_maps_api"
                    }
                    tool_context.state["user_location"] = result
                    return result
            except Exception as api_err:
                logger.warning(f"Google Maps API fallback failed: {api_err}")

        # Default to Islamabad center
        result = {
            "lat": 33.6844, "lng": 73.0479,
            "sector": location_text.strip(), "city": "Islamabad",
            "full_name": f"{location_text}, Islamabad (approximate)",
            "source": "default_center"
        }
        tool_context.state["user_location"] = result
        return result
    except Exception as e:
        logger.error(f"Error geocoding '{location_text}': {e}")
        result = {
            "lat": 33.6844, "lng": 73.0479,
            "sector": location_text.strip(), "city": "Islamabad",
            "full_name": f"{location_text} (fallback)", "source": "error_fallback"
        }
        tool_context.state["user_location"] = result
        return result


def calculate_distances(tool_context, user_lat: float, user_lng: float, providers_json: str) -> dict:
    """Calculate distances from user location to each provider using Haversine formula.
    
    Args:
        tool_context: ADK ToolContext for state access.
        user_lat: User's latitude.
        user_lng: User's longitude.
        providers_json: JSON string of provider objects with location data.
    
    Returns:
        dict with providers list (distance_km added), user_location, count.
    """
    try:
        if isinstance(providers_json, str):
            try:
                providers = json.loads(providers_json)
            except json.JSONDecodeError:
                providers = []
        elif isinstance(providers_json, list):
            providers = providers_json
        else:
            providers = []

        enriched = []
        for p in providers:
            if not isinstance(p, dict):
                continue
            prov_loc = p.get("location", {})
            dist = _haversine_km(user_lat, user_lng, prov_loc.get("lat", 0), prov_loc.get("lng", 0))
            pc = dict(p)
            pc["distance_km"] = dist
            enriched.append(pc)

        enriched.sort(key=lambda x: x.get("distance_km", 999))
        tool_context.state["providers_with_distances"] = enriched
        return {"providers": enriched, "user_location": {"lat": user_lat, "lng": user_lng}, "count": len(enriched)}
    except Exception as e:
        logger.error(f"Error calculating distances: {e}")
        return {"providers": [], "user_location": {"lat": user_lat, "lng": user_lng}, "count": 0, "error": str(e)}
