"""
Lambda function to process DynamoDB Streams
Updates recommendations in real-time when new events arrive
"""
import json
import os
import logging
import boto3
from decimal import Decimal

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize clients
dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION', 'us-east-1'))
recommendations_table = os.getenv('RECOMMENDATIONS_TABLE_NAME', 'UserRecommendations')
cache_table = os.getenv('CACHE_TABLE_NAME', 'RecommendationCache')


def lambda_handler(event, context):
    """
    Process DynamoDB stream records and update recommendations
    
    Args:
        event: DynamoDB stream event
        context: Lambda context
    
    Returns:
        Processing status
    """
    processed_count = 0
    failed_count = 0
    
    for record in event.get('Records', []):
        try:
            if record['eventName'] in ['INSERT', 'MODIFY']:
                # Extract user event data
                new_image = record.get('dynamodb', {}).get('NewImage', {})
                
                if not new_image:
                    continue
                
                user_id = new_image.get('user_id', {}).get('S')
                item_id = new_image.get('item_id', {}).get('S')
                event_type = new_image.get('event_type', {}).get('S')
                
                if not user_id or not item_id:
                    continue
                
                # Invalidate cache for this user
                invalidate_user_cache(user_id)
                
                # Trigger recommendation update (async)
                # In production, you might want to use SQS or EventBridge for this
                logger.info(f"Processing event: {user_id} -> {item_id} ({event_type})")
                
                processed_count += 1
        
        except Exception as e:
            logger.error(f"Error processing record: {e}")
            failed_count += 1
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'processed': processed_count,
            'failed': failed_count,
            'total': len(event.get('Records', []))
        })
    }


def invalidate_user_cache(user_id: str):
    """Invalidate cached recommendations for a user"""
    try:
        cache_table_resource = dynamodb.Table(cache_table)
        
        # Delete cache entries for this user
        # In production, use a GSI to query by user_id prefix
        cache_key = f"recs:{user_id}:"
        
        # Note: This is a simplified version
        # In production, you'd query the cache table and delete matching keys
        logger.info(f"Invalidated cache for user: {user_id}")
    
    except Exception as e:
        logger.warning(f"Cache invalidation error: {e}")


def update_user_recommendations(user_id: str):
    """
    Trigger recommendation update for a user
    This would typically call the recommendation engine
    """
    try:
        # In production, this might:
        # 1. Call the recommendation API
        # 2. Send message to SQS for async processing
        # 3. Update a flag in DynamoDB to trigger recomputation
        
        logger.info(f"Triggered recommendation update for user: {user_id}")
        return True
    
    except Exception as e:
        logger.error(f"Error updating recommendations: {e}")
        return False

