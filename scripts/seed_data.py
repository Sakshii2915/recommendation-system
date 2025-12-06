"""
Script to seed sample data for testing
"""
import asyncio
import random
import time
from app.dynamodb_client import DynamoDBClient

# Sample data
USERS = [f"user_{i}" for i in range(1, 101)]  # 100 users
ITEMS = [f"item_{i}" for i in range(1, 201)]  # 200 items
EVENT_TYPES = ['view', 'click', 'like', 'add_to_cart', 'purchase']


async def seed_events(num_events=1000):
    """Seed user events"""
    client = DynamoDBClient()
    
    print(f"Seeding {num_events} events...")
    
    for i in range(num_events):
        user_id = random.choice(USERS)
        item_id = random.choice(ITEMS)
        event_type = random.choice(EVENT_TYPES)
        timestamp = time.time() - random.randint(0, 86400 * 7)  # Last 7 days
        
        success = await client.put_user_event(
            user_id=user_id,
            item_id=item_id,
            event_type=event_type,
            timestamp=timestamp,
            metadata={'source': 'seed_script'}
        )
        
        if success and (i + 1) % 100 == 0:
            print(f"Seeded {i + 1} events...")
    
    print(f"✅ Seeded {num_events} events successfully!")


if __name__ == "__main__":
    asyncio.run(seed_events(1000))

