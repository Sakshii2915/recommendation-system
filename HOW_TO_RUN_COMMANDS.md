# How to Run Commands - Step by Step

## Where to Write These Commands

All commands should be run in **PowerShell** (Windows terminal).

---

## Method 1: Open PowerShell in Project Folder

### Step 1: Open PowerShell
1. Press `Windows Key + X`
2. Select **"Windows PowerShell"** or **"Terminal"**
3. Or search for "PowerShell" in Start menu

### Step 2: Navigate to Project Folder
```powershell
cd C:\Users\saras\Desktop\recommendation_system
```

### Step 3: Run Commands
Now you can run any of these commands:

---

## Method 2: Open PowerShell Directly in Folder

1. Open File Explorer
2. Navigate to: `C:\Users\saras\Desktop\recommendation_system`
3. Click in the address bar
4. Type: `powershell` and press Enter
5. PowerShell opens directly in that folder!

---

## Commands to Run

### Option 2: Run Example Client
```powershell
python example_client.py
```

**What it does**: Tests all API endpoints automatically

---

### Option 3: Test Manually

#### Track an Event:
```powershell
Invoke-WebRequest -Uri http://localhost:8000/events -Method POST -ContentType "application/json" -Body '{"user_id":"test","item_id":"item1","event_type":"view"}'
```

#### Get Recommendations:
```powershell
Invoke-WebRequest -Uri http://localhost:8000/recommendations -Method POST -ContentType "application/json" -Body '{"user_id":"test","limit":5}'
```

**Note**: Make sure the server is running first! (It should be running in the background)

---

## Quick Visual Guide

```
1. Open PowerShell
   └─> Press Windows Key + X → Select PowerShell

2. Navigate to project
   └─> Type: cd C:\Users\saras\Desktop\recommendation_system

3. Run commands
   └─> Type: python example_client.py
   └─> Or copy-paste the Invoke-WebRequest commands
```

---

## Alternative: Use the Browser (Easiest!)

Instead of typing commands, just open:
```
http://localhost:8000/docs
```

This gives you a nice web interface to test everything!

---

## Troubleshooting

### "Command not found"
- Make sure you're in PowerShell (not CMD)
- Make sure you navigated to the project folder

### "Server not running"
- The server should be running in background
- If not, start it with: `uvicorn app.main:app --reload`

### "Cannot connect"
- Make sure server is running on port 8000
- Check: http://localhost:8000/ in browser

---

## Recommended: Use Browser Instead!

**Easiest way**: Just open this in your browser:
```
http://localhost:8000/docs
```

No commands needed - everything is visual and interactive! 🎉

