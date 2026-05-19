import requests
import json
import sys

def test_stream():
    url = "http://localhost:8000/api/chat_stream" # Wait, let's test localhost first if it's running
    payload = {"message": "I need an AC technician tomorrow in G-13", "session_id": "test_stream_123"}
    try:
        response = requests.post(url, json=payload, stream=True)
        for line in response.iter_lines():
            if line:
                print(line.decode('utf-8'))
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_stream()
