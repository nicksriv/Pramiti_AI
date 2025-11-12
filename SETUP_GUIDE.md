# 🚀 Pramiti AI Organization - Setup Guide

## ✅ What's Working Now

1. **API Server**: Running on http://localhost:8084
2. **Frontend Dashboard**: Accessible at http://localhost:8084/openai-dashboard.html
3. **Blockchain Logging**: ✅ Active and logging all conversations
4. **5 AI Agents**: All initialized and ready

## ⚠️ What Needs Fixing

### Issue 1: OpenAI API Key

**Current Status**: Invalid API key  
**Error**: `Incorrect API key provided: your_ope************here`

**Solution**: You need to add your real OpenAI API key

---

## 🔑 How to Get and Set Your OpenAI API Key

### Step 1: Get Your OpenAI API Key

1. Go to: https://platform.openai.com/api-keys
2. Sign in (or create a free account if you don't have one)
3. Click **"Create new secret key"**
4. Copy the key (it starts with `sk-proj-` or `sk-`)
5. ⚠️ **IMPORTANT**: Save it somewhere safe - you can only see it once!

### Step 2: Add Your API Key to the Project

**Option A: Using the Setup Script (Easiest)**

Run this command in your terminal:

```bash
python3 setup_openai.py
```

Follow the prompts and paste your API key when asked.

**Option B: Manual Edit**

1. Open the file: `.env` (in your project root)
2. Find the line:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```
3. Replace `your_openai_api_key_here` with your actual key:
   ```
   OPENAI_API_KEY=sk-proj-your-actual-key-here
   ```
4. Save the file

### Step 3: Restart the Server

The server will auto-reload when you save the `.env` file. If not:

1. Press `Ctrl+C` in the terminal where the server is running
2. Restart with: `python3 api_server.py`

---

## 📊 Blockchain Logs Now Auto-Update

I've fixed the blockchain logs tab! Now it will:

✅ **Auto-refresh every 10 seconds** when viewing the Blockchain tab  
✅ **Update immediately** after each chat message  
✅ Show the **last 10 blocks** in reverse chronological order  
✅ Display full details: Block number, timestamp, sender, recipient, hash

---

## 🧪 How to Test Everything Works

### 1. Check API Status

Visit: http://localhost:8084/

You should see:
```json
{
  "message": "Pramiti AI Organization API",
  "status": "running",
  "agents": 5,
  "blockchain_enabled": true,
  "openai_enabled": true  // ← This should be true after adding your key
}
```

### 2. Test the Dashboard

1. Open: http://localhost:8084/openai-dashboard.html
2. Click on **"Agent Chat"** tab
3. Select any agent (e.g., "Incident Response Specialist")
4. Send a message like: "Help me with a server outage"
5. You should get an **AI-powered response** (not a fallback)

### 3. Verify Blockchain Logging

1. After chatting with agents, click the **"Blockchain Logs"** tab
2. You should see:
   - **Total Blocks**: Increasing with each message
   - **Recent Activity**: List of all your conversations
   - **Block Details**: Full transaction hashes and timestamps

---

## 🎯 Available Dashboards

You now have 3 working dashboards:

### 1. **OpenAI Dashboard** (Recommended)
**URL**: http://localhost:8084/openai-dashboard.html

**Features**:
- 🤖 View all 5 AI agents
- 💬 Chat with individual agents
- 🏢 See agent hierarchy
- 🤝 Pramiti Assistant (user-facing chatbot)
- 🔗 Blockchain logs viewer
- 📊 Real-time status

### 2. **Enhanced Dashboard**
**URL**: http://localhost:8084/enhanced-dashboard.html

**Features**:
- Full agent management
- Hierarchy builder
- Advanced chat interface
- Analytics

### 3. **Basic Dashboard**
**URL**: http://localhost:8084/index.html

**Features**:
- Simple overview
- KPI metrics
- Quick actions

---

## 🤖 Your 5 AI Agents

1. **Executive AI Director** (CEO)
   - Strategic decision making
   - Organizational oversight
   - Uses GPT-4o (most powerful model)

2. **ITSM Operations Manager** (Senior Manager)
   - Team coordination
   - Service delivery oversight
   - Incident management coordination

3. **Incident Response Specialist** (SME)
   - Incident classification
   - Root cause analysis
   - Service restoration

4. **Problem Analysis Expert** (SME)
   - Problem identification
   - Workaround development
   - Preventive measures

5. **Change Management Specialist** (SME)
   - Change assessment
   - Risk analysis
   - Implementation oversight

---

## 💡 Quick Commands

```bash
# Start the server
python3 api_server.py

# Setup OpenAI API key
python3 setup_openai.py

# View API documentation
# Open: http://localhost:8084/docs

# Check server status
curl http://localhost:8084/

# View blockchain status
curl http://localhost:8084/blockchain/status
```

---

## 🐛 Troubleshooting

### Dashboard shows "detail not found"
✅ **FIXED** - Added HTML route handlers to the API server

### Blockchain logs not updating
✅ **FIXED** - Added auto-refresh every 10 seconds + refresh after each message

### OpenAI returns fallback responses
❌ **FIX NEEDED** - Add your OpenAI API key (see instructions above)

### "Module not found" errors
Install dependencies:
```bash
pip install -r requirements.txt
```

---

## 📝 What Happens After You Add Your API Key

1. Server auto-reloads with new configuration
2. OpenAI status changes from "Need API Key" to "Connected"
3. Agents will generate **real AI responses** instead of fallback messages
4. Each conversation will:
   - Be processed by GPT-4o or GPT-4o-mini
   - Generate contextual, intelligent responses
   - Log to blockchain with full audit trail
   - Show up in the Blockchain Logs tab

---

## 💰 OpenAI Costs

- **Free Tier**: $5 free credits for new accounts
- **Cost**: ~$0.0001 - $0.0005 per message (very cheap!)
- **Model Used**:
  - CEO: GPT-4o (~$0.005 per request)
  - Others: GPT-4o-mini (~$0.0001 per request)

---

## 🎉 Next Steps

1. ✅ Add your OpenAI API key
2. ✅ Restart the server
3. ✅ Test the dashboard
4. ✅ Chat with agents
5. ✅ View blockchain logs
6. 🚀 Build your AI organization!

---

**Need Help?** Check the terminal logs for detailed error messages.
