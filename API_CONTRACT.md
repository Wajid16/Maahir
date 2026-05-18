# Maahir API Contract v2.0

## Base URL
```
http://localhost:8000
```

## Endpoints

### POST /api/chat
Main endpoint. Processes user messages through the 8-agent pipeline.

**Request:**
```json
{
  "message": "AC bilkul kaam nahi kar raha, G-13 mein kal subah chahiye",
  "session_id": "uuid-v4",
  "language": "auto"
}
```

**Response:**
```json
{
  "response": "Bilingual response text...",
  "trace_steps": [
    {
      "agent": "intent_parser | provider_discovery | matcher | pricing | scheduling | booking | followup | dispute_handler",
      "status": "completed | skipped | error",
      "summary": "Short summary of agent action",
      "detail": "Full JSON payload from agent",
      "duration_ms": 1240,
      "tools_used": ["tool_name"],
      "reasoning": "Gemini's explicit reasoning for this decision"
    }
  ],
  "providers": [
    {
      "id": "prov_001", "name": "Ali Hassan", "business_name": "Ali AC Services",
      "service_type": "ac_technician", "services": ["AC repair"],
      "rating": 4.7, "total_reviews": 45, "distance_km": 2.1,
      "price_range": {"min": 1500, "max": 5000, "currency": "PKR"},
      "experience_years": 8, "phone": "+92-300-1234567", "verified": true,
      "location": {"sector": "G-13", "city": "Islamabad", "lat": 33.64, "lng": 72.97},
      "score": 92, "score_reasoning": "Highest reliability + closest + specialization",
      "score_breakdown": {
        "distance": {"score": 85, "weighted": 10.2, "reasoning": "2.1km away"},
        "rating": {"score": 94, "weighted": 14.1, "reasoning": "4.7/5 stars"},
        "reliability": {"score": 97, "weighted": 14.5, "reasoning": "97% on-time"},
        "skill_match": {"score": 100, "weighted": 12.0, "reasoning": "Perfect match"},
        "risk_score": {"score": 88, "weighted": 7.0, "reasoning": "Low risk"}
      }
    }
  ],
  "booking": {
    "id": "book_xxx", "provider_id": "prov_001", "provider_name": "Ali AC Services",
    "service_type": "ac_technician", "scheduled_time": "ISO datetime",
    "estimated_price": {"min": 2500, "max": 3500, "currency": "PKR"},
    "status": "confirmed", "confirmation_message": "...", "reminder_time": "ISO"
  },
  "pricing": {
    "price_range": {"min": 2500, "max": 3500, "currency": "PKR"},
    "breakdown": [
      {"component": "Base Rate", "amount": 2000, "explanation": "AC technician standard", "type": "base"},
      {"component": "Visit Fee", "amount": 500, "explanation": "Inspection charge", "type": "fixed"},
      {"component": "Distance", "amount": 200, "explanation": "2km beyond free zone", "type": "variable"}
    ],
    "market_average": 2000,
    "fairness": "at_market | below_market | above_market",
    "budget_alternative": null,
    "reasoning": "Full pricing reasoning..."
  },
  "scheduling": {
    "slot_available": true,
    "confirmed_time": "ISO datetime",
    "has_conflicts": false,
    "alternative_slots": [],
    "provider_workload": {"bookings_today": 2, "utilization_pct": 33.3},
    "reasoning": "No conflicts. 30min buffer applied."
  },
  "dispute": null,
  "needs_clarification": false,
  "clarification_question": null
}
```

### GET /api/health
Returns backend status, version, model, and pipeline info.

### GET /api/trace/{session_id}
Returns all trace steps for a session.

### POST /api/dispute
File a dispute for a completed booking.

**Request:**
```json
{
  "booking_id": "book_xxx",
  "dispute_type": "no_show | late_arrival | quality_complaint | price_disagreement | cancellation_by_provider",
  "description": "Provider didn't arrive...",
  "session_id": "uuid"
}
```

### GET /api/stress-test
Runs all 6 challenge stress-test scenarios and returns results.

## 8-Agent Pipeline
```
Intent Parser → Provider Discovery → Matcher (10 factors) → Pricing → Scheduling → Booking → Follow-Up → Dispute Handler
```

## 10 Scoring Factors
| Factor | Weight | Description |
|--------|--------|-------------|
| distance | 12% | Haversine + travel time |
| rating | 15% | Overall star rating |
| review_recency | 8% | Penalize stale reviews |
| review_sentiment | 7% | Recent review analysis |
| reliability | 15% | On-time minus cancellations |
| skill_match | 12% | Skills vs job complexity |
| price | 10% | Cost competitiveness |
| capacity | 8% | Workload/availability |
| user_preference | 5% | Language, verified, gender |
| risk_score | 8% | Composite risk indicator |
