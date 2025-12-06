"""
Unit tests for recommendation system
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from app.recommendation_engine import RecommendationEngine
from app.cache_manager import CacheManager
from app.dynamodb_client import DynamoDBClient


@pytest.fixture
def mock_dynamodb_client():
    """Mock DynamoDB client"""
    client = Mock(spec=DynamoDBClient)
    client.is_connected = Mock(return_value=True)
    client.get_user_events = AsyncMock(return_value=[
        {'user_id': 'user1', 'item_id': 'item1', 'event_type': 'view', 'timestamp': 1000},
        {'user_id': 'user1', 'item_id': 'item2', 'event_type': 'click', 'timestamp': 1001},
    ])
    client.get_users_by_items = AsyncMock(return_value=['user2', 'user3'])
    client.get_popular_items = AsyncMock(return_value=[
        {'item_id': 'popular1', 'popularity_score': 100},
        {'item_id': 'popular2', 'popularity_score': 95}
    ])
    return client


@pytest.fixture
def mock_cache_manager():
    """Mock cache manager"""
    cache = Mock(spec=CacheManager)
    cache.get = Mock(return_value=None)
    cache.set = Mock(return_value=True)
    cache.is_active = Mock(return_value=True)
    cache.get_stats = Mock(return_value={
        'hits': 10,
        'misses': 5,
        'hit_rate': 66.67
    })
    return cache


@pytest.fixture
def recommendation_engine(mock_dynamodb_client, mock_cache_manager):
    """Create recommendation engine with mocked dependencies"""
    return RecommendationEngine(mock_dynamodb_client, mock_cache_manager)


@pytest.mark.asyncio
async def test_get_recommendations(recommendation_engine):
    """Test recommendation generation"""
    recommendations = await recommendation_engine.get_recommendations(
        user_id='user1',
        limit=5
    )
    
    assert len(recommendations) > 0
    assert all('item_id' in rec for rec in recommendations)
    assert all('score' in rec for rec in recommendations)
    assert all('reason' in rec for rec in recommendations)


@pytest.mark.asyncio
async def test_cold_start(recommendation_engine, mock_dynamodb_client):
    """Test cold start scenario (no user history)"""
    mock_dynamodb_client.get_user_events = AsyncMock(return_value=[])
    
    recommendations = await recommendation_engine.get_recommendations(
        user_id='new_user',
        limit=5
    )
    
    assert len(recommendations) == 5
    assert all(rec['reason'] == 'Popular item' for rec in recommendations)


def test_event_weight(recommendation_engine):
    """Test event weight calculation"""
    assert recommendation_engine._event_weight('purchase') == 5.0
    assert recommendation_engine._event_weight('view') == 1.0
    assert recommendation_engine._event_weight('unknown') == 1.0


def test_cosine_similarity(recommendation_engine):
    """Test cosine similarity calculation"""
    vec1 = {'item1': 1.0, 'item2': 2.0, 'item3': 3.0}
    vec2 = {'item1': 1.0, 'item2': 2.0, 'item3': 3.0}
    
    similarity = recommendation_engine._cosine_similarity(vec1, vec2)
    assert similarity == pytest.approx(1.0, 0.01)
    
    vec3 = {'item4': 1.0, 'item5': 2.0}
    similarity = recommendation_engine._cosine_similarity(vec1, vec3)
    assert similarity == 0.0


def test_cache_manager():
    """Test cache manager operations"""
    from app.cache_manager import CacheManager
    
    cache = CacheManager()
    
    # Test set and get
    cache.set('test_key', {'data': 'value'}, ttl=60)
    value = cache.get('test_key')
    
    assert value is not None
    assert value['data'] == 'value'
    
    # Test stats
    stats = cache.get_stats()
    assert 'hits' in stats
    assert 'misses' in stats
    assert 'hit_rate' in stats


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

