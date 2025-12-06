"""
Load testing script for Locust
Run with: locust -f tests/load_test.py --host=http://localhost:8000
"""
from locust import HttpUser, task, between


class RecommendationUser(HttpUser):
    """Simulate user behavior for load testing"""
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called when a user starts"""
        self.user_id = f"user_{self.environment.runner.user_count}"
    
    @task(3)
    def track_event(self):
        """Track a user event (most common operation)"""
        self.client.post("/events", json={
            "user_id": self.user_id,
            "item_id": f"item_{self.user_id}",
            "event_type": "view"
        })
    
    @task(1)
    def get_recommendations(self):
        """Get recommendations (less frequent)"""
        self.client.post("/recommendations", json={
            "user_id": self.user_id,
            "limit": 10
        })
    
    @task(1)
    def get_user_history(self):
        """Get user history"""
        self.client.get(f"/users/{self.user_id}/history")
    
    @task(1)
    def health_check(self):
        """Health check"""
        self.client.get("/")

