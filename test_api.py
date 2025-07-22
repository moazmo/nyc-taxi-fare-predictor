"""
Simple test script for the taxi fare prediction API.
"""

import requests
import json

def test_health():
    """Test the health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get("http://localhost:8000/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_prediction():
    """Test the prediction endpoint"""
    print("🚖 Testing prediction endpoint...")
    
    # Sample data: Manhattan pickup and dropoff
    test_data = {
        "pickup_longitude": -73.984,
        "pickup_latitude": 40.748,
        "dropoff_longitude": -73.973,
        "dropoff_latitude": 40.764,
        "passenger_count": 1
    }
    
    response = requests.post(
        "http://localhost:8000/predict",
        headers={"Content-Type": "application/json"},
        json=test_data
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Predicted fare: ${result['predicted_fare']:.2f}")
        print(f"Confidence: {result['confidence']:.1%}")
        print(f"Distance: {result['distance_miles']:.2f} miles")
    else:
        print(f"Error: {response.text}")
    print()

def test_docs():
    """Test the API documentation endpoint"""
    print("📚 Testing API documentation...")
    response = requests.get("http://localhost:8000/docs")
    print(f"Docs available: {response.status_code == 200}")
    print()

if __name__ == "__main__":
    print("🚀 Starting API tests...\n")
    
    try:
        test_health()
        test_prediction()
        test_docs()
        print("✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed: {e}")
