# Real-Time Recommendation System

A production-ready, scalable real-time recommendation system built with FastAPI, AWS Lambda, DynamoDB, and collaborative filtering. This system is designed to handle high-volume user activity and generate personalized recommendations with sub-100ms response times.

## 🚀 Live Demo

**🌐 Live API**: [https://recommendation-system-bl8w.onrender.com/docs](https://recommendation-system-bl8w.onrender.com/docs)

**📚 Interactive API Documentation**: [https://recommendation-system-bl8w.onrender.com/docs](https://recommendation-system-bl8w.onrender.com/docs)

**✅ Health Check**: [https://recommendation-system-bl8w.onrender.com/](https://recommendation-system-bl8w.onrender.com/)

Try it out:
- View interactive API docs with Swagger UI
- Test endpoints directly from the browser
- Track events and get recommendations

## 🏗️ Architecture

### Components

1. **FastAPI Application**: RESTful API for tracking user events and serving recommendations
2. **AWS Lambda**: Serverless functions for processing DynamoDB streams in real-time
3. **DynamoDB**: Low-latency NoSQL database for storing user events and recommendations
4. **DynamoDB Streams**: Triggers Lambda functions when new events arrive
5. **Caching Layer**: In-memory caching + DynamoDB Accelerator (DAX) for ultra-fast access
6. **Collaborative Filtering**: User-based similarity algorithm for personalized recommendations
7. **CloudWatch**: Monitoring and metrics dashboard

### Key Features

- ⚡ **Sub-100ms response times** with intelligent caching
- 📈 **Auto-scaling** with serverless architecture
- 🔄 **Real-time updates** via DynamoDB Streams
- 🎯 **Personalized recommendations** using collaborative filtering
- 📊 **Comprehensive monitoring** with CloudWatch dashboards
- 🚀 **Production-ready** with error handling and fallbacks

## 📋 Prerequisites

- Python 3.11+
- AWS CLI configured with appropriate credentials
- AWS SAM CLI installed ([Installation Guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html))
- Docker (for local testing)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd recommendation_system
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file:

```bash
AWS_REGION=us-east-1
EVENTS_TABLE_NAME=UserEvents
RECOMMENDATIONS_TABLE_NAME=UserRecommendations
CACHE_TABLE_NAME=RecommendationCache
DAX_ENDPOINT=  # Optional: Add if using DAX cluster
CACHE_SIZE=10000
```

### 3. Deploy AWS Infrastructure

```bash
# Build and deploy with SAM
sam build
sam deploy --guided

# Or deploy without guided mode
sam deploy --stack-name recommendation-system \
           --s3-bucket your-sam-bucket \
           --capabilities CAPABILITY_IAM \
           --region us-east-1
```

This will create:
- DynamoDB tables (UserEvents, UserRecommendations, RecommendationCache)
- Lambda function for stream processing
- CloudWatch dashboard
- IAM roles and policies

### 4. Run FastAPI Locally

```bash
# Using uvicorn directly
uvicorn app.main:app --reload --port 8000

# Or using Docker
docker build -t recommendation-api .
docker run -p 8000:8000 \
  -e AWS_REGION=us-east-1 \
  -e EVENTS_TABLE_NAME=UserEvents \
  -e RECOMMENDATIONS_TABLE_NAME=UserRecommendations \
  -e CACHE_TABLE_NAME=RecommendationCache \
  recommendation-api
```

### 5. Deploy FastAPI to Production

For production deployment, you have several options:

#### Option A: AWS ECS Fargate (Recommended)

```bash
# Build and push Docker image to ECR
aws ecr create-repository --repository-name recommendation-api
docker tag recommendation-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/recommendation-api:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/recommendation-api:latest

# Deploy to ECS (create task definition and service)
```

#### Option B: AWS Lambda with Function URL

Modify the SAM template to include a Lambda function for the FastAPI app using Mangum adapter.

#### Option C: EC2 or Elastic Beanstalk

Traditional deployment options work as well.

## 📡 API Endpoints

### Health Check
```bash
GET /
```

### Track User Event
```bash
POST /events
Content-Type: application/json

{
  "user_id": "user123",
  "item_id": "item456",
  "event_type": "view",
  "timestamp": 1699123456.789,
  "metadata": {
    "category": "electronics",
    "price": 99.99
  }
}
```

### Get Recommendations
```bash
POST /recommendations
Content-Type: application/json

{
  "user_id": "user123",
  "limit": 10,
  "context": {
    "category": "electronics"
  }
}
```

Response:
```json
{
  "user_id": "user123",
  "recommendations": [
    {
      "item_id": "item789",
      "score": 0.95,
      "reason": "Highly recommended based on similar users"
    }
  ],
  "generated_at": "2024-01-15T10:30:00",
  "response_time_ms": 45.2,
  "cache_hit": false
}
```

### Get User History
```bash
GET /users/{user_id}/history?limit=50
```

### Get Metrics
```bash
GET /metrics
```

## 🔧 Configuration

### Event Types and Weights

The system assigns different weights to event types:
- `purchase`: 5.0
- `add_to_cart`: 3.0
- `like`: 2.0
- `click`: 1.5
- `view`: 1.0
- `share`: 2.5
- `rating_5`: 4.0
- `rating_4`: 3.0
- etc.

### Caching Strategy

- **In-memory cache**: LRU cache with configurable size (default: 10,000 entries)
- **DAX**: Optional DynamoDB Accelerator for sub-millisecond reads
- **Cache TTL**: 5 minutes for recommendations
- **Cache invalidation**: Automatic on new user events

## 📊 Monitoring

### CloudWatch Dashboard

Access the dashboard at:
```
https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=RecommendationSystemDashboard
```

Metrics tracked:
- Recommendation latency (average, p95, p99)
- Cache hit/miss rates
- Throughput (events ingested, recommendations generated)
- Error rates

### Custom Metrics

The system publishes custom metrics to CloudWatch:
- `RecommendationLatency`: Response time in milliseconds
- `RecommendationCacheHits`: Number of cache hits
- `RecommendationCacheMisses`: Number of cache misses
- `EventsIngested`: Number of events processed
- `RecommendationsGenerated`: Number of recommendations created
- `EventIngestionLatency`: Event storage latency
- `RecommendationErrors`: Error count
- `EventIngestionErrors`: Event ingestion errors

## 🧪 Testing

### Unit Tests

```bash
pytest tests/
```

### Load Testing

```bash
# Install locust
pip install locust

# Run load test
locust -f tests/load_test.py --host=http://localhost:8000
```

### Example Usage

```python
import requests

# Track an event
response = requests.post("http://localhost:8000/events", json={
    "user_id": "user123",
    "item_id": "item456",
    "event_type": "view"
})

# Get recommendations
response = requests.post("http://localhost:8000/recommendations", json={
    "user_id": "user123",
    "limit": 10
})
print(response.json())
```

## 🔐 Security

- IAM roles with least privilege access
- Environment variables for sensitive configuration
- Input validation with Pydantic models
- CORS configuration for API access
- TTL on DynamoDB items for automatic cleanup

## 🚀 Scaling Considerations

### DynamoDB
- Uses on-demand billing mode for automatic scaling
- Global Secondary Indexes (GSIs) for efficient queries
- TTL enabled for automatic data cleanup

### Lambda
- Automatic scaling based on stream records
- Configurable batch size and window
- Dead letter queues for failed processing

### Caching
- Multi-layer caching (in-memory + DAX)
- LRU eviction policy
- Configurable cache size

## 📈 Performance Optimization

1. **Caching**: Aggressive caching reduces database load
2. **Batch Processing**: Lambda processes events in batches
3. **Indexes**: GSIs optimize query performance
4. **Connection Pooling**: Reuse DynamoDB connections
5. **Async Operations**: Non-blocking I/O where possible

## 🛠️ Development

### Project Structure

```
recommendation_system/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── recommendation_engine.py  # Collaborative filtering logic
│   ├── cache_manager.py     # Caching layer
│   └── dynamodb_client.py   # DynamoDB operations
├── lambda_functions/
│   ├── __init__.py
│   └── stream_processor.py  # DynamoDB stream handler
├── tests/
│   └── test_recommendations.py
├── template.yaml            # AWS SAM template
├── requirements.txt
├── Dockerfile
└── README.md
```

### Code Style

```bash
# Format code
black app/ lambda_functions/

# Lint code
flake8 app/ lambda_functions/
```

## 🔄 DynamoDB Stream Processing

When a new user event is stored:
1. DynamoDB Stream captures the change
2. Lambda function is triggered
3. Cache is invalidated for the user
4. Recommendation update is triggered (async)
5. New recommendations are generated and cached

## 📝 License

MIT License

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue on GitHub.

---

**Built with ❤️ for scalable, real-time recommendation systems**

