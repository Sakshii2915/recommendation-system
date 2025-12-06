"""
Local storage implementation for testing without AWS
Uses in-memory storage and JSON files
"""
import json
import os
import time
from typing import List, Dict, Optional
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class LocalStorage:
    """Local file-based storage for testing without AWS"""
    
    def __init__(self, data_dir: str = "local_data"):
        self.data_dir = data_dir
        self.events_file = os.path.join(data_dir, "events.json")
        self.recommendations_file = os.path.join(data_dir, "recommendations.json")
        self.popular_items_file = os.path.join(data_dir, "popular_items.json")
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # In-memory storage for fast access
        self.events = defaultdict(list)
        self.recommendations = {}
        self.popular_items = []
        
        # Load existing data
        self._load_data()
    
    def _load_data(self):
        """Load data from JSON files"""
        try:
            if os.path.exists(self.events_file):
                with open(self.events_file, 'r') as f:
                    data = json.load(f)
                    self.events = defaultdict(list, {k: v for k, v in data.items()})
        except Exception as e:
            logger.warning(f"Could not load events: {e}")
        
        try:
            if os.path.exists(self.recommendations_file):
                with open(self.recommendations_file, 'r') as f:
                    self.recommendations = json.load(f)
        except Exception as e:
            logger.warning(f"Could not load recommendations: {e}")
    
    def _save_events(self):
        """Save events to file"""
        try:
            with open(self.events_file, 'w') as f:
                json.dump(dict(self.events), f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save events: {e}")
    
    def put_user_event(self, user_id: str, item_id: str, event_type: str, 
                      timestamp: float, metadata: Dict = None) -> bool:
        """Store a user event"""
        event = {
            'event_id': f"{user_id}_{item_id}_{int(timestamp)}",
            'user_id': user_id,
            'item_id': item_id,
            'event_type': event_type,
            'timestamp': timestamp,
            'metadata': metadata or {}
        }
        
        self.events[user_id].append(event)
        # Keep only last 1000 events per user
        if len(self.events[user_id]) > 1000:
            self.events[user_id] = self.events[user_id][-1000:]
        
        self._save_events()
        return True
    
    def get_user_events(self, user_id: str, limit: int = 100) -> List[Dict]:
        """Get user's events"""
        events = self.events.get(user_id, [])
        # Sort by timestamp descending
        events.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        return events[:limit]
    
    def get_users_by_items(self, item_ids: List[str], limit: int = 100) -> List[str]:
        """Get users who interacted with given items"""
        user_set = set()
        
        for user_id, events in self.events.items():
            for event in events:
                if event.get('item_id') in item_ids:
                    user_set.add(user_id)
                    if len(user_set) >= limit:
                        return list(user_set)
        
        return list(user_set)
    
    def get_popular_items(self, limit: int = 10) -> List[Dict]:
        """Get popular items"""
        # Count item interactions
        item_counts = defaultdict(int)
        
        for events in self.events.values():
            for event in events:
                item_id = event.get('item_id')
                if item_id:
                    item_counts[item_id] += 1
        
        # Sort by count
        sorted_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {
                'item_id': item_id,
                'popularity_score': float(count)
            }
            for item_id, count in sorted_items[:limit]
        ]
    
    def save_recommendations(self, user_id: str, recommendations: List[Dict]) -> bool:
        """Save recommendations for a user"""
        self.recommendations[user_id] = {
            'recommendations': recommendations,
            'updated_at': time.time()
        }
        
        try:
            with open(self.recommendations_file, 'w') as f:
                json.dump(self.recommendations, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save recommendations: {e}")
        
        return True

