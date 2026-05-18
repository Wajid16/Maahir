"""
Maahir — Dynamic Pricing Tools v2.0
Calculates transparent, fair pricing with full breakdowns.
Handles demand surge, urgency, complexity, distance, and loyalty.
"""

import logging
import json
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import PRICING_CONFIG

logger = logging.getLogger(__name__)


def calculate_dynamic_price(
    tool_context,
    service_type: str,
    distance_km: float,
    urgency: str,
    job_complexity: str,
    provider_min_price: int,
    provider_max_price: int,
    is_returning_customer: bool = False,
    budget_sensitivity: str = "medium",
) -> dict:
    """Calculate a dynamic, transparent price quote for a service.

    Builds a price from multiple factors with full breakdown visible to user.
    Ensures fairness for both customer (not overpaying) and provider (fair earning).

    Args:
        tool_context: ADK ToolContext for state access.
        service_type: Normalized service type (e.g. "ac_technician").
        distance_km: Distance from user to provider in km.
        urgency: "normal", "urgent", or "emergency".
        job_complexity: "basic", "intermediate", or "complex".
        provider_min_price: Provider's minimum rate (PKR).
        provider_max_price: Provider's maximum rate (PKR).
        is_returning_customer: Whether user has booked before.
        budget_sensitivity: "low", "medium", or "high".

    Returns:
        dict with final price range, full breakdown, fairness analysis, alternatives.
    """
    try:
        cfg = PRICING_CONFIG
        breakdown = []

        # ── Step 1: Base Rate ────────────────────────────────────────────
        base_rate = cfg["base_rates"].get(service_type, 2000)
        # Use provider's own rate if higher (respect their pricing)
        effective_base = max(base_rate, provider_min_price)
        breakdown.append({
            "component": "Base Service Rate",
            "component_ur": "بنیادی سروس ریٹ",
            "amount": effective_base,
            "explanation": f"Standard rate for {service_type.replace('_', ' ')} service",
            "type": "base",
        })

        # ── Step 2: Visit/Inspection Fee ─────────────────────────────────
        visit_fee = cfg["visit_fee"]
        breakdown.append({
            "component": "Visit/Inspection Fee",
            "component_ur": "معائنہ فیس",
            "amount": visit_fee,
            "explanation": "One-time visit and inspection charge",
            "type": "fixed",
        })

        # ── Step 3: Distance Surcharge ───────────────────────────────────
        free_km = cfg["distance_free_km"]
        per_km = cfg["distance_per_km"]
        distance_charge = 0
        if distance_km > free_km:
            extra_km = distance_km - free_km
            distance_charge = int(extra_km * per_km)
            breakdown.append({
                "component": "Distance Surcharge",
                "component_ur": "فاصلے کا اضافی چارج",
                "amount": distance_charge,
                "explanation": f"{extra_km:.1f}km beyond {free_km}km free zone @ PKR {per_km}/km",
                "type": "variable",
            })

        # ── Step 4: Urgency Multiplier ───────────────────────────────────
        urgency_mult = cfg["urgency_multiplier"].get(urgency, 1.0)
        urgency_charge = 0
        if urgency_mult > 1.0:
            urgency_charge = int(effective_base * (urgency_mult - 1.0))
            breakdown.append({
                "component": f"Urgency Premium ({urgency.title()})",
                "component_ur": f"فوری ضرورت ({urgency})",
                "amount": urgency_charge,
                "explanation": f"{int((urgency_mult - 1) * 100)}% surcharge for {urgency} service",
                "type": "premium",
            })

        # ── Step 5: Complexity Modifier ──────────────────────────────────
        complexity_mult = cfg["complexity_multiplier"].get(job_complexity, 1.0)
        complexity_charge = 0
        if complexity_mult > 1.0:
            complexity_charge = int(effective_base * (complexity_mult - 1.0))
            breakdown.append({
                "component": f"Complexity ({job_complexity.title()} Job)",
                "component_ur": f"کام کی پیچیدگی ({job_complexity})",
                "amount": complexity_charge,
                "explanation": f"{int((complexity_mult - 1) * 100)}% added for {job_complexity} level work",
                "type": "variable",
            })

        # ── Step 6: Demand Surge ─────────────────────────────────────────
        # Check concurrent demand from session state
        concurrent_requests = 0
        try:
            concurrent_requests = int(tool_context.state.get("demand_count", 0))
        except (ValueError, TypeError):
            pass

        surge_charge = 0
        surge_active = concurrent_requests >= cfg["surge_threshold"]
        if surge_active:
            surge_mult = cfg["surge_multiplier"]
            surge_charge = int(effective_base * (surge_mult - 1.0))
            breakdown.append({
                "component": "High Demand Surge",
                "component_ur": "زیادہ مانگ سرچارج",
                "amount": surge_charge,
                "explanation": f"{concurrent_requests} concurrent requests detected, {int((surge_mult - 1) * 100)}% surge",
                "type": "surge",
            })

        # ── Step 7: Subtotal ─────────────────────────────────────────────
        subtotal = effective_base + visit_fee + distance_charge + urgency_charge + complexity_charge + surge_charge

        # ── Step 8: Loyalty Discount ─────────────────────────────────────
        loyalty_discount = 0
        if is_returning_customer:
            loyalty_pct = cfg["loyalty_discount_pct"]
            loyalty_discount = int(subtotal * loyalty_pct / 100)
            breakdown.append({
                "component": f"Loyalty Discount (-{loyalty_pct}%)",
                "component_ur": f"وفاداری ڈسکاؤنٹ (-{loyalty_pct}%)",
                "amount": -loyalty_discount,
                "explanation": f"Returning customer discount of {loyalty_pct}%",
                "type": "discount",
            })

        # ── Final Price Range ────────────────────────────────────────────
        final_min = max(500, subtotal - loyalty_discount)
        # Max is ~40% above min to account for scope uncertainty
        final_max = int(final_min * 1.4)
        # Cap max at provider's max price if reasonable
        if provider_max_price > 0:
            final_max = min(final_max, int(provider_max_price * urgency_mult * complexity_mult))

        # Ensure min <= max
        if final_min > final_max:
            final_max = final_min + 500

        # ── Market Comparison ────────────────────────────────────────────
        market_avg = cfg["base_rates"].get(service_type, 2000)
        market_comparison = "at_market"
        if final_min < market_avg * 0.8:
            market_comparison = "below_market"
        elif final_min > market_avg * 1.3:
            market_comparison = "above_market"

        # ── Fairness Analysis ────────────────────────────────────────────
        provider_earning = final_min - visit_fee - distance_charge
        fairness = {
            "customer_fairness": "fair" if market_comparison != "above_market" else "above_average",
            "provider_fairness": "fair" if provider_earning >= provider_min_price else "below_rate",
            "market_comparison": market_comparison,
            "market_average": market_avg,
            "provider_earning_estimate": max(0, provider_earning),
            "explanation": _generate_fairness_text(market_comparison, final_min, market_avg),
        }

        # ── Budget Alternative ───────────────────────────────────────────
        budget_alternative = None
        if budget_sensitivity == "high" and final_min > market_avg:
            budget_min = int(market_avg * 0.85)
            budget_max = int(market_avg * 1.1)
            budget_alternative = {
                "price_range": {"min": budget_min, "max": budget_max, "currency": "PKR"},
                "trade_offs": [
                    "May need to wait for off-peak hours",
                    "Provider may be slightly farther away",
                    "Non-urgent scheduling only",
                ],
                "suggestion": "Book for a non-peak time or choose a provider slightly farther away to save costs.",
            }

        result = {
            "price_range": {"min": final_min, "max": final_max, "currency": "PKR"},
            "breakdown": breakdown,
            "subtotal": subtotal,
            "total_discounts": loyalty_discount,
            "surge_active": surge_active,
            "fairness": fairness,
            "budget_alternative": budget_alternative,
            "pricing_factors": {
                "base_rate": effective_base,
                "visit_fee": visit_fee,
                "distance_charge": distance_charge,
                "urgency_charge": urgency_charge,
                "complexity_charge": complexity_charge,
                "surge_charge": surge_charge,
                "loyalty_discount": loyalty_discount,
            },
            "reasoning": _generate_pricing_reasoning(
                service_type, distance_km, urgency, job_complexity,
                final_min, final_max, surge_active, budget_sensitivity
            ),
        }

        tool_context.state["price_quote"] = json.dumps(result, default=str)
        logger.info(f"Dynamic price: PKR {final_min}-{final_max} for {service_type}")
        return result

    except Exception as e:
        logger.error(f"Pricing error: {e}")
        fallback = {
            "price_range": {"min": provider_min_price or 1500, "max": provider_max_price or 5000, "currency": "PKR"},
            "breakdown": [{"component": "Estimated Range", "amount": provider_min_price, "explanation": "Based on provider's standard rates", "type": "base"}],
            "fairness": {"customer_fairness": "estimated", "market_comparison": "unknown"},
            "reasoning": f"Price estimated from provider's standard rates (error: {e})",
            "error": str(e),
        }
        tool_context.state["price_quote"] = json.dumps(fallback, default=str)
        return fallback


