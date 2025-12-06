# Quick Start Guide

Get up and running with the recommendation system in 5 minutes!

## Prerequisites Check

```bash
# Check Python version (need 3.11+)
python3 --version

# Check AWS CLI
aws --version

# Check SAM CLI
sam --version
```

## Step 1: Install Dependencies

```bash
cd recommendation_system
pip install -r requirements.txt
```

## Step 2: Configure AWS

```bash
# Configure AWS credentials
aws configure

# Set your region
export AWS_REGION=us-east-1
```

## Step 3: Deploy Infrastructure

```bash
# Build and deploy
sam build
sam deploy --guided

# Or use the deployment script
chmod +x deploy.sh
./deploy.sh
```

This creates:
- ✅ DynamoDB tables
- ✅ Lambda function
- ✅ CloudWatch dashboard
- ✅ IAM roles

## Step 4: Run FastAPI Locally

```bash
# Set environment variables
export EVENTS_TABLE_NAME=UserEvents
export RECOMMENDATIONS_TABLE_NAME=UserRecommendations
export CACHE_TABLE_NAME=RecommendationCache
export AWS_REGION=us-east-1

# Run the server
uvicorn app.main:app --reload

# Or use the run script
chmod +x run_local.sh
./run_local.sh
```

Server will start at: `http://localhost:8000`

## Step 5: Test the API

### Option A: Use the example client

```bash
python example_client.py
```

### Option B: Use curl

```bash
# Health check
curl http://localhost:8000/

# Track an event
curl -X POST http://localhost:8000/events \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "item_id": "item456",
    "event_type": "view"
  }'

# Get recommendations
curl -X POST http://localhost:8000/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "limit": 10
  }'
```

### Option C: Use the interactive docs

Open in browser: `http://localhost:8000/docs`

## Step 6: Seed Sample Data (Optional)

```bash
python scripts/seed_data.py
```

This creates 1000 sample events for testing.

## Step 7: Monitor Performance

1. Open CloudWatch Dashboard:
   ```
   https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=RecommendationSystemDashboard
   ```

2. Check API metrics:
   ```bash
   curl http://localhost:8000/metrics
   ```

## Troubleshooting

### Issue: "Table does not exist"
**Solution**: Make sure you've deployed the SAM template first.

### Issue: "Access Denied"
**Solution**: Check your AWS credentials and IAM permissions.

### Issue: "Connection timeout"
**Solution**: Verify your AWS region matches the deployment region.

### Issue: "Import errors"
**Solution**: Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## Next Steps

1. ✅ Read the [README.md](README.md) for detailed documentation
2. ✅ Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
3. ✅ Review the code in `app/` directory
4. ✅ Customize event types and weights
5. ✅ Deploy to production (ECS/Lambda/EC2)

## Production Deployment

For production, consider:

1. **Deploy FastAPI to ECS Fargate**
   - Use the provided Dockerfile
   - Set up Application Load Balancer
   - Configure auto-scaling

2. **Enable DAX**
   - Create DAX cluster
   - Update environment variable: `DAX_ENDPOINT`

3. **Set up CI/CD**
   - GitHub Actions / GitLab CI
   - Automated testing
   - Blue-green deployments

4. **Monitoring & Alerts**
   - CloudWatch alarms
   - SNS notifications
   - Error tracking (Sentry)

## Support

- 📖 Full documentation: [README.md](README.md)
- 🏗️ Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- 🐛 Issues: Open a GitHub issue

Happy coding! 🚀

