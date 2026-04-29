import sys
import os

# Add the current directory to sys.path to allow imports from 'app'
sys.path.append(os.getcwd())

from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)
internal_key = "hela-secret-123"
headers = {"X-Internal-Key": internal_key}

def test_health():
    print("Testing /api/v1/health...")
    response = client.get("/api/v1/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_chat():
    print("\nTesting /api/v1/chat...")
    payload = {
        "patient_id": "123",
        "patient_symptoms": "Rani nhas b dawkha w skhana",
        "patient_data": {
            "age": 65,
            "systolic_bp": 155,
            "diastolic_bp": 95,
            "fasting_glucose": 140,
            "bmi": 27,
            "smoking": False,
            "family_history": True,
            "comorbidities": 1
        },
        "include_glossary": True
    }
    response = client.post("/api/v1/chat", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Hela Response: {data.get('hela_response')[:100]}...")
        print(f"Risk Score: {data.get('risk_score')}")
    else:
        print(f"Error: {response.text}")
    return response.status_code == 200

def test_glossary_search():
    print("\nTesting /api/v1/glossary/search...")
    payload = {"query": "السكري", "limit": 2, "language": "darija"}
    response = client.post("/api/v1/glossary/search", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Results found: {len(response.json())}")
    return response.status_code == 200

def test_drift_check():
    print("\nTesting /api/v1/patient/123/check-drift...")
    response = client.get("/api/v1/patient/123/check-drift", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

if __name__ == "__main__":
    results = [
        test_health(),
        test_chat(),
        test_glossary_search(),
        test_drift_check()
    ]
    
    if all(results):
        print("\n✅ All endpoints tested successfully!")
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)
