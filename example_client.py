"""
Example client script to demonstrate API usage
"""
import requests
import json
import time
import random

BASE_URL = "http://localhost:8000"

def track_event(user_id: str, item_id: str, event_type: str):
    """Track a user event"""
    response = requests.post(
        f"{BASE_URL}/events",
        json={
            "user_id": user_id,
            "item_id": item_id,
            "event_type": event_type,
            "metadata": {
                "source": "example_client",
                "timestamp": time.time()
            }
        }
    )
    return response.json()


def get_recommendations(user_id: str, limit: int = 10):
    """Get recommendations for a user"""
    response = requests.post(
        f"{BASE_URL}/recommendations",
        json={
            "user_id": user_id,
            "limit": limit
        }
    )
    return response.json()


def get_user_history(user_id: str):
    """Get user's event history"""
    response = requests.get(f"{BASE_URL}/users/{user_id}/history")
    return response.json()


def main():
    """Example usage"""
    print("🚀 Recommendation System Client Example\n")
    
    # Check health
    print("1. Health Check...")
    health = requests.get(f"{BASE_URL}/").json()
    print(f"   Status: {health['status']}")
    print(f"   DynamoDB: {health['dynamodb_status']}")
    print(f"   Cache: {health['cache_status']}\n")
    
    # Simulate user activity
    user_id = "user_example_123"
    items = [f"item_{i}" for i in range(1, 21)]
    event_types = ['view', 'click', 'like', 'add_to_cart']
    
    print(f"2. Tracking events for user: {user_id}")
    for i in range(10):
        item = random.choice(items)
        event_type = random.choice(event_types)
        result = track_event(user_id, item, event_type)
        print(f"   ✓ Tracked: {event_type} on {item}")
        time.sleep(0.1)
    
    print("\n3. Getting recommendations...")
    recommendations = get_recommendations(user_id, limit=5)
    print(f"   Response time: {recommendations['response_time_ms']:.2f}ms")
    print(f"   Cache hit: {recommendations['cache_hit']}")
    print(f"   Recommendations:")
    for i, rec in enumerate(recommendations['recommendations'], 1):
        print(f"   {i}. {rec['item_id']} (score: {rec['score']:.3f}) - {rec['reason']}")
    
    print("\n4. Getting user history...")
    history = get_user_history(user_id)
    print(f"   Total events: {history['count']}")
    
    print("\n5. Getting metrics...")
    metrics = requests.get(f"{BASE_URL}/metrics").json()
    print(f"   Cache stats: {json.dumps(metrics['cache'], indent=2)}")
    
    print("\n✅ Example complete!")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API.")
        print("   Make sure the FastAPI server is running:")
        print("   uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")

