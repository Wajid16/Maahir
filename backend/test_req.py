import requests
import json

data = {
    "message": "Mujhe kal subah G-13 mein AC technician chahiye",
    "session_id": "test1"
}

response = requests.post("http://localhost:8000/api/chat", json=data)
print(json.dumps(response.json(), indent=2))