def get_market_average(tool_context, service_type: str, location_sector: str = "") -> dict:
    """Get average market price for a service type in an area.

    Args:
        tool_context: ADK ToolContext for state access.
        service_type: Normalized service type.
        location_sector: Optional sector for location-specific pricing.

    Returns:
        dict with average_price, price_range, sample_size.
    """
    try:
        base = PRICING_CONFIG["base_rates"].get(service_type, 2000)
        # Simulate market data from providers
        all_providers = tool_context.state.get("all_providers", [])
        if isinstance(all_providers, str):
            try:
                all_providers = json.loads(all_providers)
            except (json.JSONDecodeError, TypeError):
                all_providers = []

        prices = []
        for p in all_providers:
            if isinstance(p, dict) and p.get("service_type") == service_type:
                pr = p.get("price_range", {})
                if isinstance(pr, dict):
                    avg_p = (pr.get("min", base) + pr.get("max", base * 2)) / 2
                    prices.append(avg_p)

        if prices:
            avg_price = int(sum(prices) / len(prices))
            min_price = int(min(prices))
            max_price = int(max(prices))
        else:
            avg_price = base
            min_price = int(base * 0.7)
            max_price = int(base * 2.0)

        return {
            "service_type": service_type,
            "average_price": avg_price,
            "price_range": {"min": min_price, "max": max_price, "currency": "PKR"},
            "sample_size": len(prices),
            "location": location_sector or "Islamabad",
        }
    except Exception as e:
        return {
            "service_type": service_type,
            "average_price": PRICING_CONFIG["base_rates"].get(service_type, 2000),
            "error": str(e),
        }


