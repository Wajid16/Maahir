"""
Maahir — Agent: Discovery & Match
Combines Provider Discovery and Matching into a single robust decision node.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from google.adk.agents import LlmAgent
from config import GEMINI_MODEL, SCORING_WEIGHTS
from tools.firestore_tools import search_providers
from tools.maps_tools import geocode_location, calculate_distances
from tools.datetime_tools import check_availability
import json

def score_provider(tool_context, provider_json: str, requested_time: str) -> dict:
    """Score a provider using 10 weighted factors with transparent per-factor reasoning."""
    try:
        provider = json.loads(provider_json) if isinstance(provider_json, str) else provider_json
        w = SCORING_WEIGHTS
        factors = {}
        
        # 1. Distance
        distance = float(provider.get("distance_km", 5.0))
        dist_score = max(0, 100 - (distance / 10.0 * 100))
        factors["distance"] = {"score": round(dist_score, 1), "weight": w["distance"], "weighted": round(dist_score * w["distance"], 1), "reasoning": f"{distance:.1f}km away."}
        
        # 2. Rating
        rating = float(provider.get("rating", 3.0))
        rating_score = (rating / 5.0) * 100
        factors["rating"] = {"score": round(rating_score, 1), "weight": w["rating"], "weighted": round(rating_score * w["rating"], 1), "reasoning": f"{rating}/5.0 stars."}

        # 3. Reliability
        reliability = float(provider.get("reliability_score", 80.0))
        factors["reliability"] = {"score": round(reliability, 1), "weight": w["reliability"], "weighted": round(reliability * w["reliability"], 1), "reasoning": f"Reliability {reliability:.0f}/100."}

        total = sum(f["weighted"] for f in factors.values())
        total = round(min(100, max(0, total)))
        
        avail = check_availability(tool_context, provider.get("id", ""), requested_time)
        is_available = avail.get("available", True)
        if not is_available:
            total = int(total * 0.6)
            
        top_reasons = [f"{k}: {v['reasoning']}" for k, v in sorted(factors.items(), key=lambda x: x[1]["weighted"], reverse=True)[:3]]

        return {
            "provider_id": provider.get("id"), "score": total,
            "factors": factors, "available": is_available,
            "availability_detail": avail.get("reason", ""),
            "top_reasons": top_reasons,
            "reasoning": f"Score {total}/100. " + " | ".join(top_reasons),
        }
    except Exception as e:
        return {"provider_id": "unknown", "score": 50, "reasoning": f"Error: {e}", "available": True}

DISCOVERY_MATCH_INSTRUCTION = """You are the Discovery & Match agent for Maahir (ماہر).

Your job is to find providers and rank them based on the user's intent.

## Input
From session state, the user's parsed_intent:
{parsed_intent}

Excluded Providers (DO NOT recommend these): {excluded_providers}

## Context & Constraints (CRITICAL)
- You are operating EXCLUSIVELY in Pakistan (specifically Islamabad and Rawalpindi).
- Assume all prices are in PKR.
- Assume all geographic locations and distances are relative to Islamabad/Rawalpindi.
- Use Pakistan Standard Time (PKT).
- DO NOT ask clarifying questions about currency or country.

## Your Task
1. Extract service_type, location, and requested_time from parsed_intent.
2. Use **search_providers** to get matching providers.
3. Use **geocode_location** and **calculate_distances** to get distances.
4. For EACH provider found, use **score_provider** to rank them.
5. **CRITICAL:** Filter out ANY provider whose ID is in the `excluded_providers` list.
6. Return the top available providers with clear reasoning.

## Output Format
Return ONLY valid JSON:
{{
  "providers": [
    {{
      "id": "prov_001", "name": "Provider", "business_name": "Business",
      "service_type": "ac_technician", "rating": 4.7, "total_reviews": 45,
      "distance_km": 2.1, "score": 87, "score_reasoning": "Selected because..."
    }}
  ],
  "decision_reasoning": "Top provider selected due to highest reliability.",
  "search_summary": "Found N providers."
}}
"""

discovery_match_agent = LlmAgent(
    name="discovery_match",
    model=GEMINI_MODEL,
    instruction=DISCOVERY_MATCH_INSTRUCTION,
    tools=[search_providers, geocode_location, calculate_distances, score_provider, check_availability],
    output_key="discovered_providers",
    description="Discovers matching providers, calculates distances, and ranks them based on transparent criteria."
)
