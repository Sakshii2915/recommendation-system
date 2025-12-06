"""
FastAPI application for real-time recommendation system
Handles user activity tracking and personalized recommendations
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import boto3
import os
import time
import logging
from datetime import datetime
import json

from app.recommendation_engine import RecommendationEngine
from app.cache_manager import CacheManager
from app.dynamodb_client import DynamoDBClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Real-Time Recommendation System",
    description="High-performance recommendation API with sub-100ms response times",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
dynamodb_client = DynamoDBClient()
cache_manager = CacheManager()
recommendation_engine = RecommendationEngine(dynamodb_client, cache_manager)

# CloudWatch client for metrics
cloudwatch = boto3.client('cloudwatch', region_name=os.getenv('AWS_REGION', 'us-east-1'))


# Request/Response Models
class UserEvent(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
    item_id: str = Field(..., description="Item identifier (product, content, etc.)")
    event_type: str = Field(..., description="Event type: view, click, purchase, like, etc.")
    timestamp: Optional[float] = Field(default=None, description="Event timestamp (Unix epoch)")
    metadata: Optional[dict] = Field(default={}, description="Additional event metadata")


class RecommendationRequest(BaseModel):
    user_id: str = Field(..., description="User ID to get recommendations for")
    limit: int = Field(default=10, ge=1, le=100, description="Number of recommendations to return")
    context: Optional[dict] = Field(default={}, description="Contextual information for recommendations")


class RecommendationResponse(BaseModel):
    user_id: str
    recommendations: List[dict]
    generated_at: str
    response_time_ms: float
    cache_hit: bool


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    dynamodb_status: str
    cache_status: str


def record_metric(metric_name: str, value: float, unit: str = "Count"):
    """Record custom CloudWatch metric"""
    try:
        cloudwatch.put_metric_data(
            Namespace='RecommendationSystem',
            MetricData=[
                {
                    'MetricName': metric_name,
                    'Value': value,
                    'Unit': unit,
                    'Timestamp': datetime.utcnow()
                }
            ]
        )
    except Exception as e:
        logger.warning(f"Failed to record metric {metric_name}: {e}")


@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "dynamodb_status": "connected" if dynamodb_client.is_connected() else "disconnected",
        "cache_status": "active" if cache_manager.is_active() else "inactive"
    }


@app.post("/events", status_code=201)
async def track_event(event: UserEvent):
    """
    Track user activity events
    Stores events in DynamoDB and triggers stream processing
    """
    start_time = time.time()
    
    try:
        # Set timestamp if not provided
        if event.timestamp is None:
            event.timestamp = time.time()
        
        # Store event in DynamoDB
        success = await dynamodb_client.put_user_event(
            user_id=event.user_id,
            item_id=event.item_id,
            event_type=event.event_type,
            timestamp=event.timestamp,
            metadata=event.metadata
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to store event")
        
        # Record metrics
        latency = (time.time() - start_time) * 1000
        record_metric("EventIngestionLatency", latency, "Milliseconds")
        record_metric("EventsIngested", 1)
        
        logger.info(f"Event tracked: {event.user_id} -> {event.item_id} ({event.event_type})")
        
        return {
            "status": "success",
            "message": "Event tracked successfully",
            "event_id": f"{event.user_id}_{event.item_id}_{int(event.timestamp)}"
        }
    
    except Exception as e:
        logger.error(f"Error tracking event: {e}")
        record_metric("EventIngestionErrors", 1)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """
    Get personalized recommendations for a user
    Uses collaborative filtering with caching for sub-100ms response times
    """
    start_time = time.time()
    cache_hit = False
    
    try:
        # Check cache first
        cache_key = f"recs:{request.user_id}:{request.limit}"
        cached_result = cache_manager.get(cache_key)
        
        if cached_result:
            cache_hit = True
            response_time = (time.time() - start_time) * 1000
            record_metric("RecommendationCacheHits", 1)
            record_metric("RecommendationLatency", response_time, "Milliseconds")
            
            return RecommendationResponse(
                user_id=request.user_id,
                recommendations=cached_result,
                generated_at=datetime.utcnow().isoformat(),
                response_time_ms=response_time,
                cache_hit=True
            )
        
        # Generate recommendations
        recommendations = await recommendation_engine.get_recommendations(
            user_id=request.user_id,
            limit=request.limit,
            context=request.context
        )
        
        # Cache the results
        cache_manager.set(cache_key, recommendations, ttl=300)  # 5 minutes TTL
        
        response_time = (time.time() - start_time) * 1000
        record_metric("RecommendationCacheMisses", 1)
        record_metric("RecommendationLatency", response_time, "Milliseconds")
        record_metric("RecommendationsGenerated", 1)
        
        logger.info(f"Generated {len(recommendations)} recommendations for user {request.user_id} in {response_time:.2f}ms")
        
        return RecommendationResponse(
            user_id=request.user_id,
            recommendations=recommendations,
            generated_at=datetime.utcnow().isoformat(),
            response_time_ms=response_time,
            cache_hit=False
        )
    
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        record_metric("RecommendationErrors", 1)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/users/{user_id}/history")
async def get_user_history(user_id: str, limit: int = 50):
    """Get user activity history"""
    try:
        events = await dynamodb_client.get_user_events(user_id, limit)
        return {
            "user_id": user_id,
            "events": events,
            "count": len(events)
        }
    except Exception as e:
        logger.error(f"Error fetching user history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def get_metrics():
    """Get system metrics"""
    try:
        cache_stats = cache_manager.get_stats()
        return {
            "cache": cache_stats,
            "dynamodb": {
                "connected": dynamodb_client.is_connected()
            }
        }
    except Exception as e:
        logger.error(f"Error fetching metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