def _generate_fairness_text(comparison: str, price: int, market_avg: int) -> str:
    """Generate human-readable fairness explanation."""
    diff_pct = abs(price - market_avg) / max(market_avg, 1) * 100
    if comparison == "below_market":
        return f"This quote is {diff_pct:.0f}% below the market average of PKR {market_avg}. Great value for the customer."
    elif comparison == "above_market":
        return f"This quote is {diff_pct:.0f}% above the market average of PKR {market_avg} due to urgency/distance factors."
    return f"This quote is in line with the market average of PKR {market_avg}. Fair for both parties."


def _generate_pricing_reasoning(
    service_type, distance_km, urgency, complexity,
    final_min, final_max, surge_active, budget_sensitivity
) -> str:
    """Generate transparent pricing reasoning text."""
    parts = [f"Calculated dynamic price for {service_type.replace('_', ' ')} service."]

    if distance_km > 3:
        parts.append(f"Distance surcharge applied: provider is {distance_km:.1f}km away (beyond 3km free zone).")
    else:
        parts.append(f"No distance surcharge — provider is within {distance_km:.1f}km free zone.")

    if urgency != "normal":
        parts.append(f"Urgency premium applied: request marked as '{urgency}'.")

    if complexity != "basic":
        parts.append(f"Complexity modifier: job classified as '{complexity}' level work.")

    if surge_active:
        parts.append("High demand detected — temporary surge pricing is active.")

    if budget_sensitivity == "high":
        parts.append("User indicated budget sensitivity — budget-friendly alternative provided.")

    parts.append(f"Final quote: PKR {final_min:,} - {final_max:,}.")
    return " ".join(parts)
