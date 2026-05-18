import json
import random
import os

SECTORS = [
    {"sector": "G-6", "lat": 33.7294, "lng": 73.0931},
    {"sector": "G-7", "lat": 33.7215, "lng": 73.0760},
    {"sector": "G-8", "lat": 33.7107, "lng": 73.0483},
    {"sector": "G-9", "lat": 33.7073, "lng": 73.0349},
    {"sector": "G-10", "lat": 33.7000, "lng": 73.0118},
    {"sector": "G-11", "lat": 33.6904, "lng": 72.9934},
    {"sector": "G-13", "lat": 33.6425, "lng": 72.9785},
    {"sector": "F-6", "lat": 33.7294, "lng": 73.0890},
    {"sector": "F-7", "lat": 33.7215, "lng": 73.0760},
    {"sector": "F-8", "lat": 33.7107, "lng": 73.0550},
    {"sector": "F-10", "lat": 33.7000, "lng": 73.0200},
    {"sector": "F-11", "lat": 33.6904, "lng": 73.0050},
    {"sector": "I-8", "lat": 33.6950, "lng": 73.0800},
    {"sector": "I-10", "lat": 33.6600, "lng": 73.0100},
    {"sector": "Blue Area", "lat": 33.7100, "lng": 73.0500},
    {"sector": "Bahria Town", "lat": 33.5200, "lng": 73.0900}
]

SERVICE_INFO = {
    "ac_technician": {"services": ["AC repair", "AC installation", "AC gas refill", "AC maintenance"], "min_p": 1500, "max_p": 5000},
    "plumber": {"services": ["Pipe repair", "Leak fixing", "Bathroom fitting", "Water heater installation"], "min_p": 500, "max_p": 3000},
    "electrician": {"services": ["Wiring", "Short circuit repair", "UPS installation", "Generator repair"], "min_p": 800, "max_p": 4000},
    "painter": {"services": ["House painting", "Wall texturing", "Waterproofing", "Polish work"], "min_p": 5000, "max_p": 15000},
    "carpenter": {"services": ["Furniture repair", "Door lock fix", "Cabinet making", "Wood polishing"], "min_p": 1000, "max_p": 8000},
    "tutor": {"services": ["Math tutoring", "Science tutoring", "English tutoring", "Exam preparation"], "min_p": 2000, "max_p": 8000},
    "beautician": {"services": ["Bridal makeup", "Party makeup", "Hair cutting", "Facial"], "min_p": 2000, "max_p": 15000},
    "cook": {"services": ["Daily cooking", "Event catering", "Baking", "Diet meals"], "min_p": 1500, "max_p": 5000},
    "driver": {"services": ["Daily drop/pick", "Monthly driving", "Out of city trips"], "min_p": 1000, "max_p": 3000},
    "pest_control": {"services": ["Termite treatment", "Bed bug removal", "General fumigation"], "min_p": 2500, "max_p": 8000}
}

NAMES = [
    "Ali Hassan", "Ahmad Khan", "Bilal Tariq", "Kamran Ahmed", "Tariq Mahmood", 
    "Nazia Bibi", "Saima Noor", "Imran Shah", "Faisal Raza", "Usman Sheikh", 
    "Zainab Ali", "Farhan Saeed", "Noman Qureshi", "Ayesha Siddiqa", "Nida Khan", 
    "Yasir Hussain", "Adnan Sami", "Hafiz Zubair", "Khurram Manzoor", "Saad Rafique", 
    "Amir Jamil", "Waqas Mian", "Sana Mir", "Mariya Shafiq", "Shoaib Akhtar", 
    "Rizwan Iqbal", "Hamza Ali", "Javed Miandad", "Rabia Anum", "Sadia Imam", 
    "Tahir Shah", "Umer Gul", "Danish Taimoor", "Asad Shafiq", "Babar Azam"
]

random.seed(123)

def generate_availability():
    has_limited = random.random() < 0.2
    if has_limited:
        return [
            {"day": "monday", "slots": ["10:00-14:00"]},
            {"day": "tuesday", "slots": ["10:00-14:00"]},
            {"day": "wednesday", "slots": []},
            {"day": "thursday", "slots": ["10:00-14:00"]},
            {"day": "friday", "slots": []},
            {"day": "saturday", "slots": ["10:00-18:00"]},
            {"day": "sunday", "slots": ["10:00-18:00"]}
        ]
    else:
        return [
            {"day": "monday", "slots": ["09:00-12:00", "14:00-18:00"]},
            {"day": "tuesday", "slots": ["09:00-12:00", "14:00-18:00"]},
            {"day": "wednesday", "slots": ["09:00-12:00", "14:00-18:00"]},
            {"day": "thursday", "slots": ["09:00-12:00", "14:00-18:00"]},
            {"day": "friday", "slots": ["09:00-12:00"]},
            {"day": "saturday", "slots": ["10:00-14:00"]},
            {"day": "sunday", "slots": []}
        ]

providers = []
service_types = list(SERVICE_INFO.keys())
types_to_assign = service_types * 3
types_to_assign += random.choices(service_types, k=5)
random.shuffle(types_to_assign)

for i in range(35):
    srv_type = types_to_assign[i]
    info = SERVICE_INFO[srv_type]
    name = NAMES[i % len(NAMES)]
    first_name = name.split()[0]
    
    biz_names = [
        f"{first_name} Services", 
        f"{first_name} {srv_type.replace('_', ' ').title()}", 
        f"{name} Professionals", 
        f"Expert {srv_type.replace('_', ' ').title()} by {first_name}"
    ]
    
    sector_info = random.choice(SECTORS)
    
    min_p = info["min_p"] + random.randint(-5, 5) * 100
    max_p = info["max_p"] + random.randint(-5, 20) * 100
    if min_p >= max_p:
        max_p = min_p + 1000
        
    provider = {
        "id": f"prov_{(i+1):03d}",
        "name": name,
        "business_name": random.choice(biz_names),
        "service_type": srv_type,
        "services": random.sample(info["services"], k=random.randint(2, len(info["services"]))),
        "rating": round(random.uniform(3.2, 4.9), 1),
        "total_reviews": random.randint(2, 150),
        "experience_years": random.randint(1, 20),
        "phone": f"+92-3{random.randint(0,4)}{random.randint(0,9)}-{random.randint(1000000, 9999999)}",
        "verified": random.random() < 0.8,
        "location": {
            "sector": sector_info["sector"],
            "city": "Islamabad",
            "lat": round(sector_info["lat"] + random.uniform(-0.005, 0.005), 4),
            "lng": round(sector_info["lng"] + random.uniform(-0.005, 0.005), 4)
        },
        "price_range": {
            "min": max(100, min_p),
            "max": max_p,
            "currency": "PKR"
        },
        "availability": generate_availability(),
        "languages": ["Urdu"] if random.random() < 0.3 else ["Urdu", "English"],
        "response_time_minutes": random.choice([15, 30, 45, 60, 120]),
        "reliability_score": round(random.uniform(70, 100), 1),
        "cancellation_rate": round(random.uniform(0, 15), 1),
        "review_recency_days": random.randint(1, 45),
        "job_complexity_skills": random.choice([
            ["basic"],
            ["basic", "intermediate"],
            ["basic", "intermediate", "complex"]
        ])
    }
    providers.append(provider)

output_path = os.path.join(os.path.dirname(__file__), "mock_providers.json")
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(providers, f, indent=2)
print(f"Successfully generated {len(providers)} providers to {output_path}")
