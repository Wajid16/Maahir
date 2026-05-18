"""Enhance existing mock_providers.json with v2 fields."""
import json, random, os

path = os.path.join(os.path.dirname(__file__), "mock_providers.json")
with open(path, "r", encoding="utf-8") as f:
    providers = json.load(f)

CERTS_BY_TYPE = {
    "ac_technician": ["AC Repair Level 2", "Gas Handling Safety", "HVAC Maintenance", "Inverter AC Specialist"],
    "plumber": ["Pipe Fitting", "Water Heater Installation", "Sanitary Works", "Solar Geyser Setup"],
    "electrician": ["Electrical Safety", "Solar Panel Install", "UPS/Inverter Wiring", "Industrial Wiring"],
    "painter": ["Decorative Painting", "Waterproofing", "Epoxy Flooring", "Texture Specialist"],
    "carpenter": ["Furniture Making", "Wood Polishing", "Cabinet Installation", "Door/Window Fitting"],
    "tutor": ["Board Exam Prep", "O/A Level Specialist", "STEM Teaching", "Language Teaching"],
    "beautician": ["Bridal Makeup", "Hair Styling", "Skin Care", "Mehndi Artist"],
    "cook": ["Pakistani Cuisine", "BBQ Specialist", "Catering", "Baking"],
    "driver": ["City Navigation", "Long Route", "Defensive Driving", "AC Vehicle"],
    "pest_control": ["Termite Treatment", "Fumigation Safety", "Organic Pest Control", "Rodent Control"],
}

TOOLS_BY_TYPE = {
    "ac_technician": ["AC gas kit", "Multimeter", "Vacuum pump", "Flare tool", "Manifold gauge"],
    "plumber": ["Pipe wrench", "Plunger", "Thread seal tape", "Pipe cutter", "Soldering kit"],
    "electrician": ["Wire stripper", "Multimeter", "Circuit tester", "Drill machine", "Cable ties"],
    "painter": ["Spray gun", "Roller set", "Masking tape", "Putty knife", "Sandpaper kit"],
    "carpenter": ["Power drill", "Circular saw", "Chisel set", "Measuring tape", "Wood glue"],
    "tutor": ["Whiteboard", "Tablet", "Study materials", "Past papers"],
    "beautician": ["Makeup kit", "Hair dryer", "Straightener", "Facial kit", "Wax heater"],
    "cook": ["Knife set", "Portable stove", "Spice kit", "BBQ grill"],
    "driver": ["GPS device", "First aid kit", "Phone mount"],
    "pest_control": ["Spray machine", "Safety mask", "Chemical kit", "Inspection torch"],
}

REVIEW_TEXTS = {
    5: ["بہت اچھا کام کیا", "Excellent work, very professional", "10/10 would recommend", "Bahut acha kaam kiya, time pe aaya"],
    4: ["Good work overall", "Acha kaam tha, recommended", "Satisfied with the service", "Time pe aaya aur kaam bhi theek kiya"],
    3: ["Average work, could be better", "Theek tha, not great", "Kaam ho gaya but quality average thi"],
    2: ["Late aaya aur kaam bhi slow tha", "Not satisfied, overcharged", "Poor communication"],
    1: ["Worst experience, nahi aaya time pe", "Very bad quality, had to call someone else"],
}

TRANSPORT = ["motorcycle", "rickshaw", "car", "bicycle", "walk"]

for p in providers:
    st = p.get("service_type", "")
    rating = p.get("rating", 3.5)
    exp = p.get("experience_years", 5)

    # Certifications (more for experienced)
    avail_certs = CERTS_BY_TYPE.get(st, ["General"])
    n_certs = min(len(avail_certs), max(1, exp // 4))
    p["certifications"] = random.sample(avail_certs, n_certs)

    # Tools owned
    avail_tools = TOOLS_BY_TYPE.get(st, ["Basic toolkit"])
    n_tools = min(len(avail_tools), max(2, exp // 3))
    p["tools_owned"] = random.sample(avail_tools, n_tools)

    # Recent reviews (3-6 reviews)
    n_reviews = random.randint(3, 6)
    reviews = []
    for i in range(n_reviews):
        r_rating = max(1, min(5, int(rating + random.gauss(0, 0.8))))
        texts = REVIEW_TEXTS.get(r_rating, REVIEW_TEXTS[3])
        reviews.append({
            "rating": r_rating,
            "text": random.choice(texts),
            "days_ago": random.randint(1, 45),
        })
    reviews.sort(key=lambda x: x["days_ago"])
    p["recent_reviews"] = reviews

    # Workload fields
    p["completed_jobs_30d"] = random.randint(5, 25)
    p["active_bookings_today"] = random.randint(0, 3)
    p["complaint_rate"] = round(random.uniform(0, 8), 1)
    p["preferred_areas"] = random.sample(
        ["G-13", "G-14", "G-11", "G-10", "F-8", "F-10", "F-11", "I-8", "I-10", "H-8", "Blue Area"],
        k=random.randint(2, 4)
    )
    p["transport_mode"] = random.choices(TRANSPORT, weights=[50, 15, 20, 10, 5])[0]
    p["average_completion_time_min"] = random.choice([45, 60, 75, 90, 120])
    p["gender"] = random.choice(["male", "male", "male", "female"])  # Reflects Pakistan demographics
    # Ensure existing fields have sensible values
    if "response_time_minutes" not in p:
        p["response_time_minutes"] = random.choice([15, 30, 45, 60])

with open(path, "w", encoding="utf-8") as f:
    json.dump(providers, f, indent=2, ensure_ascii=False)

print(f"Enhanced {len(providers)} providers with v2 fields")
print(f"Sample certifications: {providers[0].get('certifications')}")
print(f"Sample reviews: {len(providers[0].get('recent_reviews', []))}")
