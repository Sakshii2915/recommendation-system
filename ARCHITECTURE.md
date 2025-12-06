# Architecture Documentation

## System Overview

This real-time recommendation system is designed to handle high-volume user activity and generate personalized recommendations with sub-100ms response times. The architecture follows a serverless, event-driven pattern optimized for scalability and performance.

## Architecture Diagram

```
┌─────────────┐
│   Client    │
│  (Browser/  │
│    App)     │
└──────┬──────┘
       │
       │ HTTP/REST
       │
┌──────▼─────────────────────────────────────┐
│         FastAPI Application                 │
│  ┌──────────────────────────────────────┐  │
│  │  Event Tracking Endpoint              │  │
│  │  Recommendation Endpoint              │  │
│  │  User History Endpoint                │  │
│  └──────────────────────────────────────┘  │
└──────┬──────────────────────────────────────┘
       │
       ├─────────────────┬──────────────────┐
       │                 │                  │
┌──────▼──────┐  ┌──────▼──────┐  ┌───────▼──────┐
│  DynamoDB   │  │   Cache      │  │  CloudWatch  │
│  UserEvents │  │   Manager    │  │   Metrics    │
└──────┬──────┘  └──────────────┘  └──────────────┘
       │
       │ Stream
       │
┌──────▼─────────────────────────────────────┐
│      DynamoDB Streams                       │
└──────┬──────────────────────────────────────┘
       │
       │ Triggers
       │
┌──────▼─────────────────────────────────────┐
│   Lambda Function                           │
│   (Stream Processor)                        │
│   - Cache Invalidation                      │
│   - Recommendation Updates                  │
└─────────────────────────────────────────────┘
```

## Component Details

### 1. FastAPI Application Layer

**Purpose**: RESTful API for client interactions

**Key Features**:
- Event ingestion endpoint (`POST /events`)
- Recommendation endpoint (`POST /recommendations`)
- User history endpoint (`GET /users/{user_id}/history`)
- Health check and metrics endpoints

**Performance Optimizations**:
- Async/await for non-blocking I/O
- Request validation with Pydantic
- CORS middleware for cross-origin requests

### 2. DynamoDB Storage Layer

**Tables**:

1. **UserEvents**
   - Primary Key: `event_id` (HASH)
   - GSIs:
     - `user_id-timestamp-index`: Query events by user
     - `item_id-timestamp-index`: Query events by item
   - TTL: 1 year (automatic cleanup)
   - Stream: Enabled for real-time processing

2. **UserRecommendations**
   - Primary Key: `user_id` (HASH)
   - Stores pre-computed recommendations
   - Updated by Lambda function

3. **RecommendationCache**
   - Primary Key: `cache_key` (HASH)
   - TTL: Configurable per item
   - Used by DAX for ultra-fast reads

**Design Decisions**:
- On-demand billing for automatic scaling
- GSIs for efficient query patterns
- TTL for automatic data lifecycle management

### 3. Caching Layer

**Multi-tier Caching Strategy**:

1. **In-Memory Cache (LRU)**
   - Fastest access (< 1ms)
   - Limited by memory size
   - Eviction: Least Recently Used

2. **DynamoDB Accelerator (DAX)**
   - Sub-millisecond reads
   - Fully managed
   - Optional but recommended for production

**Cache Keys**:
- Recommendations: `recs:{user_id}:{limit}`
- Similarities: `similarity:{user_id}`
- Popular items: `popular:{limit}`

**Cache Invalidation**:
- Automatic on new user events
- TTL-based expiration
- Manual invalidation via Lambda

### 4. Lambda Stream Processor

**Trigger**: DynamoDB Streams (UserEvents table)

**Responsibilities**:
1. Process new/modified events
2. Invalidate user cache
3. Trigger recommendation updates (async)
4. Handle errors gracefully

**Configuration**:
- Batch size: 10 records
- Batch window: 5 seconds
- Timeout: 60 seconds
- Memory: 256 MB

### 5. Recommendation Engine

**Algorithm**: User-based Collaborative Filtering

**Process**:
1. Get user's interaction history
2. Find similar users (cosine similarity)
3. Weight items by similarity scores
4. Rank and return top-N items

**Event Weights**:
- Purchase: 5.0
- Add to cart: 3.0
- Like: 2.0
- Click: 1.5
- View: 1.0

**Cold Start Handling**:
- Returns popular items for new users
- Gradually improves as user history grows

### 6. CloudWatch Monitoring

**Metrics Tracked**:
- `RecommendationLatency`: Response time (avg, p95, p99)
- `RecommendationCacheHits`: Cache hit count
- `RecommendationCacheMisses`: Cache miss count
- `EventsIngested`: Event ingestion rate
- `RecommendationsGenerated`: Recommendation generation rate
- `EventIngestionLatency`: Event storage latency
- `RecommendationErrors`: Error count
- `EventIngestionErrors`: Event ingestion errors

**Dashboard**: Pre-configured with key metrics

## Data Flow

### Event Ingestion Flow

1. Client sends event to FastAPI
2. FastAPI validates and stores in DynamoDB
3. DynamoDB Stream captures the change
4. Lambda function processes the stream
5. Cache is invalidated for the user
6. CloudWatch metrics are recorded

### Recommendation Flow

1. Client requests recommendations
2. FastAPI checks cache (in-memory → DAX)
3. If cache miss:
   - Query user history from DynamoDB
   - Calculate similarities
   - Generate recommendations
   - Store in cache
4. Return recommendations to client
5. Record metrics in CloudWatch

## Scalability Considerations

### Horizontal Scaling
- FastAPI: Stateless, can run multiple instances
- Lambda: Auto-scales based on stream records
- DynamoDB: On-demand mode handles traffic spikes

### Performance Optimization
- Caching reduces database load by 80-90%
- Batch processing in Lambda
- Connection pooling for DynamoDB
- Async operations throughout

### Cost Optimization
- TTL on DynamoDB items (automatic cleanup)
- On-demand billing (pay per request)
- Cache reduces read costs
- Lambda only runs when needed

## Security

- IAM roles with least privilege
- Environment variables for configuration
- Input validation on all endpoints
- CORS configuration
- No sensitive data in logs

## Deployment Options

1. **ECS Fargate** (Recommended for production)
   - Containerized FastAPI
   - Auto-scaling
   - Load balancing

2. **Lambda + API Gateway**
   - Fully serverless
   - Use Mangum adapter
   - Lower cost for variable traffic

3. **EC2 / Elastic Beanstalk**
   - Traditional deployment
   - More control
   - Requires manual scaling

## Future Enhancements

1. **Item-based Collaborative Filtering**
   - Alternative algorithm
   - Better for sparse data

2. **Matrix Factorization**
   - More sophisticated ML approach
   - Better accuracy

3. **Real-time Feature Store**
   - Store user/item features
   - Enable more complex models

4. **A/B Testing Framework**
   - Test different algorithms
   - Measure impact

5. **Graph Database**
   - Neo4j for relationship queries
   - Better for complex recommendations

