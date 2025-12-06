# Quick Setup Checklist ✅

Follow this checklist to get your recommendation system running:

## Phase 1: Prerequisites (5 minutes)

- [ ] **Python 3.11+ installed**
  ```bash
  python --version
  ```

- [ ] **AWS CLI installed and configured**
  ```bash
  aws --version
  aws configure
  ```

- [ ] **AWS SAM CLI installed** (optional, for deployment)
  ```bash
  sam --version
  ```

---

## Phase 2: Project Setup (5 minutes)

- [ ] **Navigate to project folder**
  ```bash
  cd C:\Users\saras\Desktop\recommendation_system
  ```

- [ ] **Create virtual environment**
  ```bash
  python -m venv venv
  ```

- [ ] **Activate virtual environment**
  ```bash
  # PowerShell
  .\venv\Scripts\Activate.ps1
  
  # CMD
  venv\Scripts\activate.bat
  ```

- [ ] **Install dependencies**
  ```bash
  pip install -r requirements.txt
  ```

- [ ] **Create .env file**
  ```bash
  # Copy the content below into a new .env file
  AWS_REGION=us-east-1
  EVENTS_TABLE_NAME=UserEvents
  RECOMMENDATIONS_TABLE_NAME=UserRecommendations
  CACHE_TABLE_NAME=RecommendationCache
  CACHE_SIZE=10000
  ```

---

## Phase 3: Deploy AWS Infrastructure (10 minutes)

- [ ] **Build SAM application**
  ```bash
  sam build
  ```

- [ ] **Deploy to AWS**
  ```bash
  sam deploy --guided
  ```
  *Answer the prompts (press Enter for defaults)*

- [ ] **Verify tables created**
  ```bash
  aws dynamodb list-tables
  ```
  *Should show: UserEvents, UserRecommendations, RecommendationCache*

---

## Phase 4: Run Locally (2 minutes)

- [ ] **Start the server**
  ```bash
  uvicorn app.main:app --reload
  ```

- [ ] **Verify server is running**
  - Open browser: http://localhost:8000/docs
  - Or run: `curl http://localhost:8000/`

---

## Phase 5: Test (5 minutes)

- [ ] **Test health endpoint**
  ```bash
  curl http://localhost:8000/
  ```

- [ ] **Track a test event**
  ```bash
  curl -X POST http://localhost:8000/events -H "Content-Type: application/json" -d "{\"user_id\":\"test\",\"item_id\":\"item1\",\"event_type\":\"view\"}"
  ```

- [ ] **Get recommendations**
  ```bash
  curl -X POST http://localhost:8000/recommendations -H "Content-Type: application/json" -d "{\"user_id\":\"test\",\"limit\":5}"
  ```

- [ ] **Run example client**
  ```bash
  python example_client.py
  ```

---

## ✅ You're Done!

Your recommendation system is now running!

**Next Steps:**
- Read `SETUP_GUIDE.md` for detailed instructions
- Check `README.md` for full documentation
- Explore the API at http://localhost:8000/docs

---

## Common Issues & Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| "Table does not exist" | Run `sam deploy --guided` |
| "Module not found" | Run `pip install -r requirements.txt` |
| "Access Denied" | Run `aws configure` |
| "Port 8000 in use" | Use `--port 8001` |
| "Connection timeout" | Check AWS region and credentials |

---

**Need help?** See `SETUP_GUIDE.md` for detailed troubleshooting!

