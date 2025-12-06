# 🚀 Run Without AWS Setup!

Good news! I've created a **local mode** that works without AWS. You can test everything right now!

## Quick Start (No AWS Needed!)

### Step 1: Start the Server
```powershell
cd C:\Users\saras\Desktop\recommendation_system
uvicorn app.main:app --reload
```

### Step 2: Test It!
Open your browser: **http://localhost:8000/docs**

Or run the example client:
```powershell
python example_client.py
```

---

## What's Different?

- ✅ **No AWS setup required** - Uses local file storage
- ✅ **All features work** - Events, recommendations, everything!
- ✅ **Data saved locally** - In `local_data/` folder
- ✅ **Perfect for testing** - Same API, no cloud needed

---

## Switch to AWS Later

When you're ready to use AWS:

1. Set in `.env` file:
   ```
   USE_LOCAL_STORAGE=false
   ```

2. Configure AWS:
   ```powershell
   aws configure
   ```

3. Deploy infrastructure:
   ```powershell
   sam build
   sam deploy --guided
   ```

---

## Try It Now!

Just run:
```powershell
uvicorn app.main:app --reload
```

Then open: http://localhost:8000/docs

**That's it!** No AWS setup needed! 🎉

