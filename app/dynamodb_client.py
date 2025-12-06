"""
DynamoDB Client for storing and retrieving user events
Optimized for low-latency reads and writes
"""
import os
import logging
import boto3
import time
from botocore.exceptions import ClientError
from typing import List, Dict, Optional
from decimal import Decimal
import json

logger = logging.getLogger(__name__)


class DynamoDBClient:
    """DynamoDB client for user events and recommendations"""
    
    def __init__(self):
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        self.events_table = os.getenv('EVENTS_TABLE_NAME', 'UserEvents')
        self.recommendations_table = os.getenv('RECOMMENDATIONS_TABLE_NAME', 'UserRecommendations')
        
        # Use DAX if endpoint is provided, otherwise use regular DynamoDB
        dax_endpoint = os.getenv('DAX_ENDPOINT', None)
        if dax_endpoint:
            try:
                from amazondax import AmazonDaxClient
                self.dynamodb = AmazonDaxClient(
                    endpoint_url=dax_endpoint,
                    region_name=self.region
                )
                logger.info(f"Using DAX endpoint: {dax_endpoint}")
            except ImportError:
                logger.warning("DAX not available, using regular DynamoDB")
                self.dynamodb = boto3.resource('dynamodb', region_name=self.region)
            except Exception as e:
                logger.warning(f"DAX initialization failed: {e}, using regular DynamoDB")
                self.dynamodb = boto3.resource('dynamodb', region_name=self.region)
        else:
            self.dynamodb = boto3.resource('dynamodb', region_name=self.region)
        
        self.events_table_resource = None
        self.recommendations_table_resource = None
        self._initialize_tables()
    
    def _initialize_tables(self):
        """Initialize table resources"""
        try:
            self.events_table_resource = self.dynamodb.Table(self.events_table)
            self.recommendations_table_resource = self.dynamodb.Table(self.recommendations_table)
        except Exception as e:
            logger.warning(f"Tables may not exist yet: {e}")
    
    def is_connected(self) -> bool:
        """Check if DynamoDB connection is active"""
        try:
            if self.events_table_resource:
                self.events_table_resource.meta.client.describe_table(TableName=self.events_table)
            return True
        except Exception:
            return False
    
    async def put_user_event(
        self,
        user_id: str,
        item_id: str,
        event_type: str,
        timestamp: float,
        metadata: Dict = None
    ) -> bool:
        """
        Store user event in DynamoDB
        
        Args:
            user_id: User identifier
            item_id: Item identifier
            event_type: Type of event
            timestamp: Event timestamp
            metadata: Additional metadata
        
        Returns:
            True if successful
        """
        try:
            event_id = f"{user_id}_{item_id}_{int(timestamp)}"
            
            item = {
                'event_id': event_id,
                'user_id': user_id,
                'item_id': item_id,
                'event_type': event_type,
                'timestamp': Decimal(str(timestamp)),
                'metadata': json.dumps(metadata or {}),
                'ttl': int(timestamp) + (365 * 24 * 60 * 60)  # 1 year TTL
            }
            
            if not self.events_table_resource:
                self._initialize_tables()
            
            self.events_table_resource.put_item(Item=item)
            
            # Also update user-item index for faster queries
            self._update_user_item_index(user_id, item_id, event_type, timestamp)
            
            return True
        
        except Exception as e:
            logger.error(f"Error putting user event: {e}")
            return False
    
    def _update_user_item_index(self, user_id: str, item_id: str, event_type: str, timestamp: float):
        """Update user-item index for faster similarity calculations"""
        try:
            # This would update a GSI or separate table for user-item relationships
            # For simplicity, we'll use the same table with a different key structure
            pass
        except Exception as e:
            logger.debug(f"Index update error (non-critical): {e}")
    
    async def get_user_events(self, user_id: str, limit: int = 100) -> List[Dict]:
        """
        Get user's event history
        
        Args:
            user_id: User identifier
            limit: Maximum number of events to return
        
        Returns:
            List of user events
        """
        try:
            if not self.events_table_resource:
                self._initialize_tables()
            
            response = self.events_table_resource.query(
                IndexName='user_id-timestamp-index',
                KeyConditionExpression='user_id = :uid',
                ExpressionAttributeValues={
                    ':uid': user_id
                },
                ScanIndexForward=False,  # Most recent first
                Limit=limit
            )
            
            events = []
            for item in response.get('Items', []):
                events.append({
                    'event_id': item.get('event_id'),
                    'user_id': item.get('user_id'),
                    'item_id': item.get('item_id'),
                    'event_type': item.get('event_type'),
                    'timestamp': float(item.get('timestamp', 0)),
                    'metadata': json.loads(item.get('metadata', '{}'))
                })
            
            return events
        
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.warning("Table or index does not exist yet")
                return []
            logger.error(f"Error getting user events: {e}")
            return []
        except Exception as e:
            logger.error(f"Error getting user events: {e}")
            return []
    
    async def get_users_by_items(self, item_ids: List[str], limit: int = 100) -> List[str]:
        """
        Get users who interacted with given items
        
        Args:
            item_ids: List of item identifiers
            limit: Maximum number of users to return
        
        Returns:
            List of user IDs
        """
        try:
            if not self.events_table_resource:
                self._initialize_tables()
            
            user_set = set()
            
            # Query for each item (in production, use batch operations)
            for item_id in item_ids[:10]:  # Limit to avoid too many queries
                response = self.events_table_resource.query(
                    IndexName='item_id-timestamp-index',
                    KeyConditionExpression='item_id = :iid',
                    ExpressionAttributeValues={
                        ':iid': item_id
                    },
                    Limit=20
                )
                
                for item in response.get('Items', []):
                    user_set.add(item.get('user_id'))
                    if len(user_set) >= limit:
                        break
                
                if len(user_set) >= limit:
                    break
            
            return list(user_set)
        
        except Exception as e:
            logger.error(f"Error getting users by items: {e}")
            return []
    
    async def get_popular_items(self, limit: int = 10) -> List[Dict]:
        """
        Get popular items based on interaction count
        
        Args:
            limit: Number of items to return
        
        Returns:
            List of popular items with scores
        """
        try:
            # In production, this would use a pre-computed popular items table
            # For now, return sample data
            return [
                {
                    'item_id': f'popular_item_{i}',
                    'popularity_score': 100.0 - (i * 5)
                }
                for i in range(limit)
            ]
        except Exception as e:
            logger.error(f"Error getting popular items: {e}")
            return []
    
    async def save_recommendations(self, user_id: str, recommendations: List[Dict]):
        """Save generated recommendations for a user"""
        try:
            if not self.recommendations_table_resource:
                self._initialize_tables()
            
            item = {
                'user_id': user_id,
                'recommendations': json.dumps(recommendations),
                'updated_at': Decimal(str(int(time.time())))
            }
            
            self.recommendations_table_resource.put_item(Item=item)
            return True
        
        except Exception as e:
            logger.error(f"Error saving recommendations: {e}")
            return False

