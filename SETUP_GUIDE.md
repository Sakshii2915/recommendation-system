# Step-by-Step Setup Guide

Follow these steps to get your recommendation system up and running.

## Prerequisites Check

### Step 1: Check Python Installation
```bash
c
```
**Expected**: Python 3.11 or higher

**If not installed**: Download from https://www.python.org/downloads/

---

### Step 2: Check AWS CLI Installation
```bash
aws --version
```
**Expected**: AWS CLI version 2.x

**If not installed**: 
- Download from: https://aws.amazon.com/cli/
- Or install via: `pip install awscli`

---

### Step 3: Configure AWS Credentials
```bash
aws configure
```
Enter:
- **AWS Access Key ID**: (Your access key)
- **AWS Secret Access Key**: (Your secret key)
- **Default region**: `us-east-1` (or your preferred region)
- **Default output format**: `json`

**If you don't have AWS credentials**: 
- Go to AWS Console → IAM → Users → Your User → Security Credentials
- Create Access Key

---

### Step 4: Install AWS SAM CLI (Optional - for deployment)
```bash
sam --version
```
**If not installed**: 
- Windows: Download installer from https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html
- Or use: `pip install aws-sam-cli`

---

## Local Setup

### Step 5: Navigate to Project Directory
```bash
cd C:\Users\saras\Desktop\recommendation_system
```

---

### Step 6: Create Virtual Environment (Recommended)
```bash
python -m venv venv
```

**Activate virtual environment:**
```bash
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows Command Prompt
venv\Scripts\activate.bat
```

You should see `(venv)` in your prompt.

---

### Step 7: Install Dependencies
```bash
pip install -r requirements.txt
```

This will install:
- FastAPI
- Uvicorn
- Boto3
- NumPy
- And other dependencies

**Wait for installation to complete** (may take 2-3 minutes)

---

### Step 8: Set Environment Variables

Create a `.env` file in the project root:

**Option A: Create manually**
1. Create a new file named `.env` in `C:\Users\saras\Desktop\recommendation_system\`
2. Add these lines:
```
AWS_REGION=us-east-1
EVENTS_TABLE_NAME=UserEvents
RECOMMENDATIONS_TABLE_NAME=UserRecommendations
CACHE_TABLE_NAME=RecommendationCache
CACHE_SIZE=10000
```

**Option B: Use PowerShell**
```powershell
@"
AWS_REGION=us-east-1
EVENTS_TABLE_NAME=UserEvents
RECOMMENDATIONS_TABLE_NAME=UserRecommendations
CACHE_TABLE_NAME=RecommendationCache
CACHE_SIZE=10000
"@ | Out-File -FilePath .env -Encoding utf8
```

---

## Deploy AWS Infrastructure (Required Before Running)

### Step 9: Deploy DynamoDB Tables and Lambda

**Option A: Using AWS SAM (Recommended)**
```bash
# Build the application
sam build

# Deploy (first time - guided)
sam deploy --guided
```

When prompted:
- **Stack Name**: `recommendation-system` (or press Enter)
- **AWS Region**: `us-east-1` (or your region)
- **Confirm changes**: `Y`
- **Allow SAM CLI IAM role creation**: `Y`
- **Disable rollback**: `N`
- **Save arguments to configuration file**: `Y`

**Wait for deployment** (takes 2-5 minutes)

**Option B: Using AWS Console (Manual)**
1. Go to AWS Console → DynamoDB
2. Create tables manually using the schema in `template.yaml`
3. Enable streams on UserEvents table

---

### Step 10: Verify Deployment
```bash
aws dynamodb list-tables
```

You should see:
- `UserEvents`
- `UserRecommendations`
- `RecommendationCache`

---

## Run the Application Locally

### Step 11: Start the FastAPI Server

**Option A: Using Uvicorn directly**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Option B: Using the run script**
```bash
# Make script executable (if needed)
chmod +x run_local.sh

# Run (Linux/Mac)
./run_local.sh

# Or on Windows PowerShell
.\run_local.sh
```

**You should see:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

### Step 12: Test the API

**Open a new terminal/PowerShell window** (keep the server running)

**Option A: Use the example client**
```bash
cd C:\Users\saras\Desktop\recommendation_system
python example_client.py
```

**Option B: Use curl**
```bash
# Health check
curl http://localhost:8000/

# Track an event
curl -X POST http://localhost:8000/events -H "Content-Type: application/json" -d "{\"user_id\":\"user123\",\"item_id\":\"item456\",\"event_type\":\"view\"}"

# Get recommendations
curl -X POST http://localhost:8000/recommendations -H "Content-Type: application/json" -d "{\"user_id\":\"user123\",\"limit\":10}"
```

**Option C: Use the interactive docs**
1. Open browser: http://localhost:8000/docs
2. Try the endpoints interactively

---

## Seed Sample Data (Optional)

### Step 13: Add Sample Events
```bash
python scripts/seed_data.py
```

This creates 1000 sample events for testing.

---

## Verify Everything Works

### Step 14: Check Health
```bash
curl http://localhost:8000/
```

**Expected response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-12-06T...",
  "dynamodb_status": "connected",
  "cache_status": "active"
}
```

### Step 15: Test Full Flow
```bash
# 1. Track some events
curl -X POST http://localhost:8000/events -H "Content-Type: application/json" -d "{\"user_id\":\"test_user\",\"item_id\":\"item1\",\"event_type\":\"view\"}"
curl -X POST http://localhost:8000/events -H "Content-Type: application/json" -d "{\"user_id\":\"test_user\",\"item_id\":\"item2\",\"event_type\":\"click\"}"
curl -X POST http://localhost:8000/events -H "Content-Type: application/json" -d "{\"user_id\":\"test_user\",\"item_id\":\"item3\",\"event_type\":\"purchase\"}"

# 2. Get recommendations
curl -X POST http://localhost:8000/recommendations -H "Content-Type: application/json" -d "{\"user_id\":\"test_user\",\"limit\":5}"

# 3. Check user history
curl http://localhost:8000/users/test_user/history
```

---

## Troubleshooting

### Problem: "Table does not exist"
**Solution**: Make sure you deployed the AWS infrastructure (Step 9)

### Problem: "Access Denied" or "Credentials not found"
**Solution**: Run `aws configure` again (Step 3)

### Problem: "Module not found"
**Solution**: 
```bash
pip install -r requirements.txt
```

### Problem: Port 8000 already in use
**Solution**: 
```bash
# Use a different port
uvicorn app.main:app --reload --port 8001
```

### Problem: "Connection timeout" to DynamoDB
**Solution**: 
- Check your AWS region matches
- Verify AWS credentials
- Check internet connection

---

## Next Steps

✅ **You're running!** Now you can:

1. **Monitor Performance**: 
   - CloudWatch Dashboard: https://console.aws.amazon.com/cloudwatch/
   - API Metrics: `curl http://localhost:8000/metrics`

2. **Read Documentation**:
   - Full docs: `README.md`
   - Architecture: `ARCHITECTURE.md`
   - Quick start: `QUICKSTART.md`

3. **Deploy to Production**:
   - See `README.md` for deployment options (ECS, Lambda, EC2)

4. **Customize**:
   - Modify event weights in `app/recommendation_engine.py`
   - Adjust cache settings in `app/cache_manager.py`
   - Add new endpoints in `app/main.py`

---

## Quick Command Reference

```bash
# Start server
uvicorn app.main:app --reload

# Run tests
pytest tests/

# Format code
black app/

# Deploy to AWS
sam build && sam deploy

# Seed data
python scripts/seed_data.py
```

---

**Need help?** Check the README.md or open an issue on GitHub!

